"""
Unit tests for bus_formatter module
"""

import os
import sys
import unittest

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bus_formatter import (
    format_both_directions,
    format_bus_list,
    format_single_bus,
    format_time_to_arrival,
)


class TestFormatTimeToArrival(unittest.TestCase):
    """Test time formatting edge cases"""

    def test_zero_seconds(self):
        """< 1 minute should be 'due now'"""
        self.assertEqual(format_time_to_arrival(0), "due now")

    def test_59_seconds(self):
        """59 seconds should be 'due now'"""
        self.assertEqual(format_time_to_arrival(59), "due now")

    def test_60_seconds(self):
        """60 seconds should be 'in 1 minute'"""
        self.assertEqual(format_time_to_arrival(60), "in 1 minute")

    def test_119_seconds(self):
        """119 seconds should be 'in 1 minute'"""
        self.assertEqual(format_time_to_arrival(119), "in 1 minute")

    def test_120_seconds(self):
        """120 seconds should be 'in 2 minutes'"""
        self.assertEqual(format_time_to_arrival(120), "in 2 minutes")

    def test_multiple_minutes(self):
        """Test various minute values"""
        self.assertEqual(format_time_to_arrival(180), "in 3 minutes")
        self.assertEqual(format_time_to_arrival(600), "in 10 minutes")
        self.assertEqual(format_time_to_arrival(3540), "in 59 minutes")

    def test_exactly_one_hour(self):
        """3600 seconds should be 'in 1 hour'"""
        self.assertEqual(format_time_to_arrival(3600), "in 1 hour")

    def test_one_hour_one_minute(self):
        """3660 seconds should be 'in 1 hour and 1 minute'"""
        self.assertEqual(format_time_to_arrival(3660), "in 1 hour and 1 minute")

    def test_one_hour_multiple_minutes(self):
        """3720 seconds should be 'in 1 hour and 2 minutes'"""
        self.assertEqual(format_time_to_arrival(3720), "in 1 hour and 2 minutes")

    def test_multiple_hours(self):
        """7200 seconds should be 'in 2 hours'"""
        self.assertEqual(format_time_to_arrival(7200), "in 2 hours")

    def test_multiple_hours_one_minute(self):
        """7260 seconds should be 'in 2 hours and 1 minute'"""
        self.assertEqual(format_time_to_arrival(7260), "in 2 hours and 1 minute")

    def test_multiple_hours_multiple_minutes(self):
        """7320 seconds should be 'in 2 hours and 2 minutes'"""
        self.assertEqual(format_time_to_arrival(7320), "in 2 hours and 2 minutes")


class TestFormatSingleBus(unittest.TestCase):
    """Test single bus formatting"""

    def test_format_single_bus(self):
        """Test basic bus formatting"""
        arrival = {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 120}
        result = format_single_bus(arrival)
        self.assertEqual(result, "The 25 in 2 minutes")

    def test_format_single_bus_due_now(self):
        """Test bus arriving soon"""
        arrival = {"lineName": "73", "destinationName": "Victoria", "timeToStation": 30}
        result = format_single_bus(arrival)
        self.assertEqual(result, "The 73 due now")

    def test_format_single_bus_with_letter(self):
        """Test bus route with letter (like 25A)"""
        arrival = {"lineName": "25A", "destinationName": "Holborn", "timeToStation": 300}
        result = format_single_bus(arrival)
        self.assertEqual(result, "The 25A in 5 minutes")


class TestFormatBusList(unittest.TestCase):
    """Test list formatting with different numbers of buses"""

    def test_empty_list(self):
        """Test empty list handling"""
        result = format_bus_list([], "school")
        self.assertEqual(result, "No buses are scheduled to arrive at school in the next hour")

    def test_one_bus(self):
        """Test singular bus"""
        arrivals = [{"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 120}]
        result = format_bus_list(arrivals, "school")
        self.assertEqual(result, "The next bus to school is The 25 in 2 minutes.")

    def test_two_buses(self):
        """Test two buses with 'and' connector"""
        arrivals = [
            {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 120},
            {"lineName": "73", "destinationName": "Victoria", "timeToStation": 300},
        ]
        result = format_bus_list(arrivals, "the station")
        self.assertEqual(
            result,
            "The next 2 buses to the station are: The 25 in 2 minutes, and The 73 in 5 minutes.",
        )

    def test_three_buses(self):
        """Test three buses"""
        arrivals = [
            {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 120},
            {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 420},
            {"lineName": "73", "destinationName": "Victoria", "timeToStation": 720},
        ]
        result = format_bus_list(arrivals, "school")
        self.assertEqual(
            result,
            "The next 3 buses to school are: The 25 in 2 minutes, The 25 in 7 minutes, and The 73 in 12 minutes.",
        )

    def test_five_buses(self):
        """Test five buses with proper comma and 'and' usage"""
        arrivals = [
            {"lineName": "73", "destinationName": "Victoria", "timeToStation": 60},
            {"lineName": "388", "destinationName": "Elephant and Castle", "timeToStation": 240},
            {"lineName": "73", "destinationName": "Victoria", "timeToStation": 480},
            {"lineName": "25", "destinationName": "Holborn", "timeToStation": 660},
            {"lineName": "388", "destinationName": "Elephant and Castle", "timeToStation": 900},
        ]
        result = format_bus_list(arrivals, "the station")
        self.assertIn("The next 5 buses to the station are:", result)
        self.assertIn("The 73 in 1 minute", result)
        self.assertIn("The 388 in 4 minutes", result)
        self.assertIn("and The 388 in 15 minutes.", result)


class TestFormatBothDirections(unittest.TestCase):
    """Test both directions formatting"""

    def test_both_directions_with_buses(self):
        """Test normal case with buses in both directions"""
        school_buses = [
            {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 180},
            {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 420},
        ]
        station_buses = [
            {"lineName": "73", "destinationName": "Victoria", "timeToStation": 120},
            {"lineName": "388", "destinationName": "Elephant and Castle", "timeToStation": 540},
        ]
        result = format_both_directions(school_buses, station_buses)
        self.assertIn("To school:", result)
        self.assertIn("The 25 in 3 minutes", result)
        self.assertIn("The 25 in 7 minutes", result)
        self.assertIn("To the station:", result)
        self.assertIn("The 73 in 2 minutes", result)
        self.assertIn("The 388 in 9 minutes", result)

    def test_both_directions_empty_school(self):
        """Test with no school buses"""
        school_buses = []
        station_buses = [{"lineName": "73", "destinationName": "Victoria", "timeToStation": 120}]
        result = format_both_directions(school_buses, station_buses)
        self.assertIn("To school: no buses scheduled soon", result)
        self.assertIn("To the station: The 73 in 2 minutes", result)

    def test_both_directions_empty_station(self):
        """Test with no station buses"""
        school_buses = [
            {"lineName": "25", "destinationName": "Oxford Circus", "timeToStation": 180}
        ]
        station_buses = []
        result = format_both_directions(school_buses, station_buses)
        self.assertIn("To school: The 25 in 3 minutes", result)
        self.assertIn("To the station: no buses scheduled soon", result)

    def test_both_directions_all_empty(self):
        """Test with no buses in either direction"""
        school_buses = []
        station_buses = []
        result = format_both_directions(school_buses, station_buses)
        self.assertIn("To school: no buses scheduled soon", result)
        self.assertIn("To the station: no buses scheduled soon", result)


if __name__ == "__main__":
    unittest.main()
