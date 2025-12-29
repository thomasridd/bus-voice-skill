# TfL Bus Checker Alexa Skill - Claude Code Specification

## Overview

Build an Alexa skill that checks Transport for London (TfL) bus arrivals for two specific stops (westbound to school, eastbound to station). Uses TfL Unified API to fetch real-time arrival predictions.

## Project Structure

```
tfl-bus-checker/
├── lambda/
│   ├── lambda_function.py          # Main Lambda handler
│   ├── tfl_client.py               # TfL API wrapper
│   ├── bus_formatter.py            # Response formatting
│   ├── config.py                   # Stop IDs and configuration
│   ├── requirements.txt            # Python dependencies
│   └── tests/
│       ├── test_tfl_client.py
│       └── test_bus_formatter.py
├── skill-package/
│   ├── skill.json                  # Skill manifest
│   └── interactionModels/
│       └── custom/
│           └── en-GB.json          # UK English interaction model
├── infrastructure/
│   └── template.yaml               # AWS SAM/CloudFormation
└── README.md
```

## Requirements

### Dependencies (requirements.txt)

```
ask-sdk-core==1.19.0
requests==2.31.0
python-dateutil==2.8.2
```

### AWS Resources

- Lambda function (Python 3.11 runtime)
- No database needed (stateless queries)
- IAM role with permissions:
  - CloudWatch Logs
- Lambda needs internet access (default VPC or NAT gateway if in VPC)

### External API

- TfL Unified API: <https://api.tfl.gov.uk>
- Endpoint: `/StopPoint/{stopId}/Arrivals`
- No API key required for basic usage (rate limited to 500 calls/min)
- Optional: Register for app_id and app_key for higher limits

## Functional Specification

### 1. TfL API Integration

**Configuration Required**

```python
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
```

**TfL API Response Structure** (arrivals endpoint)

```json
[
  {
    "id": "1234567890",
    "lineName": "25",
    "destinationName": "Oxford Circus",
    "towards": "Oxford Circus",
    "expectedArrival": "2024-01-15T14:32:45Z",
    "timeToStation": 125,  // seconds
    "currentLocation": "On approach",
    "platformName": "Stop A"
  }
]
```

### 2. Voice Interaction Design

#### Intents

**CheckSchoolBusesIntent**

- Utterances:
  - “when’s the next bus to school”
  - “check school buses”
  - “buses to school”
  - “school bus times”
  - “next {count} buses to school”
- Slot: `count` (AMAZON.NUMBER, optional, default 3)

**CheckStationBusesIntent**

- Utterances:
  - “when’s the next bus to the station”
  - “check station buses”
  - “buses to the station”
  - “station bus times”
  - “next {count} buses to the station”
- Slot: `count` (AMAZON.NUMBER, optional, default 3)

**CheckBothIntent**

- Utterances:
  - “check all buses”
  - “check both directions”
  - “what buses are coming”
  - “bus times”
- No slots (uses default count of 2 for brevity)

**AMAZON.HelpIntent** (built-in)
**AMAZON.CancelIntent** (built-in)
**AMAZON.StopIntent** (built-in)

### 3. Core Behaviors

#### Checking School Buses

1. Call TfL API for school stop ID
1. Parse and sort arrivals by `timeToStation` (ascending)
1. Filter to next N buses (default 3)
1. Format response:

   ```
   "The next 3 buses to school are:
    Route 25 in 2 minutes to Oxford Circus,
    Route 25 in 7 minutes to Oxford Circus,
    Route 73 in 12 minutes to Victoria."
   ```

#### Checking Station Buses

1. Call TfL API for station stop ID
1. Parse and sort arrivals by `timeToStation` (ascending)
1. Filter to next N buses (default 3)
1. Format response (same pattern as school)

#### Checking Both Directions

1. Make parallel API calls to both stops
1. Format combined response:

   ```
   "To school: Route 25 in 2 minutes, Route 25 in 7 minutes.
    To the station: Route 73 in 3 minutes, Route 388 in 9 minutes."
   ```

#### Launch Request (No Intent)

- Respond with help/prompt:

  ```
  "I can check buses to school or the station. Which would you like?"
  ```

### 4. Response Formatting Rules

**Time Formatting**

- < 1 minute: “due now” or “arriving now”
- 1 minute exactly: “in 1 minute”
- 2-59 minutes: “in X minutes”
- ≥ 60 minutes: “in X hours and Y minutes” (rare but handle it)

**Bus Description**

- Include route number and destination
- Format: “Route {lineName} in {time} to {destinationName}”
- If same route appears multiple times, still include destination each time

**Multiple Buses**

