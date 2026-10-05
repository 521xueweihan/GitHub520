import unittest
from unittest.mock import patch

import common


def complete_payload():
    return [(f"192.0.2.{index + 1}", hostname)
            for index, hostname in enumerate(common.GITHUB_URLS)]


class HostsPayloadValidationTest(unittest.TestCase):
    def assert_rejected_without_writing(self, content_list):
        with patch("common.write_file") as write_file:
            with self.assertRaises(ValueError):
                common.write_hosts_content("payload", content_list)
        write_file.assert_not_called()

    def test_accepts_complete_ipv4_payload(self):
        with patch("common.write_file", return_value=False):
            result = common.write_hosts_content("payload", complete_payload())
        self.assertIn("# GitHub520 Host Start", result)

    def test_rejects_empty_payload(self):
        with patch("common.write_file") as write_file:
            with self.assertRaises(ValueError):
                common.write_hosts_content("", complete_payload())
        write_file.assert_not_called()

    def test_rejects_missing_host(self):
        self.assert_rejected_without_writing(complete_payload()[:-1])

    def test_rejects_duplicate_host(self):
        payload = complete_payload()
        payload[-1] = payload[0]
        self.assert_rejected_without_writing(payload)

    def test_rejects_dns_failure_sentinel(self):
        payload = complete_payload()
        payload[0] = ("# IP Address Not Found", common.GITHUB_URLS[0])
        self.assert_rejected_without_writing(payload)

    def test_rejects_ipv6_mapping(self):
        payload = complete_payload()
        payload[0] = ("2001:db8::1", common.GITHUB_URLS[0])
        self.assert_rejected_without_writing(payload)


if __name__ == "__main__":
    unittest.main()
