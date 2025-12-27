"""
Unit tests for tfl_client module
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tfl_client import TfLClient
from requests.exceptions import RequestException, Timeout


class TestTfLClient(unittest.TestCase):
    """Test TfL API client"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = TfLClient()
        self.test_stop_id = '490000123ABC'

    @patch('tfl_client.requests.get')
    def test_get_arrivals_success(self, mock_get):
        """Test successful API response"""
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': '1',
                'lineName': '25',
                'destinationName': 'Oxford Circus',
                'timeToStation': 300
            },
            {
                'id': '2',
                'lineName': '73',
                'destinationName': 'Victoria',
                'timeToStation': 120
            },
            {
                'id': '3',
                'lineName': '25',
                'destinationName': 'Oxford Circus',
                'timeToStation': 600
            }
        ]
        mock_get.return_value = mock_response

        # Call the method
        arrivals = self.client.get_arrivals(self.test_stop_id)

        # Verify results
        self.assertEqual(len(arrivals), 3)
        # Should be sorted by timeToStation
        self.assertEqual(arrivals[0]['timeToStation'], 120)
        self.assertEqual(arrivals[1]['timeToStation'], 300)
        self.assertEqual(arrivals[2]['timeToStation'], 600)

    @patch('tfl_client.requests.get')
    def test_get_arrivals_sorting(self, mock_get):
        """Test that arrivals are sorted by timeToStation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'lineName': 'A', 'timeToStation': 500},
            {'lineName': 'B', 'timeToStation': 100},
            {'lineName': 'C', 'timeToStation': 300},
            {'lineName': 'D', 'timeToStation': 200}
        ]
        mock_get.return_value = mock_response

        arrivals = self.client.get_arrivals(self.test_stop_id)

        # Verify sorting
        self.assertEqual(arrivals[0]['timeToStation'], 100)
        self.assertEqual(arrivals[1]['timeToStation'], 200)
        self.assertEqual(arrivals[2]['timeToStation'], 300)
        self.assertEqual(arrivals[3]['timeToStation'], 500)

    @patch('tfl_client.requests.get')
    def test_get_arrivals_timeout(self, mock_get):
        """Test timeout handling"""
        mock_get.side_effect = Timeout("Request timed out")

        with self.assertRaises(Timeout):
            self.client.get_arrivals(self.test_stop_id)

    @patch('tfl_client.requests.get')
    def test_get_arrivals_404(self, mock_get):
        """Test 404 error (invalid stop)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = RequestException("404 Not Found")
        mock_get.return_value = mock_response

        with self.assertRaises(RequestException):
            self.client.get_arrivals(self.test_stop_id)

    @patch('tfl_client.requests.get')
    def test_get_arrivals_500(self, mock_get):
        """Test 500 error (server error)"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = RequestException("500 Server Error")
        mock_get.return_value = mock_response

        with self.assertRaises(RequestException):
            self.client.get_arrivals(self.test_stop_id)

    @patch('tfl_client.requests.get')
    def test_get_next_buses(self, mock_get):
        """Test getting next N buses"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'lineName': '25',
                'destinationName': 'Oxford Circus',
                'timeToStation': 120,
                'towards': 'Oxford Circus',
                'expectedArrival': '2024-01-15T14:32:45Z'
            },
            {
                'lineName': '73',
                'destinationName': 'Victoria',
                'timeToStation': 300,
                'towards': 'Victoria',
                'expectedArrival': '2024-01-15T14:35:00Z'
            },
            {
                'lineName': '25',
                'destinationName': 'Oxford Circus',
                'timeToStation': 600,
                'towards': 'Oxford Circus',
                'expectedArrival': '2024-01-15T14:40:00Z'
            }
        ]
        mock_get.return_value = mock_response

        # Get next 2 buses
        buses = self.client.get_next_buses(self.test_stop_id, count=2)

        # Verify results
        self.assertEqual(len(buses), 2)
        self.assertEqual(buses[0]['lineName'], '25')
        self.assertEqual(buses[0]['destinationName'], 'Oxford Circus')
        self.assertEqual(buses[0]['timeToStation'], 120)
        self.assertEqual(buses[1]['lineName'], '73')
        self.assertEqual(buses[1]['timeToStation'], 300)

        # Verify only necessary fields are returned
        self.assertIn('lineName', buses[0])
        self.assertIn('destinationName', buses[0])
        self.assertIn('timeToStation', buses[0])
        self.assertNotIn('towards', buses[0])
        self.assertNotIn('expectedArrival', buses[0])

    @patch('tfl_client.requests.get')
    def test_get_next_buses_default_count(self, mock_get):
        """Test default count of 3 buses"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'lineName': '1', 'destinationName': 'Dest1', 'timeToStation': 100},
            {'lineName': '2', 'destinationName': 'Dest2', 'timeToStation': 200},
            {'lineName': '3', 'destinationName': 'Dest3', 'timeToStation': 300},
            {'lineName': '4', 'destinationName': 'Dest4', 'timeToStation': 400},
            {'lineName': '5', 'destinationName': 'Dest5', 'timeToStation': 500}
        ]
        mock_get.return_value = mock_response

        buses = self.client.get_next_buses(self.test_stop_id)

        # Should return 3 by default
        self.assertEqual(len(buses), 3)

    @patch('tfl_client.requests.get')
    def test_get_next_buses_fewer_than_requested(self, mock_get):
        """Test when fewer buses available than requested"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'lineName': '25', 'destinationName': 'Oxford Circus', 'timeToStation': 120}
        ]
        mock_get.return_value = mock_response

        buses = self.client.get_next_buses(self.test_stop_id, count=5)

        # Should return only 1 bus (all that's available)
        self.assertEqual(len(buses), 1)

    @patch('tfl_client.requests.get')
    def test_build_url_with_auth(self, mock_get):
        """Test URL building with authentication"""
        # Set environment variables
        with patch.dict(os.environ, {'TFL_APP_ID': 'test_id', 'TFL_APP_KEY': 'test_key'}):
            client = TfLClient()

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            client.get_arrivals(self.test_stop_id)

            # Verify URL includes auth params
            called_url = mock_get.call_args[0][0]
            self.assertIn('app_id=test_id', called_url)
            self.assertIn('app_key=test_key', called_url)

    @patch('tfl_client.requests.get')
    def test_build_url_without_auth(self, mock_get):
        """Test URL building without authentication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        self.client.get_arrivals(self.test_stop_id)

        # Verify URL doesn't include auth params
        called_url = mock_get.call_args[0][0]
        self.assertNotIn('app_id', called_url)
        self.assertNotIn('app_key', called_url)


if __name__ == '__main__':
    unittest.main()
