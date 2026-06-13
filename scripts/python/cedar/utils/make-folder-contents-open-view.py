#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.parse
from typing import Any, Dict, Tuple

import requests


def _host_from_url(url: str) -> str:
    return urllib.parse.urlparse(url).netloc


def _derive_env_hosts(cedar_ui_base: str) -> Tuple[str, str]:
    """
    From UI base like:
      - cedar.metadatacenter.org
      - cedar.staging.metadatacenter.org
    return (api_host, repo_host) like:
      - resource.metadatacenter.org, repo.metadatacenter.org
      - resource.staging.metadatacenter.org, repo.staging.metadatacenter.org
    """
    ui_host = _host_from_url(cedar_ui_base)
    parts = ui_host.split(".")
    if parts[0] != "cedar":
        raise ValueError(f"Unexpected UI host (expects to begin with 'cedar'): {ui_host}")
    api_parts = parts.copy()
    api_parts[0] = "resource"
    repo_parts = parts.copy()
    repo_parts[0] = "repo"
    return ".".join(api_parts), ".".join(repo_parts)


class CedarClient:
    def __init__(self, cedar_ui_base: str, api_key: str):
        api_host, repo_host = _derive_env_hosts(cedar_ui_base)
        self.api_base = f"https://{api_host}"
        self.repo_host = repo_host
        self.sess = requests.Session()
        self.sess.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"apiKey {api_key}",
        })

    def get_folder_contents(self, folder_id_iri: str, limit: int = 500, offset: int = 0) -> Dict[str, Any]:
        enc_id = urllib.parse.quote(folder_id_iri, safe="")
        url = f"{self.api_base}/folders/{enc_id}/contents?limit={limit}&offset={offset}"
        r = self.sess.get(url, timeout=60)
        r.raise_for_status()
        return r.json()

    def make_artifact_open(self, artifact_id_iri: str) -> requests.Response:
        """
        POST /command/make-artifact-open with body {"@id": "<artifact IRI>"}.
        """
        url = f"{self.api_base}/command/make-artifact-open"
        payload = {"@id": artifact_id_iri}
        r = self.sess.post(url, data=json.dumps(payload), timeout=60)
        return r


def infer_artifact_id_from_hit(hit: Dict[str, Any]) -> str:
    rid = hit.get("@id") or hit.get("iri") or hit.get("id")
    if not rid:
        raise ValueError("Cannot find @id in folder contents item.")
    path = urllib.parse.urlparse(rid).path or ""
    # Skip folders explicitly
    if "/folders/" in path:
        raise RuntimeError("Item is a folder; skipping.")
    return rid


def main():
    ap = argparse.ArgumentParser(description="Set openView=true for all top-level artifacts in a CEDAR folder.")
    ap.add_argument("--wet-run", action="store_true", help="Actually POST to make artifacts open. Default is dry-run.")
    ap.add_argument("--sleep-ms", type=int, default=200, help="Sleep between POSTs in wet-run.")
    ap.add_argument("--page-size", type=int, default=500, help="Max items to fetch from folder contents.")
    args = ap.parse_args()

    server_url = os.environ.get("CEDARSCRIPT_SERVER_URL")
    api_key = os.environ.get("CEDARSCRIPT_API_KEY")
    folder_id = os.environ.get("CEDARSCRIPT_FOLDER_ID")

    for name, val in [
        ("CEDARSCRIPT_SERVER_URL", server_url),
        ("CEDARSCRIPT_API_KEY", api_key),
        ("CEDARSCRIPT_FOLDER_ID", folder_id),
    ]:
        if not val:
            print(f"ERROR: missing env var {name}", file=sys.stderr)
            sys.exit(2)

    client = CedarClient(server_url, api_key)

    # Fetch top-level contents (single page; no recursion)
    try:
        contents = client.get_folder_contents(folder_id, limit=args.page_size, offset=0)
    except requests.HTTPError as e:
        print(f"ERROR listing folder contents: {e}\nResponse: {getattr(e.response, 'text', '')}", file=sys.stderr)
        sys.exit(3)

    resources = contents.get("resources") or contents.get("items") or []
    if not isinstance(resources, list):
        print("ERROR: Unexpected folder contents shape; no 'resources' list.", file=sys.stderr)
        sys.exit(3)

    print(f"Found {len(resources)} items (top-level only).")

    successes = 0
    failures = 0
    skipped = 0

    for hit in resources:
        try:
            rid = infer_artifact_id_from_hit(hit)
        except RuntimeError as e:
            print(f"- SKIP: {e}")
            skipped += 1
            continue
        except Exception as e:
            print(f"- ERROR: could not parse item: {e}")
            failures += 1
            continue

        print(f"- artifact: {rid}")
        if args.wet_run:
            try:
                resp = client.make_artifact_open(rid)
                if 200 <= resp.status_code < 300:
                    print(f"  OK: openView set ({resp.status_code})")
                    successes += 1
                else:
                    print(f"  ERROR: {resp.status_code}\n  Body: {resp.text[:1000]}")
                    failures += 1
                time.sleep(args.sleep_ms / 1000.0)
            except requests.HTTPError as e:
                print(f"  ERROR: exception during POST: {e}\n  Response: {getattr(e.response, 'text', '')}")
                failures += 1
        else:
            print("  DRY-RUN: would POST /command/make-artifact-open with this @id.")
            successes += 1

    print(f"\nDone. Successes={successes}, Failures={failures}, Skipped={skipped}. WetRun={args.wet_run}")


if __name__ == "__main__":
    main()
