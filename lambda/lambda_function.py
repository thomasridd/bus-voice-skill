"""
AWS Lambda handler for TfL Bus Checker Alexa Skill
"""
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from requests.exceptions import RequestException, Timeout

from tfl_client import TfLClient
from bus_formatter import format_bus_list, format_both_directions
from config import BUS_STOPS, DEFAULT_BUS_COUNT

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize TfL client
tfl_client = TfLClient()


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "I can check buses to school or the station. Which would you like?"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CheckSchoolBusesIntentHandler(AbstractRequestHandler):
    """Handler for CheckSchoolBusesIntent"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("CheckSchoolBusesIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Get count from slot or use default
        slots = handler_input.request_envelope.request.intent.slots
        count = DEFAULT_BUS_COUNT

        if 'count' in slots and slots['count'].value:
            try:
                count = int(slots['count'].value)
                count = max(1, min(count, 10))  # Clamp between 1 and 10
            except (ValueError, TypeError):
                count = DEFAULT_BUS_COUNT

        try:
            school_stop_id = BUS_STOPS['school']['stopId']
            buses = tfl_client.get_next_buses(school_stop_id, count)
            speak_output = format_bus_list(buses, 'school')

        except Timeout:
            speak_output = "Sorry, Transport for London isn't responding. Please try again."
        except RequestException as e:
            logger.error(f"Error fetching school buses: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 429:
                    speak_output = "I'm checking buses too frequently. Please wait a moment and try again."
                elif 400 <= status_code < 500:
                    speak_output = "There's a problem with the bus stop configuration. Please contact support."
                elif 500 <= status_code < 600:
                    speak_output = "Transport for London is experiencing issues. Please try again later."
                else:
                    speak_output = "I can't reach the bus information service right now."
            else:
                speak_output = "I can't connect to the bus information service right now."
        except Exception as e:
            logger.error(f"Unexpected error in CheckSchoolBusesIntent: {str(e)}")
            speak_output = "I received unexpected data from Transport for London."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class CheckStationBusesIntentHandler(AbstractRequestHandler):
    """Handler for CheckStationBusesIntent"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("CheckStationBusesIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Get count from slot or use default
        slots = handler_input.request_envelope.request.intent.slots
        count = DEFAULT_BUS_COUNT

        if 'count' in slots and slots['count'].value:
            try:
                count = int(slots['count'].value)
                count = max(1, min(count, 10))  # Clamp between 1 and 10
            except (ValueError, TypeError):
                count = DEFAULT_BUS_COUNT

        try:
            station_stop_id = BUS_STOPS['station']['stopId']
            buses = tfl_client.get_next_buses(station_stop_id, count)
            speak_output = format_bus_list(buses, 'the station')

        except Timeout:
            speak_output = "Sorry, Transport for London isn't responding. Please try again."
        except RequestException as e:
            logger.error(f"Error fetching station buses: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 429:
                    speak_output = "I'm checking buses too frequently. Please wait a moment and try again."
                elif 400 <= status_code < 500:
                    speak_output = "There's a problem with the bus stop configuration. Please contact support."
                elif 500 <= status_code < 600:
                    speak_output = "Transport for London is experiencing issues. Please try again later."
                else:
                    speak_output = "I can't reach the bus information service right now."
            else:
                speak_output = "I can't connect to the bus information service right now."
        except Exception as e:
            logger.error(f"Unexpected error in CheckStationBusesIntent: {str(e)}")
            speak_output = "I received unexpected data from Transport for London."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class CheckBothIntentHandler(AbstractRequestHandler):
    """Handler for CheckBothIntent - checks both directions"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("CheckBothIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Use smaller count for "both" query to keep response concise
        count = 2

        school_buses = []
        station_buses = []
        errors = []

        # Fetch both stops in parallel
        def fetch_school():
            try:
                return tfl_client.get_next_buses(BUS_STOPS['school']['stopId'], count)
            except Exception as e:
                logger.error(f"Error fetching school buses: {str(e)}")
                return None

        def fetch_station():
            try:
                return tfl_client.get_next_buses(BUS_STOPS['station']['stopId'], count)
            except Exception as e:
                logger.error(f"Error fetching station buses: {str(e)}")
                return None

        # Execute API calls in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            school_future = executor.submit(fetch_school)
            station_future = executor.submit(fetch_station)

            school_buses = school_future.result()
            station_buses = station_future.result()

        # Handle graceful degradation
        if school_buses is None and station_buses is None:
            speak_output = "Sorry, I can't reach the bus information service right now."
        elif school_buses is None:
            speak_output = "I found buses to the station, but couldn't check school. " + \
                          format_bus_list(station_buses, 'the station')
        elif station_buses is None:
            speak_output = "I found buses to school, but couldn't check the station. " + \
                          format_bus_list(school_buses, 'school')
        else:
            speak_output = format_both_directions(school_buses, station_buses)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = (
            "I can check buses to school or the station. "
            "You can say things like: check school buses, "
            "next five buses to the station, or check both directions. "
            "What would you like?"
        )

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for Cancel and Stop Intents"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        # Cleanup logic (if needed)
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """Catchall handler for intent reflection"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        intent_name = handler_input.request_envelope.request.intent.name
        speak_output = f"You just triggered {intent_name}. I'm not sure how to handle that."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handler"""

    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(f"Unexpected error: {exception}", exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


# Build skill
sb = SkillBuilder()

# Register request handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CheckSchoolBusesIntentHandler())
sb.add_request_handler(CheckStationBusesIntentHandler())
sb.add_request_handler(CheckBothIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())  # Make sure this is last

# Register exception handler
sb.add_exception_handler(CatchAllExceptionHandler())

# Lambda handler
lambda_handler = sb.lambda_handler()
