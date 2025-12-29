"""
TfL Unified API client for fetching bus arrivals
"""

import os

import requests
from config import TFL_API_BASE, TIMEOUT_SECONDS
from requests.exceptions import RequestException, Timeout


class TfLClient:
    """Client for interacting with Transport for London Unified API"""

    def __init__(self, base_url: str = None, timeout: int = None):
        """
        Initialize TfL API client

        Args:
            base_url: Override default TfL API base URL (mainly for testing)
            timeout: Override default timeout in seconds
        """
        self.base_url = base_url or TFL_API_BASE
        self.timeout = timeout or TIMEOUT_SECONDS
        self.app_id = os.environ.get("TFL_APP_ID")
        self.app_key = os.environ.get("TFL_APP_KEY")

    def _build_url(self, stop_id: str) -> str:
        """
        Build the API URL with optional authentication parameters

        Args:
            stop_id: TfL stop point ID

        Returns:
            Complete URL for the arrivals endpoint
        """
        url = f"{self.base_url}/StopPoint/{stop_id}/Arrivals"

        # Add authentication if available
        if self.app_id and self.app_key:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}app_id={self.app_id}&app_key={self.app_key}"

        return url

    def get_arrivals(self, stop_id: str, timeout: int = None) -> list[dict]:
        """
        Fetch arrivals for a stop from TfL API

        Args:
            stop_id: TfL stop point ID
            timeout: Optional timeout override

        Returns:
            Sorted list of arrivals by timeToStation (ascending)

        Raises:
            RequestException: On network errors
            Timeout: On request timeout
        """
        url = self._build_url(stop_id)
        timeout_val = timeout or self.timeout

        try:
            response = requests.get(url, timeout=timeout_val)
            response.raise_for_status()

            arrivals = response.json()

            # Sort by timeToStation (ascending)
            sorted_arrivals = sorted(arrivals, key=lambda x: x.get("timeToStation", float("inf")))

            return sorted_arrivals

        except Timeout as e:
            raise Timeout(f"TfL API request timed out after {timeout_val} seconds") from e
        except RequestException as e:
            raise RequestException(f"Error fetching arrivals: {str(e)}") from e

    def get_next_buses(self, stop_id: str, count: int = 3) -> list[dict]:
        """
        Get next N buses for a stop

        Args:
            stop_id: TfL stop point ID
            count: Number of buses to return

        Returns:
            List of arrival dicts with keys: lineName, destinationName, timeToStation

        Raises:
            RequestException: On network errors
            Timeout: On request timeout
        """
        arrivals = self.get_arrivals(stop_id)

        # Filter to next N buses
        next_buses = arrivals[:count]

        # Return only the fields we need
        return [
            {
                "lineName": bus.get("lineName", "Unknown"),
                "destinationName": bus.get("destinationName", "Unknown"),
                "timeToStation": bus.get("timeToStation", 0),
            }
            for bus in next_buses
        ]
