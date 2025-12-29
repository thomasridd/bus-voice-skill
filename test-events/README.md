# Test Events for Lambda Function

This directory contains test event payloads for testing the TfL Bus Checker Lambda function.

## Test Events

### launch-request.json
Simulates a user launching the skill ("Alexa, open Bus Times")
- **Expected Response:** Help message asking which buses to check

### check-school-buses.json
Simulates checking school buses ("Alexa, ask Bus Times for school buses")
- **Expected Response:** Next 3 buses to school
- **Note:** Requires TfL API to be accessible

## Using Test Events

### Via AWS Lambda Console

1. Go to AWS Lambda Console
2. Open your function (`tfl-bus-checker-dev`)
3. Click "Test" tab
4. Click "Create new test event"
5. Copy contents from one of the JSON files
6. Save and click "Test"

### Via AWS CLI

```bash
# Test launch request
aws lambda invoke \
  --function-name tfl-bus-checker-dev \
  --cli-binary-format raw-in-base64-out \
  --payload file://test-events/launch-request.json \
  response.json

# View response
cat response.json
```

### Via SAM Local

```bash
# Test locally with SAM
sam build --template infrastructure/template.yaml
sam local invoke \
  -t .aws-sam/build/template.yaml \
  -e test-events/launch-request.json
```

### Via Makefile

```bash
# Test launch request locally
make local-test
```

## Creating Custom Test Events

Use the existing files as templates. Key fields:

- `request.type`: LaunchRequest or IntentRequest
- `request.intent.name`: The intent name (for IntentRequest)
- `request.intent.slots`: Slot values
- `request.locale`: "en-GB" for UK English

## Test Event Structure

All Alexa requests follow this structure:

```json
{
  "version": "1.0",
  "session": { /* Session info */ },
  "context": { /* Device/system context */ },
  "request": { /* The actual request */ }
}
```

### Request Types

1. **LaunchRequest** - User opens skill without specific intent
2. **IntentRequest** - User invokes specific intent
3. **SessionEndedRequest** - Session ends

## Notes

- Test events use placeholder IDs (applicationId, userId, etc.)
- The Lambda function only cares about the `request` object
- Real Alexa requests will have actual IDs and tokens
- Timestamps are in ISO 8601 format
- Locale should match your skill's supported locales