- Use natural language connectors: “and” for last item, commas for others
- Example: “Route 25 in 2 minutes, Route 73 in 5 minutes, and Route 25 in 8 minutes”

**No Buses Found**

- “No buses are scheduled to arrive at {location} in the next hour”

**API Errors**

- Timeout: “Sorry, I’m having trouble reaching Transport for London right now. Please try again”
- Invalid stop: “I couldn’t find bus information for that stop”
- Network error: “I can’t connect to the bus information service right now”

### 5. Implementation Requirements

#### TfL Client (`tfl_client.py`)

```python
class TfLClient:
    def get_arrivals(self, stop_id: str, timeout: int = 5) -> List[Dict]:
        """
        Fetch arrivals for a stop from TfL API
        Returns sorted list by timeToStation
        Raises: RequestException on network errors
        """
        pass

    def get_next_buses(self, stop_id: str, count: int = 3) -> List[Dict]:
        """
        Get next N buses for a stop
        Returns list of arrival dicts with keys: lineName, destinationName, timeToStation
        """
        pass
```

#### Bus Formatter (`bus_formatter.py`)

```python
def format_time_to_arrival(seconds: int) -> str:
    """Convert seconds to friendly string: '2 minutes', 'due now', etc."""
    pass

def format_single_bus(arrival: Dict) -> str:
    """Format one bus: 'Route 25 in 2 minutes to Oxford Circus'"""
    pass

def format_bus_list(arrivals: List[Dict], destination_name: str) -> str:
    """
    Format multiple buses for speech
    destination_name: 'school' or 'the station'
    Returns: Full sentence ready for Alexa speech
    """
    pass

def format_both_directions(school_buses: List[Dict], station_buses: List[Dict]) -> str:
    """Format buses for both directions in one response"""
    pass
```

#### Lambda Handler Structure

```python
def lambda_handler(event, context):
    # Initialize skill builder (no persistence needed)
    # Register request handlers:
    # 1. LaunchRequestHandler
    # 2. CheckSchoolBusesIntentHandler
    # 3. CheckStationBusesIntentHandler
    # 4. CheckBothIntentHandler
    # 5. HelpIntentHandler
    # 6. CancelAndStopIntentHandler
    # 7. SessionEndedRequestHandler
    # 8. IntentReflectorHandler (catchall)
    # 9. ErrorHandler
    pass
```

### 6. Error Handling

**Network Errors**

- Timeout (5 seconds): “Sorry, Transport for London isn’t responding. Please try again”
- Connection error: “I can’t reach the bus information service right now”
- HTTP 5xx: “Transport for London is experiencing issues. Please try again later”
- HTTP 4xx: “There’s a problem with the bus stop configuration. Please contact support”

**Data Validation**

- Empty arrivals list: “No buses are scheduled to arrive soon”
- Invalid stop ID in config: Log error, return generic error message
- Malformed API response: Log details, return “I received unexpected data from Transport for London”

**Rate Limiting**

- HTTP 429: “I’m checking buses too frequently. Please wait a moment and try again”

**Graceful Degradation**

- If one API call fails in “both” query, return data for the successful stop only
- Example: “I found buses to school, but couldn’t check the station. To school: Route 25 in 2 minutes…”

### 7. Testing Requirements

**Unit Tests**

`test_tfl_client.py`:

- Mock TfL API responses
- Test parsing of arrivals
- Test sorting by timeToStation
- Test filtering to N buses
- Test error conditions (timeout, 404, 500)

`test_bus_formatter.py`:

- Test time formatting edge cases (0 sec, 59 sec, 60 sec, 119 sec, 3600 sec)
- Test single bus formatting
- Test list formatting with 1, 2, 3, 5 buses
- Test both directions formatting
- Test empty list handling

**Integration Tests**

- Test full flow with mocked Alexa SDK
- Test all intents with various slot values
- Test concurrent API calls for “both” intent

**Manual Testing Checklist**

- [ ] “Check school buses” - verify 3 buses returned
- [ ] “Check station buses” - verify 3 buses returned
- [ ] “Check both directions” - verify both stops queried
- [ ] “Next 5 buses to school” - verify count respected
- [ ] “Next 1 bus to station” - verify singular grammar
- [ ] Test during off-peak hours (fewer buses)
- [ ] Test during peak hours (many buses)
- [ ] Test with network disconnected (error handling)
- [ ] Test Help, Stop, Cancel intents

### 8. Configuration Setup

**Finding Your Stop IDs**

