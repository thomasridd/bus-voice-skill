# Deployment Troubleshooting Guide

Common issues and solutions for deploying the TfL Bus Checker to AWS Lambda.

## Template Not Found Error

### Error Message
```
Error: Template file not found at /home/runner/work/bus-voice-skill/bus-voice-skill/template.yml
```

### Cause
SAM is looking for the template in the wrong location.

### Solution
✅ **Fixed!** The deployment workflow now correctly specifies:
```bash
sam build --template infrastructure/template.yaml
```

### If Still Having Issues
1. Verify the template file exists at `infrastructure/template.yaml`
2. Check the file is committed to your repository
3. Ensure the workflow has the correct path

## AWS Credentials Error

### Error Message
```
Error: Unable to locate credentials
```

### Cause
GitHub Secrets are not configured or incorrectly named.

### Solution
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Verify these secrets exist:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. Check spelling is EXACT (case-sensitive)
4. See [AWS_SETUP.md](AWS_SETUP.md) for detailed setup

## Permission Denied Errors

### Error Message
```
User: arn:aws:iam::xxx:user/github-actions is not authorized to perform: lambda:CreateFunction
```

### Cause
IAM user lacks necessary permissions.

### Solution
1. Go to AWS Console → IAM → Users
2. Click your deployment user
3. Attach these policies:
   - `AWSLambda_FullAccess`
   - `IAMFullAccess`
   - `AmazonS3FullAccess`
   - `CloudFormationFullAccess`

