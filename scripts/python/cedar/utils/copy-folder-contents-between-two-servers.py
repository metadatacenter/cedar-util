#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.parse
from typing import Any, Dict, Iterable, Tuple

import requests

# ---------- Helpers: derive environment-specific bases from UI base ----------
def _host_from_url(url: str) -> str:
    return urllib.parse.urlparse(url).netloc

def _derive_env_hosts(cedar_ui_base: str) -> Tuple[str, str]:
    """
    Given the UI base host like:
      - cedar.metadatacenter.org
      - cedar.staging.metadatacenter.org
    return (api_host, repo_host) like:
      - resource.metadatacenter.org, repo.metadatacenter.org
      - resource.staging.metadatacenter.org, repo.staging.metadatacenter.org
    """
    ui_host = _host_from_url(cedar_ui_base)
    parts = ui_host.split(".")
    # replace leading 'cedar' with 'resource' or 'repo' while preserving any env prefix
    if parts[0] != "cedar":
        raise ValueError(f"Unexpected UI host (expects to begin with 'cedar'): {ui_host}")
    api_parts = parts.copy()
    api_parts[0] = "resource"
    repo_parts = parts.copy()
    repo_parts[0] = "repo"
    return ".".join(api_parts), ".".join(repo_parts)

# ---------- HTTP ----------
class CedarClient:
    def __init__(self, cedar_ui_base: str, api_key: str):
        api_host, repo_host = _derive_env_hosts(cedar_ui_base)
        self.api_base = f"https://{api_host}"
        self.repo_host = repo_host  # e.g., repo.metadatacenter.org or repo.staging.metadatacenter.org
        self.sess = requests.Session()
        self.sess.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"apiKey {api_key}",
            "Accept": "application/json",
        })

    def get_folder_contents(self, folder_id_iri: str, limit: int = 500, offset: int = 0) -> Dict[str, Any]:
        # folder_id must be URL-encoded in path (Swagger note).
        # Endpoint form: GET /folders/{folder_id}/contents
        # Reference: Insomnia issue links the exact swagger op id.
        # We'll do single page fetch (no recursion as requested).
        enc_id = urllib.parse.quote(folder_id_iri, safe="")
        url = f"{self.api_base}/folders/{enc_id}/contents?limit={limit}&offset={offset}"
        r = self.sess.get(url, timeout=60)
        r.raise_for_status()
        return r.json()

    def get_resource(self, collection: str, resource_id_iri: str) -> Dict[str, Any]:
        enc_id = urllib.parse.quote(resource_id_iri, safe="")
        url = f"{self.api_base}/{collection}/{enc_id}"
        r = self.sess.get(url, timeout=60)
        r.raise_for_status()
        return r.json()

    def create_resource_with_id(self, collection: str, payload: Dict[str, Any], target_folder_id_iri: str) -> requests.Response:
        """
        Create (or update) a resource using PUT with a specific ID.
        Matches the Java API signature:
            PUT /{collection}/{id}?folder_id={folderId}
        """
        rid = payload.get("@id")
        if not rid:
            raise ValueError("Payload missing @id for PUT create-with-id.")
        enc_id = urllib.parse.quote(rid, safe="")
        enc_folder = urllib.parse.quote(target_folder_id_iri, safe="")
        url = f"{self.api_base}/{collection}/{enc_id}?folder_id={enc_folder}"
        r = self.sess.put(url, data=json.dumps(payload), timeout=120)
        return r

# ---------- Model / mapping ----------
# Map a resource "type" to the REST collection name expected by the API.
# We inspect the item's '@type' or a summary field to categorize.
# Collections per public docs: templates | template-elements | template-instances (and also template-fields).
TYPE_TO_COLLECTION = {
    "https://schema.metadatacenter.org/core/Template": "templates",
    "https://schema.metadatacenter.org/core/Element": "template-elements",
    "https://schema.metadatacenter.org/core/Field": "template-fields",
    "https://schema.metadatacenter.org/core/TemplateInstance": "template-instances",
}

