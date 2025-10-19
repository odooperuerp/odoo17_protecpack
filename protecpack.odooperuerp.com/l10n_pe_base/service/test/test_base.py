import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from service.main.sire import SireSunatBase, ApiSireSunat
from service.test.credentials import RUC, USER, PASSWORD


class TestSireSunatBase(unittest.TestCase):

    @patch('requests.request')
    def test_request_access_token_success(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {
            "access_token": "mock_access_token",
            "expires_in": 3600
        }

        sire_base = SireSunatBase(ruc=RUC, user=USER, password=PASSWORD)

        access_token, expires_in = sire_base._request_access_token()

        self.assertEqual(access_token, "mock_access_token")
        self.assertEqual(expires_in, 3600)

    @patch('requests.request')
    def test_request_access_token_failure(self, mock_request):
        mock_request.return_value.status_code = 401

        sire_base = SireSunatBase(ruc='mock_ruc', user='mock_user', password='mock_password')

        access_token, expires_in = sire_base._request_access_token()

        self.assertIsNone(access_token)
        self.assertEqual(expires_in, 1)


if __name__ == '__main__':
    unittest.main()