1. Visit: [https://api.tfl.gov.uk/StopPoint/Search/{query}](https://api.tfl.gov.uk/StopPoint/Search/%7Bquery%7D)

- Example: `https://api.tfl.gov.uk/StopPoint/Search/Highbury`

1. Or use: <https://tfl.gov.uk/travel-information/stations-stops-and-piers/>
1. Stop IDs are 9-15 character alphanumeric codes (e.g., “490000123XYZ”)
1. Validate stop ID: `https://api.tfl.gov.uk/StopPoint/{stopId}`

**Update config.py Before Deployment**

```python
BUS_STOPS = {
    'school': {
        'stopId': 'YOUR_ACTUAL_STOP_ID_HERE',  # ← CHANGE THIS
        'name': 'School Stop',  # Friendly name for logs
        'direction': 'westbound'  # For reference only
    },
    'station': {
        'stopId': 'YOUR_ACTUAL_STOP_ID_HERE',  # ← CHANGE THIS
        'name': 'Station Stop',
        'direction': 'eastbound'
    }
}
```

### 9. Deployment

**Environment Variables**

- `LOG_LEVEL`: INFO (production) or DEBUG
- `TFL_APP_ID`: (optional) Your TfL application ID
- `TFL_APP_KEY`: (optional) Your TfL application key

**SAM Template Requirements**

- Lambda timeout: 10 seconds (API calls + processing)
- Memory: 256 MB
- Environment: Python 3.11
- Trigger: Alexa Skills Kit
- VPC: None (needs internet access for TfL API)

**Skill Manifest (skill.json)**

```json
{
  "manifest": {
    "publishingInformation": {
      "locales": {
        "en-GB": {
          "name": "Bus Times Checker",
          "summary": "Check next buses to school and station",
          "description": "Get real-time bus arrivals for your local stops",
          "examplePhrases": [
            "Alexa, ask Bus Times when's the next bus to school",
            "Alexa, ask Bus Times to check station buses",
            "Alexa, ask Bus Times to check both directions"
          ]
        }
      },
      "category": "TRAVEL_AND_TRANSPORTATION"
    },
    "apis": {
      "custom": {
        "endpoint": {
          "uri": "arn:aws:lambda:eu-west-2:ACCOUNT:function:tfl-bus-checker"
        }
      }
    }
  }
}
```

### 10. Enhancements (Optional)

**Phase 2 Ideas**:

- Cache API responses for 30 seconds (reduce API calls if asked repeatedly)
- Support route filtering: “Next route 25 to school”
- Add travel time estimates: “You can catch the bus in 2 minutes if you leave now”
- APL (Alexa Presentation Language) visual card showing bus times table
- Scheduled reminders: “Remind me of school buses every weekday at 8am”

**Performance Optimizations**:

- Use connection pooling with `requests.Session()`
- Implement exponential backoff for retries
- Add CloudWatch metrics for API latency monitoring

### 11. Success Criteria

The implementation should:

- ✅ Fetch real-time bus arrivals from TfL API
- ✅ Handle both stop locations (school and station)
- ✅ Support configurable bus count (1-10)
- ✅ Format times naturally (“2 minutes”, “due now”)
- ✅ Handle API timeouts and errors gracefully
- ✅ Provide helpful error messages to users
- ✅ Respond within 3 seconds under normal conditions
- ✅ Support “both directions” query efficiently
- ✅ Use proper English grammar (singular/plural)
- ✅ Work during TfL API outages with clear messaging

## Notes for Implementation

- TfL API requires HTTPS
- `timeToStation` is in seconds, already accounts for current time
- TfL occasionally returns duplicate entries - deduplicate if needed
- Bus routes may have letters (e.g., “25A”, “N25” for night buses)
- Platform names help disambiguate stops with multiple stands
- Consider logging stop_id + timestamp for debugging real-world issues
- Test during actual school run times to validate usefulness

## Example Interactions

```
User: "Alexa, ask Bus Times when's the next bus to school"
Alexa: "The next 3 buses to school are: Route 25 in 2 minutes to Oxford Circus,
        Route 25 in 7 minutes to Oxford Circus, and Route 73 in 12 minutes to Victoria."

User: "Alexa, ask Bus Times for the next 5 buses to the station"
Alexa: "The next 5 buses to the station are: Route 73 in 1 minute to Victoria,
        Route 388 in 4 minutes to Elephant and Castle, Route 73 in 8 minutes to Victoria,
        Route 25 in 11 minutes to Holborn, and Route 388 in 15 minutes to Elephant and Castle."

User: "Alexa, ask Bus Times to check both directions"
Alexa: "To school: Route 25 in 3 minutes and Route 73 in 9 minutes.
        To the station: Route 388 in 2 minutes and Route 73 in 7 minutes."
```