def infer_collection_from_hit(hit: Dict[str, Any]) -> Tuple[str, str]:
    """
    Try to infer collection name and id IRI from a folder contents 'hit'.
    We accept either explicit '@type' list or look at 'path' if present.
    Returns (collection, id_iri)
    """
    rid = hit.get("@id") or hit.get("iri") or hit.get("id")
    if not rid:
        raise ValueError(f"Cannot find @id in folder contents item: {hit.keys()}")

    t = hit.get("@type")
    if isinstance(t, list):
        for ty in t:
            if ty in TYPE_TO_COLLECTION:
                return TYPE_TO_COLLECTION[ty], rid

    # Heuristic fallback: look at IRI path
    p = urllib.parse.urlparse(rid).path
    if "/templates/" in p:
        return "templates", rid
    if "/template-elements/" in p:
        return "template-elements", rid
    if "/template-fields/" in p:
        return "template-fields", rid
    if "/template-instances/" in p or "/instances/" in p:
        # The canonical path segment is 'template-instances'
        return "template-instances", rid

    # If it's a folder we skip it (we only want artifacts)
    if "/folders/" in p:
        raise RuntimeError("Item is a folder; skipping per requirements.")

    raise ValueError(f"Could not infer collection for item with @id={rid}")

# ---------- IRI rewriting ----------
def rewrite_all_repo_iris(obj: Any, src_repo_host: str, dst_repo_host: str) -> Any:
    """
    Recursively walk JSON and replace any string IRIs that start with 'https://{src_repo_host}/'
    with 'https://{dst_repo_host}/'. Keeps the UUIDs and trailing paths intact.
    """
    prefix_src = f"https://{src_repo_host}/"
    prefix_dst = f"https://{dst_repo_host}/"

    if isinstance(obj, dict):
        return {k: rewrite_all_repo_iris(v, src_repo_host, dst_repo_host) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [rewrite_all_repo_iris(v, src_repo_host, dst_repo_host) for v in obj]
    elif isinstance(obj, str):
        if obj.startswith(prefix_src):
            return prefix_dst + obj[len(prefix_src):]
        # also handle rare http case
        if obj.startswith(f"http://{src_repo_host}/"):
            return prefix_dst + obj[len(f"http://{src_repo_host}/"):]
        return obj
    else:
        return obj

# ---------- main ----------
# It will read the folder contents
# Will recreate every artifact on the target server
# Does not dive into subfolders
# pass in --wet-run to actually execute the copy

# Set env vars prior to run:
# export CEDARSCRIPT_SOURCE_SERVER_URL=https://cedar.metadatacenter.org/
# export CEDARSCRIPT_TARGET_SERVER_URL=https://cedar.staging.metadatacenter.org/
# export CEDARSCRIPT_SOURCE_API_KEY=K1
# export CEDARSCRIPT_TARGET_API_KEY=K3
# export CEDARSCRIPT_SOURCE_FOLDER_ID=https://repo.metadatacenter.org/folders/UUID1
# export CEDARSCRIPT_TARGET_FOLDER_ID=https://repo.staging.metadatacenter.org/folders/UUID2

def main():
    ap = argparse.ArgumentParser(description="Copy top-level CEDAR artifacts from a source folder to a target folder, preserving UUIDs.")
    ap.add_argument("--wet-run", action="store_true", help="Actually PUT to target. Default is dry-run.")
    ap.add_argument("--sleep-ms", type=int, default=250, help="Sleep between PUTs to be polite (only in wet-run).")
    args = ap.parse_args()

    # Env vars
    src_ui = os.environ.get("CEDARSCRIPT_SOURCE_SERVER_URL")
    tgt_ui = os.environ.get("CEDARSCRIPT_TARGET_SERVER_URL")
    src_key = os.environ.get("CEDARSCRIPT_SOURCE_API_KEY")
    tgt_key = os.environ.get("CEDARSCRIPT_TARGET_API_KEY")
    src_folder = os.environ.get("CEDARSCRIPT_SOURCE_FOLDER_ID")
    tgt_folder = os.environ.get("CEDARSCRIPT_TARGET_FOLDER_ID")

    for name, val in [
        ("CEDARSCRIPT_SOURCE_SERVER_URL", src_ui),
        ("CEDARSCRIPT_TARGET_SERVER_URL", tgt_ui),
        ("CEDARSCRIPT_SOURCE_API_KEY", src_key),
        ("CEDARSCRIPT_TARGET_API_KEY", tgt_key),
        ("CEDARSCRIPT_SOURCE_FOLDER_ID", src_folder),
        ("CEDARSCRIPT_TARGET_FOLDER_ID", tgt_folder),
    ]:
        if not val:
            print(f"ERROR: missing env var {name}", file=sys.stderr)
            sys.exit(2)

    # Build clients and repo hosts
    src_api_host, src_repo_host = _derive_env_hosts(src_ui)
    tgt_api_host, tgt_repo_host = _derive_env_hosts(tgt_ui)

    src = CedarClient(src_ui, src_key)
    tgt = CedarClient(tgt_ui, tgt_key)

    # 1) List only direct contents of the folder
    try:
        contents = src.get_folder_contents(src_folder, limit=500, offset=0)
    except requests.HTTPError as e:
        print(f"ERROR listing source folder contents: {e}\nResponse: {getattr(e.response, 'text', '')}", file=sys.stderr)
        sys.exit(3)

    resources = contents.get("resources") or contents.get("items") or []
    if not isinstance(resources, list):
        print("ERROR: Unexpected folder contents shape; no 'resources' list.", file=sys.stderr)
        sys.exit(3)

    print(f"Found {len(resources)} items in source folder (top-level only).")

    # 2) Iterate, fetch, rewrite, create
    successes = 0
    failures = 0

    for hit in resources:
        try:
            collection, rid = infer_collection_from_hit(hit)
        except Exception as e:
            # Skip folders and unknowns
            print(f"- SKIP: {e}")
            continue

        # Retrieve full JSON
        try:
            body = src.get_resource(collection, rid)
        except requests.HTTPError as e:
            print(f"- ERROR fetching {rid}: {e}\n  Response: {getattr(e.response, 'text', '')}")
            failures += 1
            continue

        # Rewrite IRIs from source repo host to target repo host
        rewritten = rewrite_all_repo_iris(body, src_repo_host, tgt_repo_host)

        # Sanity: ensure @id changed host but preserved UUID/path
        src_id = body.get("@id", "")
        dst_id = rewritten.get("@id", "")
        print(f"- {collection}:")
        print(f"  src: {src_id}")
        print(f"  dst: {dst_id}")

        if not dst_id or not isinstance(dst_id, str):
            print("  ERROR: no @id in rewritten payload; skipping.")
            failures += 1
            continue

        # Prepare to PUT
        if args.wet_run:
            try:
                resp = tgt.create_resource_with_id(collection, rewritten, tgt_folder)
                if 200 <= resp.status_code < 300:
                    print(f"  OK: created on target ({resp.status_code})")
                    successes += 1
                else:
                    # Common failures: already exists (409), dependency missing (4xx), auth problems (401/403)
                    print(f"  ERROR: target PUT returned {resp.status_code}")
                    print(f"  Body: {resp.text[:1000]}")
                    failures += 1
                time.sleep(args.sleep_ms / 1000.0)
            except requests.HTTPError as e:
                print(f"  ERROR: exception during PUT: {e}\n  Response: {getattr(e.response, 'text', '')}")
                failures += 1
        else:
            print("  DRY-RUN: would PUT to target collection with preserved @id.")
            successes += 1

    print(f"\nDone. Successes={successes}, Failures={failures}. WetRun={args.wet_run}")

if __name__ == "__main__":
    main()
