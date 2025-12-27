"""
Bus arrival response formatting for Alexa speech output
"""
from typing import List, Dict


def format_time_to_arrival(seconds: int) -> str:
    """
    Convert seconds to friendly string: '2 minutes', 'due now', etc.

    Args:
        seconds: Time to arrival in seconds

    Returns:
        Formatted time string for speech output
    """
    if seconds < 60:
        return "due now"

    minutes = seconds // 60

    if minutes == 1:
        return "in 1 minute"

    if minutes < 60:
        return f"in {minutes} minutes"

    # Handle >= 60 minutes (rare but possible)
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        if hours == 1:
            return "in 1 hour"
        return f"in {hours} hours"

    if hours == 1:
        if remaining_minutes == 1:
            return "in 1 hour and 1 minute"
        return f"in 1 hour and {remaining_minutes} minutes"

    if remaining_minutes == 1:
        return f"in {hours} hours and 1 minute"
    return f"in {hours} hours and {remaining_minutes} minutes"


def format_single_bus(arrival: Dict) -> str:
    """
    Format one bus: 'Route 25 in 2 minutes to Oxford Circus'

    Args:
        arrival: Dict with keys lineName, destinationName, timeToStation

    Returns:
        Formatted bus description
    """
    route = arrival['lineName']
    destination = arrival['destinationName']
    time_str = format_time_to_arrival(arrival['timeToStation'])

    return f"Route {route} {time_str} to {destination}"


def format_bus_list(arrivals: List[Dict], destination_name: str) -> str:
    """
    Format multiple buses for speech

    Args:
        arrivals: List of arrival dicts
        destination_name: 'school' or 'the station'

    Returns:
        Full sentence ready for Alexa speech
    """
    if not arrivals:
        return f"No buses are scheduled to arrive at {destination_name} in the next hour"

    count = len(arrivals)

    if count == 1:
        bus_desc = format_single_bus(arrivals[0])
        return f"The next bus to {destination_name} is {bus_desc}."

    # Multiple buses
    bus_descriptions = [format_single_bus(bus) for bus in arrivals]

    # Join with commas and 'and' for the last item
    if count == 2:
        buses_str = f"{bus_descriptions[0]}, and {bus_descriptions[1]}"
    else:
        all_but_last = ", ".join(bus_descriptions[:-1])
        buses_str = f"{all_but_last}, and {bus_descriptions[-1]}"

    return f"The next {count} buses to {destination_name} are: {buses_str}."


def format_both_directions(school_buses: List[Dict], station_buses: List[Dict]) -> str:
    """
    Format buses for both directions in one response

    Args:
        school_buses: List of arrivals for school stop
        station_buses: List of arrivals for station stop

    Returns:
        Combined response for both directions
    """
    school_parts = []
    station_parts = []

    # Format school buses (short format for "both" query)
    if school_buses:
        for bus in school_buses:
            route = bus['lineName']
            time_str = format_time_to_arrival(bus['timeToStation'])
            school_parts.append(f"Route {route} {time_str}")

    # Format station buses
    if station_buses:
        for bus in station_buses:
            route = bus['lineName']
            time_str = format_time_to_arrival(bus['timeToStation'])
            station_parts.append(f"Route {route} {time_str}")

    # Build combined response
    parts = []

    if school_parts:
        if len(school_parts) == 1:
            school_str = school_parts[0]
        elif len(school_parts) == 2:
            school_str = f"{school_parts[0]} and {school_parts[1]}"
        else:
            all_but_last = ", ".join(school_parts[:-1])
            school_str = f"{all_but_last}, and {school_parts[-1]}"
        parts.append(f"To school: {school_str}")
    else:
        parts.append("To school: no buses scheduled soon")

    if station_parts:
        if len(station_parts) == 1:
            station_str = station_parts[0]
        elif len(station_parts) == 2:
            station_str = f"{station_parts[0]} and {station_parts[1]}"
        else:
            all_but_last = ", ".join(station_parts[:-1])
            station_str = f"{all_but_last}, and {station_parts[-1]}"
        parts.append(f"To the station: {station_str}")
    else:
        parts.append("To the station: no buses scheduled soon")

    return ". ".join(parts) + "."
