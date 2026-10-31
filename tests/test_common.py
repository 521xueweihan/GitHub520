import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import common


class WriteFileTests(unittest.TestCase):
    def test_unchanged_hosts_do_not_rewrite_any_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hosts_content = "# GitHub520 Host Start\n1.2.3.4 github.com\n\n# Update time: old\n"
            hosts = "before hosts"
            (root / "README.md").write_text(
                "prefix```bash\n"
                f"{hosts_content.split('# Update time:')[0].strip()}\n"
                "# Update time: previous\n```suffix",
                encoding="utf-8",
            )
            (root / "README_template.md").write_text(
                "{hosts_str}|{update_time}", encoding="utf-8"
            )
            (root / "hosts").write_text(hosts, encoding="utf-8")

            with patch.object(common, "__file__", str(root / "common.py")):
                changed = common.write_file(hosts_content, "new")

            self.assertFalse(changed)
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"),
                             "prefix```bash\n"
                             f"{hosts_content.split('# Update time:')[0].strip()}\n"
                             "# Update time: previous\n```suffix")
            self.assertEqual((root / "hosts").read_text(encoding="utf-8"), hosts)

    def test_changed_hosts_update_all_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "prefix```bash\nold host\n```suffix", encoding="utf-8"
            )
            (root / "README_template.md").write_text(
                "{hosts_str}|{update_time}", encoding="utf-8"
            )

            hosts_content = "new host\n# Update time: now\n"
            with patch.object(common, "__file__", str(root / "common.py")):
                changed = common.write_file(hosts_content, "now")

            self.assertTrue(changed)
            self.assertEqual((root / "hosts").read_text(encoding="utf-8"), hosts_content)
            self.assertIn(hosts_content, (root / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
