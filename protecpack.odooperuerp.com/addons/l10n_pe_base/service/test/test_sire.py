import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from service.main.sire import SireSunatBase,ApiSireSunat
from service.test.credentials import RUC, USER, PASSWORD


class TestApiSireSunat(unittest.TestCase):

    @patch('requests.get')
    def test_get_proposal_ticket_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "numTicket": "mock_ticket_number"
        }

        api_sire = ApiSireSunat(ruc=RUC, user=USER, password=PASSWORD)

        ticket_number = api_sire.get_proposal_ticket(period='202201')

        self.assertEqual(ticket_number, "mock_ticket_number")


    @patch('requests.get')
    def test_get_file_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
                   'registros': [
                       {'archivoReporte': [
                               {
                                   'codTipoAchivoReporte': 'mock_cod',
                                   'nomArchivoReporte': 'mock_report_name',
                                   'nomArchivoContenido': 'mock_content_name'
                               }
                           ]}]}

        api_sire = ApiSireSunat(ruc=RUC, user=USER, password=PASSWORD)
        ticket_number = api_sire.get_proposal_ticket(period='202307')
        result = api_sire.get_file_data(initial_period='202201', final_period='202202', num_ticket=ticket_number)
        expected_result = ['mock_cod', 'mock_report_name', 'mock_content_name']

        self.assertEqual(result, expected_result)


    @patch('requests.get')
    def test_download_zip_file_txt_success_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'mock_file_content'

        api_sire = ApiSireSunat(ruc=RUC, user=USER, password=PASSWORD)
        ticket_number = api_sire.get_proposal_ticket(period='202307')
        file_data = api_sire.get_file_data(initial_period='202307', final_period='202307', num_ticket=ticket_number)
        result = api_sire.download_zip_file_txt(report_name=file_data[1], report_type=file_data[0])
        expected_result = b'mock_file_content'
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()