import ast
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LIVE_HTTP_MODULES = [
    REPOSITORY_ROOT / "scripts/python/cedar/utils/getter.py",
    REPOSITORY_ROOT / "scripts/python/cedar/utils/storer.py",
    REPOSITORY_ROOT / "scripts/python/cedar/utils/updater.py",
    REPOSITORY_ROOT / "scripts/python/cedar/utils/remover.py",
    REPOSITORY_ROOT / "scripts/python/cedar/utils/searcher.py",
    REPOSITORY_ROOT / "scripts/python/cedar/utils/validator.py",
    REPOSITORY_ROOT / "scripts/python/cedar/tools/cedar-instance-delete.py",
]


class LiveHttpTlsVerificationTest(unittest.TestCase):

    def test_live_http_calls_do_not_disable_tls_verification_or_warnings(self):
        for module_path in LIVE_HTTP_MODULES:
            with self.subTest(module=module_path.name):
                tree = ast.parse(module_path.read_text(), filename=str(module_path))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    self.assertFalse(
                        self._is_disable_warnings_call(node),
                        f"{module_path} suppresses TLS warnings",
                    )
                    for keyword in node.keywords:
                        self.assertFalse(
                            keyword.arg == "verify"
                            and isinstance(keyword.value, ast.Constant)
                            and keyword.value.value is False,
                            f"{module_path} disables TLS verification",
                        )

    @staticmethod
    def _is_disable_warnings_call(node):
        return isinstance(node.func, ast.Attribute) and node.func.attr == "disable_warnings"


if __name__ == "__main__":
    unittest.main()
