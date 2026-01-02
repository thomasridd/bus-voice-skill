# CLAUDE.md - AI Assistant Guide

> This document provides comprehensive guidance for AI assistants working with the TfL Bus Checker Alexa Skill codebase.

**Last Updated:** 2026-01-02

---

## Table of Contents

- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Key Technologies & Tools](#key-technologies--tools)
- [Development Workflow](#development-workflow)
- [Code Style & Conventions](#code-style--conventions)
- [Testing Strategy](#testing-strategy)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Common Tasks](#common-tasks)
- [File Reference](#file-reference)
- [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

**Name:** TfL Bus Checker Alexa Skill
**Purpose:** An Alexa skill that provides real-time bus arrival information for two specific stops (school and station) using the Transport for London (TfL) Unified API.

**Key Features:**
- Check next buses to school (westbound)
- Check next buses to station (eastbound)
- Check both directions simultaneously
- Real-time arrival predictions from TfL API
- Natural language time formatting ("2 minutes", "due now")

**Target Users:** Families with school-age children in London who need quick bus arrival information.

---

## Repository Structure

```
bus-voice-skill/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline (tests, linting, security)
│       └── deploy.yml          # Deployment pipeline (dev/prod)
│
├── lambda/                     # AWS Lambda function code
│   ├── lambda_function.py      # Main handler with Alexa intent handlers
│   ├── tfl_client.py           # TfL API client wrapper
│   ├── bus_formatter.py        # Response formatting for speech output
│   ├── config.py               # Configuration (stop IDs, constants)
│   ├── requirements.txt        # Production dependencies
│   ├── requirements-dev.txt    # Development dependencies
│   └── tests/                  # Unit tests
│       ├── test_tfl_client.py
│       └── test_bus_formatter.py
│
├── infrastructure/
│   └── template.yaml           # AWS SAM template (CloudFormation)
│
├── skill-package/
│   ├── skill.json              # Alexa skill manifest
│   └── interactionModels/
│       └── custom/
│           └── en-GB.json      # UK English voice interaction model
│
├── test-events/                # Sample Alexa requests for local testing
│   ├── launch-request.json
│   └── check-school-buses.json
│
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── pyproject.toml              # Ruff and coverage configuration
├── Makefile                    # Development commands
├── README.md                   # Main project documentation
├── SETUP.md                    # Setup instructions
├── AWS_SETUP.md                # AWS deployment setup
├── CI_CD_GUIDE.md              # CI/CD documentation
└── DEPLOYMENT_TROUBLESHOOTING.md  # Deployment help
```

---

## Key Technologies & Tools

### Core Technologies
- **Python 3.11+** - Primary language (AWS Lambda runtime)
- **AWS Lambda** - Serverless compute for Alexa skill backend
- **Alexa Skills Kit (ASK)** - Voice interface framework
- **TfL Unified API** - Real-time bus data source

### Development Tools
- **Ruff** - Fast Python linter and formatter (replaces Black, isort, Flake8)
- **Bandit** - Security vulnerability scanner
- **Coverage.py** - Code coverage reporting
- **unittest** - Testing framework (Python standard library)
- **pre-commit** - Git hooks for automated checks

### Build & Deployment
- **AWS SAM (Serverless Application Model)** - Infrastructure as code
- **GitHub Actions** - CI/CD automation
- **CloudFormation** - AWS resource provisioning

### External APIs
- **TfL Unified API** - `https://api.tfl.gov.uk`
  - Endpoint: `/StopPoint/{stopId}/Arrivals`
  - No API key required (basic usage, 500 calls/min limit)
  - Optional: Register for app_id/app_key for higher limits

---

## Development Workflow

### Initial Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repo-url>
   cd bus-voice-skill
   make install-dev
   ```

2. **Set up pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. **Configure stop IDs:**
   - Edit `lambda/config.py`
   - Replace placeholder stop IDs with actual TfL stop IDs
   - Find stop IDs at: `https://api.tfl.gov.uk/StopPoint/Search/{query}`

### Development Cycle

```
┌─────────────────┐
│  Make Changes   │
└────────┬────────┘
         │
         ├──> Pre-commit runs (auto format + lint)
         │
         ├──> make test (run unit tests)
         │
         ├──> make lint (check code quality)
         │
         ├──> make security (scan for vulnerabilities)
         │
         ├──> git commit (if all checks pass)
         │
         └──> Push to GitHub → CI pipeline runs
                              │
                              ├─> Tests on Python 3.11 & 3.12
                              ├─> Lint & format checks
                              ├─> Security scans
                              ├─> Dependency vulnerability checks
                              └─> Skill package validation
```

### Branching Strategy

- **main** - Production-ready code
- **develop** - Integration branch (if used)
- **feature/** - Feature branches (merge to develop or main)
- **fix/** - Bug fix branches

---

## Code Style & Conventions

### Python Style Guide

**Configured via `pyproject.toml`:**
- Line length: **100 characters**
- Target Python: **3.11+**
- Quote style: **Double quotes**
- Indentation: **4 spaces**

### Ruff Rules Enabled
```python
# pyproject.toml [tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort (import sorting)
    "N",   # pep8-naming
    "UP",  # pyupgrade (modern Python syntax)
    "B",   # flake8-bugbear (common bugs)
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
```

### Import Ordering
```python
# 1. Standard library
import logging
import os
from concurrent.futures import ThreadPoolExecutor

# 2. Third-party packages
from ask_sdk_core.skill_builder import SkillBuilder
from requests.exceptions import RequestException

# 3. Local modules
from bus_formatter import format_bus_list
from config import BUS_STOPS
from tfl_client import TfLClient
```

### Naming Conventions
- **Classes:** PascalCase (`CheckSchoolBusesIntentHandler`)
- **Functions/Methods:** snake_case (`get_next_buses`, `format_time_to_arrival`)
- **Constants:** UPPER_SNAKE_CASE (`DEFAULT_BUS_COUNT`, `TFL_API_BASE`)
- **Private members:** Prefix with underscore (`_validate_response`)

### Docstrings
```python
def get_arrivals(self, stop_id: str, timeout: int = 5) -> List[Dict]:
    """
    Fetch arrivals for a stop from TfL API

    Args:
        stop_id: TfL stop point identifier (e.g., "490000123ABC")
        timeout: Request timeout in seconds (default: 5)

    Returns:
        List of arrival dictionaries sorted by timeToStation

    Raises:
        RequestException: On network errors
        Timeout: If request exceeds timeout
    """
```

### Error Handling Pattern
```python
try:
    buses = tfl_client.get_next_buses(stop_id, count)
    speak_output = format_bus_list(buses, "school")
except Timeout:
    speak_output = "Sorry, Transport for London isn't responding. Please try again"
except RequestException as e:
    logger.error(f"TfL API error: {e}")
    speak_output = "I can't reach the bus information service right now"
```

---

## Testing Strategy

### Test Framework
- **unittest** (Python standard library)
- **unittest.mock** for mocking external dependencies

### Test Structure
```
lambda/tests/
├── __init__.py
├── test_tfl_client.py       # TfL API client tests
└── test_bus_formatter.py    # Response formatting tests
```

### Running Tests
```bash
# Run all tests
make test

# Run with coverage
make coverage
# View coverage report at lambda/htmlcov/index.html

# Run specific test file
cd lambda && python -m unittest tests/test_tfl_client.py -v
```

### Test Coverage Requirements
- **Minimum:** 80% overall coverage
- **Target:** 90%+ for critical modules (`tfl_client.py`, `bus_formatter.py`)
- Excluded from coverage: `tests/`, `__pycache__/`, virtual environments

### Test Categories

**1. Unit Tests (`test_tfl_client.py`)**
- Mock TfL API responses using `unittest.mock`
- Test parsing of arrivals
- Test sorting by `timeToStation`
- Test filtering to N buses
- Test error conditions (timeout, 404, 500, rate limiting)

**2. Formatter Tests (`test_bus_formatter.py`)**
- Time formatting edge cases (0s, 59s, 60s, 119s, 3600s)
- Single bus formatting
- List formatting (1, 2, 3, 5 buses)
- Both directions formatting
- Empty list handling
- Grammar (singular/plural)

**3. Integration Tests (Manual)**
- Use `make local-test` to test Lambda locally with SAM
- Test all intents with sample events in `test-events/`

### Example Test Pattern
```python
import unittest
from unittest.mock import patch, MagicMock
from tfl_client import TfLClient

class TestTfLClient(unittest.TestCase):
    def setUp(self):
        self.client = TfLClient()

    @patch('tfl_client.requests.get')
    def test_get_arrivals_success(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"lineName": "25", "timeToStation": 120}
        ]
        mock_get.return_value = mock_response

        # Act
        result = self.client.get_arrivals("490000123ABC")

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["lineName"], "25")
```

---

## CI/CD Pipeline

### CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

1. **Test & Lint** (Matrix: Python 3.11 & 3.12)
   - Install dependencies
   - Ruff linting (syntax errors fail, warnings reported)
   - Format checking
   - Security scan (Bandit)
   - Unit tests
   - Coverage report (Python 3.11 only)
   - Upload to Codecov

2. **Dependency Check**
   - Scan dependencies for known vulnerabilities (Safety)
   - Continues on failure (informational)

3. **Skill Validation**
   - Validate `skill.json` syntax
   - Validate interaction model (`en-GB.json`)

### Deployment Pipeline (`.github/workflows/deploy.yml`)

**Triggers:**
- Manual workflow dispatch (workflow_dispatch)
- Push to `main` (production deployment)

**Environments:**
- **dev** - Development environment
- **prod** - Production environment

**Steps:**
1. Build SAM application
2. Deploy to AWS using SAM CLI
3. Run smoke tests (optional)

---

## Deployment

### Prerequisites
- AWS account with appropriate IAM permissions
- AWS CLI configured (`aws configure`)
- SAM CLI installed (`pip install aws-sam-cli`)

### Local Testing
```bash
# Test launch request
make local-test

# Test school buses intent
make local-test-school

# Build SAM application
make build

# Validate SAM template
make validate
```

### Deploy to Dev
```bash
make deploy-dev
```

**What happens:**
1. SAM builds Lambda deployment package
2. Creates/updates CloudFormation stack: `tfl-bus-checker-dev`
3. Provisions:
   - Lambda function (Python 3.11, 256MB, 10s timeout)
   - IAM execution role
   - CloudWatch log group
4. Outputs Lambda ARN for Alexa skill configuration

### Deploy to Prod
```bash
make deploy-prod
```

**Stack name:** `tfl-bus-checker-prod`
**Note:** Uses `--no-confirm-changeset` for automated deployments

### Environment Configuration

**Lambda Environment Variables:**
```yaml
# infrastructure/template.yaml
Environment:
  Variables:
    LOG_LEVEL: !Ref LogLevel        # INFO (prod) or DEBUG (dev)
    TFL_APP_ID: ""                  # Optional: TfL application ID
    TFL_APP_KEY: ""                 # Optional: TfL application key
```

### Viewing Logs
```bash
# Tail dev logs
make logs-dev

# Tail prod logs
make logs-prod

# View in AWS Console
# CloudWatch > Log Groups > /aws/lambda/tfl-bus-checker-<env>
```

---

## Common Tasks

### Adding a New Intent

1. **Update interaction model:** `skill-package/interactionModels/custom/en-GB.json`
   ```json
   {
     "name": "MyNewIntent",
     "slots": [...],
     "samples": ["utterance 1", "utterance 2"]
   }
   ```

2. **Create intent handler:** `lambda/lambda_function.py`
   ```python
   class MyNewIntentHandler(AbstractRequestHandler):
       def can_handle(self, handler_input: HandlerInput) -> bool:
           return is_intent_name("MyNewIntent")(handler_input)

       def handle(self, handler_input: HandlerInput) -> Response:
           # Implementation
           pass
   ```

3. **Register handler in `lambda_handler()`**
   ```python
   sb.add_request_handler(MyNewIntentHandler())
   ```

4. **Add tests:** `lambda/tests/test_lambda_function.py` (if not exists)

5. **Create test event:** `test-events/my-new-intent.json`

### Adding a New Bus Stop

1. **Find stop ID:**
   ```bash
   curl "https://api.tfl.gov.uk/StopPoint/Search/Highbury"
   # Look for "id" field in results
   ```

2. **Update config:** `lambda/config.py`
   ```python
   BUS_STOPS = {
       'school': {...},
       'station': {...},
       'new_stop': {
           'stopId': '490000789XYZ',
           'name': 'New Stop Name',
           'direction': 'northbound'
       }
   }
   ```

3. **Add new intent handler** (see "Adding a New Intent")

### Updating Dependencies

```bash
# Edit lambda/requirements.txt or requirements-dev.txt
# Then:
make install-dev

# Check for security vulnerabilities
make check-deps

# Run tests to verify compatibility
make test
```

### Running Code Quality Checks Locally

```bash
# Run all CI checks
make ci

# Individual checks
make lint          # Check for issues
make lint-fix      # Auto-fix issues
make format        # Check formatting
make format-fix    # Auto-format code
make security      # Security scan
make test          # Unit tests
make coverage      # Tests with coverage
```

### Debugging Lambda Locally

```bash
# 1. Build the function
make build

# 2. Invoke with test event
sam local invoke -e test-events/check-school-buses.json

# 3. Start local API endpoint (if needed)
sam local start-api

# 4. Test with curl
curl -X POST http://localhost:3000/
```

### Cleaning Build Artifacts

```bash
make clean
# Removes:
# - __pycache__/
# - *.pyc, *.pyo
# - .pytest_cache/
# - htmlcov/, .coverage, coverage.xml
# - deployment-package.zip, response.json
```

---

## File Reference

### Critical Files (Do Not Modify Without Care)

| File | Purpose | Notes |
|------|---------|-------|
| `lambda/config.py` | Stop IDs and constants | **Must update stop IDs before deployment** |
| `infrastructure/template.yaml` | AWS infrastructure definition | Changes affect deployed resources |
| `skill-package/skill.json` | Alexa skill manifest | Required for skill certification |
| `skill-package/interactionModels/custom/en-GB.json` | Voice interaction model | Defines all intents and utterances |
| `pyproject.toml` | Ruff and coverage config | Changes affect all developers |

### Lambda Function Files

| File | Purpose | Typical Changes |
|------|---------|-----------------|
| `lambda_function.py` | Main Lambda handler | Add/modify intent handlers |
| `tfl_client.py` | TfL API wrapper | Rarely modified |
| `bus_formatter.py` | Speech formatting | Modify response templates |
| `config.py` | Configuration | Update stop IDs, constants |
| `requirements.txt` | Production dependencies | Add new libraries |
| `requirements-dev.txt` | Dev dependencies | Add testing/linting tools |

### Configuration Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `.pre-commit-config.yaml` | Pre-commit hooks | Update tool versions |
| `pyproject.toml` | Ruff, coverage settings | Change code style rules |
| `Makefile` | Development commands | Add new commands |
| `.gitignore` | Git exclusions | Add new patterns |
| `.github/workflows/ci.yml` | CI pipeline | Modify test/lint steps |
| `.github/workflows/deploy.yml` | Deployment pipeline | Change deploy strategy |

### Documentation Files

| File | Audience | Content |
|------|----------|---------|
| `README.md` | Users/developers | Project overview, quick start |
| `CLAUDE.md` | **AI assistants** | **This file** |
| `SETUP.md` | New developers | Detailed setup instructions |
| `AWS_SETUP.md` | DevOps/deployment | AWS account configuration |
| `CI_CD_GUIDE.md` | DevOps | CI/CD pipeline documentation |
| `DEPLOYMENT_TROUBLESHOOTING.md` | Operators | Common deployment issues |
| `QUICKSTART.md` | Quick reference | Common commands |

---

## AI Assistant Guidelines

### General Principles

1. **Read Before Modifying**
   - Always read existing files before suggesting changes
   - Understand the current implementation patterns
   - Maintain consistency with existing code style

2. **Follow Established Conventions**
   - Use Ruff for formatting (do NOT suggest Black or isort)
   - Respect the 100-character line length
   - Follow import ordering (stdlib → third-party → local)
   - Use double quotes for strings

3. **Test-Driven Development**
   - Write tests for new functionality
   - Update existing tests when modifying behavior
   - Run `make test` before committing
   - Aim for 80%+ code coverage

4. **Security First**
   - Never commit secrets or API keys
   - Use environment variables for sensitive data
   - Run `make security` to check for vulnerabilities
   - Validate all user inputs (slot values)

5. **Error Handling**
   - Always handle TfL API errors gracefully
   - Provide user-friendly error messages
   - Log errors with context for debugging
   - Use appropriate exception types

### Common Pitfalls to Avoid

**❌ Don't:**
- Modify `config.py` without understanding stop ID format
- Add dependencies without updating `requirements.txt`
- Change SAM template without testing deployment
- Skip tests when adding new features
- Use print() for logging (use `logger` instead)
- Hardcode stop IDs in handler code (use `config.BUS_STOPS`)
- Forget to update interaction model when adding intents
- Use deprecated Alexa SDK patterns

**✅ Do:**
- Run `make ci` before committing
- Update tests when changing behavior
- Add docstrings to new functions
- Use type hints for function signatures
- Handle API timeouts (TfL can be slow)
- Test with actual TfL API responses
- Validate SAM template with `make validate`
- Check CloudWatch logs when debugging

### Code Review Checklist

When reviewing or suggesting changes:

- [ ] Code follows Ruff style guidelines
- [ ] All functions have docstrings
- [ ] Type hints are used for parameters and return values
- [ ] Error handling is comprehensive
- [ ] Tests are added/updated
- [ ] No secrets or API keys in code
- [ ] Logging is appropriate (not excessive, not missing)
- [ ] User-facing messages are clear and helpful
- [ ] Changes are documented in relevant files
- [ ] SAM template is valid (`make validate`)

### Suggested Workflow for Modifications

```
1. Read relevant files
   ├─> lambda/lambda_function.py (for intent handlers)
   ├─> lambda/tfl_client.py (for API interactions)
   └─> lambda/bus_formatter.py (for response formatting)

2. Understand current implementation
   └─> Check tests to understand expected behavior

3. Make changes
   ├─> Update code
   ├─> Update/add tests
   └─> Update documentation if needed

4. Validate changes
   ├─> make lint
   ├─> make format
   ├─> make test
   ├─> make security
   └─> make validate (if SAM template changed)

5. Test locally (if possible)
   └─> make local-test

6. Commit with clear message
   └─> git commit -m "Add support for X feature"
```

### Example Change Patterns

**Adding a new helper function:**
```python
# 1. Add to appropriate module (e.g., bus_formatter.py)
def format_route_number(route: str) -> str:
    """
    Format route number for speech output

    Args:
        route: Route identifier (e.g., "25", "N25")

    Returns:
        Formatted route for speech (e.g., "Route 25", "Night Route 25")
    """
    if route.startswith("N"):
        return f"Night Route {route[1:]}"
    return f"Route {route}"

# 2. Add tests (test_bus_formatter.py)
def test_format_route_number(self):
    self.assertEqual(format_route_number("25"), "Route 25")
    self.assertEqual(format_route_number("N25"), "Night Route 25")
```

**Modifying an intent handler:**
```python
# 1. Update handler in lambda_function.py
def handle(self, handler_input: HandlerInput) -> Response:
    # Original code...

    # New feature
    if some_condition:
        speak_output = "New behavior"

    return handler_input.response_builder.speak(speak_output).response

# 2. Update interaction model (skill-package/interactionModels/custom/en-GB.json)
# Add new sample utterances if needed

# 3. Add test event (test-events/new-scenario.json)

# 4. Update tests (if integration tests exist)
```

### Understanding the Request Flow

```
Alexa User → Alexa Service → Lambda Function → TfL API
                ↓                    ↑              ↓
           Intent/Slots          Handler        JSON Response
                                    ↓              ↓
                              bus_formatter    Parsed Arrivals
                                    ↓
                              Speech Output
                                    ↓
Alexa User ← Alexa Service ← Lambda Response
```

**Key Components:**
1. **Intent Recognition** - Alexa determines user intent from utterance
2. **Slot Extraction** - Alexa extracts values (e.g., count of buses)
3. **Lambda Invocation** - Alexa calls Lambda with intent + slots
4. **Handler Routing** - Lambda routes to appropriate intent handler
5. **API Call** - Handler calls TfL API via `tfl_client.py`
6. **Formatting** - Response formatted via `bus_formatter.py`
7. **Response** - Lambda returns speech text to Alexa
8. **Speech Output** - Alexa speaks response to user

### Debugging Tips

**Lambda function not responding:**
1. Check CloudWatch logs: `make logs-dev`
2. Verify Lambda timeout (should be 10s minimum)
3. Test locally: `make local-test`
4. Check TfL API is reachable: `curl https://api.tfl.gov.uk/StopPoint/<id>/Arrivals`

**Tests failing:**
1. Run with verbose: `cd lambda && python -m unittest tests/test_*.py -v`
2. Check if dependencies are installed: `make install-dev`
3. Verify Python version: `python --version` (should be 3.11+)

**Linting errors:**
1. Auto-fix: `make lint-fix && make format-fix`
2. Check specific rules: `cd lambda && ruff check . --show-source`
3. Ignore false positives: Add `# noqa: <rule>` comment

**Deployment fails:**
1. Validate template: `make validate`
2. Check AWS credentials: `aws sts get-caller-identity`
3. Review error in CloudFormation console
4. See `DEPLOYMENT_TROUBLESHOOTING.md`

### Resources for Further Learning

**Alexa Skills Kit:**
- [ASK Python SDK Docs](https://alexa-skills-kit-python-sdk.readthedocs.io/)
- [Alexa Design Guide](https://developer.amazon.com/en-US/docs/alexa/alexa-design/get-started.html)

**TfL API:**
- [TfL API Documentation](https://api.tfl.gov.uk/)
- [API Explorer](https://api-portal.tfl.gov.uk/)

**AWS Services:**
- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [Lambda Python Guide](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

**Testing & Quality:**
- [Python unittest Docs](https://docs.python.org/3/library/unittest.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

---

## Appendix: Quick Reference

### Essential Commands
```bash
make install-dev      # Install dependencies
make test             # Run tests
make lint             # Check code quality
make format-fix       # Auto-format code
make ci               # Run all checks
make local-test       # Test Lambda locally
make deploy-dev       # Deploy to dev
make logs-dev         # View logs
make clean            # Clean artifacts
```

### File Paths (for quick reference)
```
Lambda code:          lambda/lambda_function.py
TfL client:           lambda/tfl_client.py
Response formatting:  lambda/bus_formatter.py
Configuration:        lambda/config.py
Tests:                lambda/tests/
SAM template:         infrastructure/template.yaml
Interaction model:    skill-package/interactionModels/custom/en-GB.json
CI pipeline:          .github/workflows/ci.yml
```

### Environment Variables
```bash
LOG_LEVEL            # INFO or DEBUG
TFL_APP_ID           # Optional: TfL application ID
TFL_APP_KEY          # Optional: TfL application key
```

### Important URLs
```
TfL API Base:        https://api.tfl.gov.uk
Stop Search:         https://api.tfl.gov.uk/StopPoint/Search/{query}
Arrivals Endpoint:   https://api.tfl.gov.uk/StopPoint/{stopId}/Arrivals
```

---

**Document Version:** 1.0
**Compatible With:** Python 3.11+, AWS SAM CLI 1.x, Ruff 0.8.x

---

_This document is maintained for AI assistants. For human-readable documentation, see README.md_
