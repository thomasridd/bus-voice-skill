# config.py
BUS_STOPS = {
    'school': {
        'stopId': '490009659W',  # Marketplace Westbound
        'name': 'School Stop',
        'direction': 'westbound'
    },
    'station': {
        'stopId': '490004093E',  # Blandford close Eastbound
        'name': 'Station Stop',
        'direction': 'eastbound'
    }
}

TFL_API_BASE = 'https://api.tfl.gov.uk'
DEFAULT_BUS_COUNT = 3  # Number of next buses to report
TIMEOUT_SECONDS = 5