Or use the custom policy from [AWS_SETUP.md](AWS_SETUP.md#option-b-custom-policy-more-secure---recommended).

## Stack Already Exists Error

### Error Message
```
Stack [tfl-bus-checker-dev] already exists
```

### Cause
You're trying to create a stack that already exists from a previous deployment.

### Solution
This is normal for updates! The workflow uses `sam deploy` which handles updates automatically.

If you want to start fresh:
```bash
# Delete the stack in AWS Console or via CLI
aws cloudformation delete-stack --stack-name tfl-bus-checker-dev --region eu-west-2

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name tfl-bus-checker-dev --region eu-west-2

# Then redeploy
```

## S3 Bucket Error

### Error Message
```
Unable to upload artifact ... Bucket does not exist
```

### Cause
SAM couldn't create an S3 bucket for deployment artifacts.

### Solution
The workflow now uses `--resolve-s3` which automatically creates the bucket.

If still having issues:
1. Check your IAM user has S3 permissions
2. Ensure the region is correct (default: eu-west-2)
3. Manually create a bucket: `aws-sam-cli-managed-default-samclisourcebucket-<random>`

## Lambda Function Not Working After Deployment

### Error Message
Lambda invokes but skill doesn't respond correctly.

### Causes & Solutions

#### 1. No Internet Access
**Symptom:** Can't reach TfL API

**Check:**
```bash
# View Lambda logs
aws logs tail /aws/lambda/tfl-bus-checker-dev --follow
```

**Solution:** Ensure Lambda is NOT in a VPC, or if in a VPC, has NAT gateway access.

#### 2. Environment Variables Not Set
**Symptom:** Config not loading

**Check:** Lambda → Configuration → Environment variables

**Solution:** Verify these are set:
- `ENVIRONMENT`: dev or prod
- `LOG_LEVEL`: INFO

#### 3. Code Issues
**Symptom:** Lambda errors in logs

**Solution:**
1. Run tests locally first: `make test`
2. Check CloudWatch Logs for stack traces
3. Test locally: `make local-test`

## Region Mismatch

### Error Message
```
The security token included in the request is invalid
```

### Cause
Credentials configured for different region than deployment.

### Solution
1. Check workflow uses same region: `.github/workflows/deploy.yml`
2. Verify IAM user can access the target region
3. Default region is `eu-west-2` (London)

To change region, update:
- `.github/workflows/deploy.yml` line 48
- `Makefile` deploy commands
- `samconfig.toml.example`

## Build Failures

### Error Message
```
Build Failed
Error: PythonPipBuilder:ResolveDependencies - {error details}
```

### Cause
Python dependency installation failed during SAM build.

### Solution
1. Check `lambda/requirements.txt` is valid
2. Verify all dependencies are available on PyPI
3. Check for platform-specific dependencies
4. Test build locally: `make build`

Common issues:
- Wrong Python version specified (should be 3.11)
- Dependencies requiring compilation (use pure Python alternatives)
- Network issues downloading packages

## Smoke Test Failures

### Error Message
```
Lambda invocation failed!
errorMessage: ...
```

### Cause
Lambda function has runtime errors.

### Solution
1. Check the error message in the deployment logs
2. View CloudWatch Logs:
   ```bash
   make logs-dev
   ```
3. Common causes:
   - Missing dependencies
   - Import errors
   - Configuration issues
   - TfL API unreachable

## CloudFormation Errors

### Error Message
```
CREATE_FAILED: Resource creation failed
```

### Solution
1. Go to AWS Console → CloudFormation
2. Find your stack: `tfl-bus-checker-dev`
3. Click Events tab
4. Look for the failed resource and reason
5. Common issues:
   - IAM role creation failed (check IAM permissions)
   - Lambda creation failed (check code/dependencies)
   - Resource name conflicts (change function name)

## GitHub Actions Workflow Not Triggering

### Symptoms
- Push to main but no deployment
- Manual trigger button missing

### Solutions

#### Workflow Not Visible
1. Ensure `.github/workflows/deploy.yml` is committed
2. Check file syntax: `cat .github/workflows/deploy.yml`
3. Refresh the Actions tab

#### Not Triggering on Push
The workflow only triggers when:
- Pushing to `main` branch
- Changes made to `lambda/**` or `infrastructure/**`

Force trigger: Use manual dispatch in GitHub Actions UI

## Local Deployment Issues

### Error: SAM CLI Not Found
```bash
sam: command not found
```

**Solution:**
```bash
# macOS
brew install aws-sam-cli

# Or follow: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
```

### Error: AWS CLI Not Configured
```bash
Unable to locate credentials
```

**Solution:**
```bash
# Configure AWS CLI
aws configure

# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: eu-west-2
# - Default output format: json
```

## Cost Concerns

### Unexpected Charges

**Common Causes:**
- CloudWatch Logs retention (free tier: 5GB/month)
- Lambda invocations beyond free tier (free: 1M requests/month)
- S3 storage for deployment artifacts (usually <$0.01/month)

**Solution:**
1. Set up AWS Budget alerts
2. Monitor AWS Cost Explorer
3. Check CloudWatch Logs are not excessive
4. Delete old deployment artifacts in S3

This skill should stay well within free tier limits.

## Getting More Help

### Check Logs
```bash
# From GitHub Actions
# 1. Go to Actions tab
# 2. Click the failed workflow
# 3. Expand each step to see output

# From AWS
make logs-dev    # Tail dev logs
make logs-prod   # Tail prod logs

# Or AWS Console
# CloudWatch → Log groups → /aws/lambda/tfl-bus-checker-dev
```

### Validate Template
```bash
make validate
```

### Test Locally
```bash
# Build
make build

# Test locally (requires Docker)
make local-test
```

### Manual Deployment
```bash
# Deploy to dev
make deploy-dev

# Deploy to prod
make deploy-prod
```

## Quick Fixes Checklist

When deployment fails, try these in order:

```
□ Check GitHub Secrets are set correctly
□ Verify IAM user has all required permissions
□ Ensure template file exists at infrastructure/template.yaml
□ Run `make ci` locally to catch code issues
□ Validate template: `make validate`
□ Check CloudWatch Logs for Lambda errors
□ Verify region matches across all configs
□ Try manual deployment: `make deploy-dev`
□ Delete stack and redeploy if corrupted
```

## Still Stuck?

1. Check [AWS_SETUP.md](AWS_SETUP.md) for detailed AWS configuration
2. Check [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for pipeline documentation
3. Review AWS CloudFormation Events in AWS Console
4. Check CloudWatch Logs for runtime errors
5. Test the Lambda function directly in AWS Console
