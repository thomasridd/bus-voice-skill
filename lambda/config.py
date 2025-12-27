# config.py
BUS_STOPS = {
    'school': {
        'stopId': '490000123ABC',  # Replace with actual stop ID
        'name': 'School Stop',
        'direction': 'westbound'
    },
    'station': {
        'stopId': '490000456DEF',  # Replace with actual stop ID
        'name': 'Station Stop',
        'direction': 'eastbound'
    }
}

TFL_API_BASE = 'https://api.tfl.gov.uk'
DEFAULT_BUS_COUNT = 3  # Number of next buses to report
TIMEOUT_SECONDS = 5
