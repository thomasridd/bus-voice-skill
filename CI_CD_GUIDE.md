# CI/CD Pipeline Guide

This guide explains how to use the GitHub Actions CI/CD pipeline for the TfL Bus Checker Alexa Skill.

## Overview

The project includes two main workflows:

1. **CI Pipeline** (`.github/workflows/ci.yml`) - Runs on every push and pull request
2. **CD Pipeline** (`.github/workflows/deploy.yml`) - Deploys to AWS Lambda

## CI Pipeline

### What It Does

The CI pipeline automatically runs on:
- Pushes to `main` or `develop` branches
- All pull requests

It performs the following checks:

1. **Multi-version Testing** - Tests against Python 3.11 and 3.12
2. **Code Linting** - Uses Ruff to check code quality
3. **Format Checking** - Ensures consistent code formatting
4. **Security Scanning** - Uses Bandit to detect security issues
5. **Unit Tests** - Runs all tests in the `lambda/tests/` directory
6. **Code Coverage** - Tracks test coverage and uploads to Codecov
7. **Dependency Security** - Checks for known vulnerabilities in dependencies
8. **Skill Validation** - Validates Alexa skill JSON files

### Running CI Checks Locally

Before pushing code, you can run the same checks locally:

#### Install development dependencies

```bash
cd lambda
pip install -r requirements.txt -r requirements-dev.txt
```

#### Run linting

```bash
# Check for errors
ruff check .

# Check formatting
ruff format --check .

# Auto-fix issues
ruff check . --fix
ruff format .
```

#### Run security scan

```bash
bandit -r . -ll -x ./tests
```

#### Run tests

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run with coverage
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report
coverage html  # Creates htmlcov/index.html
```

#### Check dependencies

```bash
safety check
```

## CD Pipeline (Deployment)

### Prerequisites

Before you can deploy to AWS Lambda, you need to:

1. **Set up AWS credentials** in GitHub Secrets:
   - **📖 See [AWS_SETUP.md](AWS_SETUP.md) for complete step-by-step instructions**
   - Summary:
     - Create an IAM user in AWS Console
     - Generate access keys for that user
     - Add them to GitHub repository secrets:
       - `AWS_ACCESS_KEY_ID`
       - `AWS_SECRET_ACCESS_KEY`

2. **Install AWS SAM CLI** (for local testing):
   ```bash
   # macOS
   brew install aws-sam-cli

   # Or follow: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
   ```

3. **Update SAM Template** (if needed):
   - Edit `infrastructure/template.yaml` to match your AWS setup
   - Ensure the region is correct (default: eu-west-2)

### Deployment Methods

#### Method 1: Manual Deployment (Recommended)

Trigger deployment manually through GitHub Actions:

1. Go to Actions tab in your GitHub repository
2. Select "Deploy to AWS Lambda" workflow
3. Click "Run workflow"
4. Choose environment (`dev` or `prod`)
5. Click "Run workflow" button

#### Method 2: Automatic Deployment

The workflow also deploys automatically when:
- You push to the `main` branch
- Changes are made to `lambda/` or `infrastructure/` directories

This defaults to the `dev` environment.

### Deployment Process

The deployment pipeline:

1. ✅ Checks out your code
2. ✅ Sets up Python 3.11
3. ✅ Configures AWS credentials
4. ✅ Installs AWS SAM CLI
5. ✅ Installs Lambda dependencies
6. ✅ Creates deployment package (excludes tests)
7. ✅ Deploys using SAM
8. ✅ Runs smoke test
9. ✅ Creates deployment summary

### Environments

The pipeline supports two environments:

- **dev** - Development/testing environment
- **prod** - Production environment

Each environment creates a separate CloudFormation stack:
- `tfl-bus-checker-dev`
- `tfl-bus-checker-prod`

### Verifying Deployment

After deployment:

1. Check the GitHub Actions summary for deployment details
2. View the Lambda function in AWS Console
3. Test the Alexa skill in the Alexa Developer Console

## GitHub Actions Status Badges

Add these badges to your README to show build status:

```markdown
![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI%20Pipeline/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Deploy%20to%20AWS%20Lambda/badge.svg)
```

## Troubleshooting

### CI Pipeline Issues

**Tests failing locally but passing in CI (or vice versa)**
- Ensure you're using the same Python version (3.11)
- Check that all dependencies are installed: `pip install -r requirements.txt -r requirements-dev.txt`

**Linting errors**
- Run `ruff check . --fix` to auto-fix many issues
- Run `ruff format .` to fix formatting

**Coverage too low**
- Add more unit tests in `lambda/tests/`
- Aim for at least 80% coverage

### CD Pipeline Issues

**Deployment fails with AWS credentials error**
- Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in GitHub Secrets
- Ensure the IAM user has necessary permissions (Lambda, CloudFormation, IAM, S3)

**SAM deployment fails**
- Check `infrastructure/template.yaml` is valid
- Verify the Lambda runtime matches your code (Python 3.11)
- Check CloudFormation stack events in AWS Console

**Smoke test fails**
- Check Lambda function logs in CloudWatch
- Verify the function has internet access (for TfL API)
- Ensure environment variables are set correctly

## Best Practices

1. **Always run tests locally** before pushing
2. **Create pull requests** for changes - CI will run automatically
3. **Review CI results** before merging PRs
4. **Deploy to dev first** - Test thoroughly before deploying to prod
5. **Monitor CloudWatch Logs** after deployment
6. **Keep dependencies updated** - Check for security vulnerabilities regularly

## Advanced Configuration

### Customizing the CI Pipeline

Edit `.github/workflows/ci.yml` to:
- Add more Python versions to test
- Enable/disable specific checks
- Add custom test commands
- Integrate additional tools

### Customizing the CD Pipeline

Edit `.github/workflows/deploy.yml` to:
- Change the AWS region
- Add deployment notifications (Slack, email)
- Run integration tests after deployment
- Add rollback capability

### Scheduled Dependency Checks

Add a scheduled workflow to check dependencies weekly:

```yaml
# .github/workflows/security-scan.yml
name: Weekly Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
  workflow_dispatch:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install safety
      - run: |
          pip install -r lambda/requirements.txt
          safety check --json
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## Getting Help

If you encounter issues:

1. Check the Actions tab for detailed error logs
2. Review this guide's troubleshooting section
3. Check AWS CloudWatch Logs for Lambda errors
4. Consult the AWS SAM CLI documentation
