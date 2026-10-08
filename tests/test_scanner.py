"""
Unit and integration tests for bulkdomainsearch core scanner.
"""

import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from bulkdomainsearch import BulkDomainScanner, DomainStatus, normalize_domain, validate_label
from bulkdomainsearch.models import DomainResult


class TestDomainValidation(unittest.TestCase):
    def test_normalize_domain(self):
        self.assertEqual(normalize_domain("agent"), "agent.si")
        self.assertEqual(normalize_domain("AGENT"), "agent.si")
        self.assertEqual(normalize_domain("agent.si"), "agent.si")
        self.assertEqual(normalize_domain("  'vector'  "), "vector.si")

    def test_validate_label(self):
        # Valid labels
        is_valid, _ = validate_label("ai")
        self.assertTrue(is_valid)

        is_valid, _ = validate_label("super-intelligence")
        self.assertTrue(is_valid)

        # Invalid: too short (1 char)
        is_valid, err = validate_label("a")
        self.assertFalse(is_valid)
        self.assertIn("at least 2", err)

        # Invalid: leading/trailing hyphen
        is_valid, err = validate_label("-tech")
        self.assertFalse(is_valid)

        is_valid, err = validate_label("tech-")
        self.assertFalse(is_valid)

        # Invalid: special symbols
        is_valid, err = validate_label("tech$ai")
        self.assertFalse(is_valid)


class TestBulkScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = BulkDomainScanner(workers=2, timeout=2)

    def test_invalid_domain_short_circuit(self):
        res = self.scanner.check_domain("a")
        self.assertEqual(res.status, DomainStatus.INVALID)
        self.assertEqual(res.http_code, 400)
        self.assertFalse(res.is_available)

    @patch("urllib.request.urlopen")
    def test_available_domain_http_404(self, mock_urlopen):
        # Simulate registry returning HTTP 404 (Domain Not Found -> Available)
        http_error = urllib.error.HTTPError(
            url="https://bulkdomainsearch.si/api/check?domain=unregistered.si",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )
        mock_urlopen.side_effect = http_error

        res = self.scanner.check_domain("unregistered.si")
        self.assertEqual(res.status, DomainStatus.AVAILABLE)
        self.assertEqual(res.http_code, 404)
        self.assertTrue(res.is_available)

    @patch("urllib.request.urlopen")
    def test_taken_domain_http_200(self, mock_urlopen):
        # Simulate registry returning HTTP 200 (Active domain)
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status": "TAKEN", "details": "Registered"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = self.scanner.check_domain("google.si")
        self.assertEqual(res.status, DomainStatus.TAKEN)
        self.assertEqual(res.http_code, 200)
        self.assertFalse(res.is_available)


if __name__ == "__main__":
    unittest.main()
