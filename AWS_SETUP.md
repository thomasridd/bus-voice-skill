# AWS Setup Guide for CI/CD Deployment

This guide walks you through setting up AWS credentials for automated deployment of your Lambda function.

## Overview

To deploy your Alexa skill to AWS Lambda via GitHub Actions, you need:
1. An AWS account
2. An IAM user with appropriate permissions
3. Access keys for that user
4. Those keys stored as GitHub Secrets

## Step 1: Create an IAM User

### 1.1 Log into AWS Console

1. Go to [https://console.aws.amazon.com](https://console.aws.amazon.com)
2. Sign in with your AWS account

### 1.2 Navigate to IAM

1. In the search bar at the top, type "IAM"
2. Click on "IAM" (Identity and Access Management)

### 1.3 Create a New User

1. Click **Users** in the left sidebar
2. Click **Create user** button
3. Enter a username: `github-actions-deploy` (or any name you prefer)
4. Click **Next**

## Step 2: Set Permissions

You have two options: use a managed policy (easier) or create a custom policy (more secure).

### Option A: Using AWS Managed Policies (Easier)

On the "Set permissions" page:

1. Select **Attach policies directly**
2. Search for and select these policies:
   - `AWSLambda_FullAccess`
   - `IAMFullAccess` (needed for SAM to create execution roles)
   - `AmazonS3FullAccess` (SAM uses S3 for deployments)
   - `CloudFormationFullAccess` (SAM uses CloudFormation)

3. Click **Next**
4. Review and click **Create user**

### Option B: Custom Policy (More Secure - Recommended)

1. Select **Attach policies directly**
2. Click **Create policy**
3. Click the **JSON** tab
4. Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudFormationAccess",
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResource",
        "cloudformation:DescribeStackResources",
        "cloudformation:GetTemplate",
        "cloudformation:ValidateTemplate",
        "cloudformation:CreateChangeSet",
        "cloudformation:DescribeChangeSet",
        "cloudformation:ExecuteChangeSet",
        "cloudformation:DeleteChangeSet"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetBucketLocation",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "LambdaAccess",
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:DeleteFunction",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:ListFunctions",
        "lambda:PublishVersion",
        "lambda:CreateAlias",
        "lambda:DeleteAlias",
        "lambda:UpdateAlias",
        "lambda:GetAlias",
        "lambda:InvokeFunction",
        "lambda:AddPermission",
        "lambda:RemovePermission"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMAccess",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRolePolicy",
        "iam:TagRole"
      ],
      "Resource": "*"
    },
    {
      "Sid": "LogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:FilterLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

5. Click **Next**
6. Name it: `GitHubActionsDeployPolicy`
7. Add description: "Policy for deploying Lambda via GitHub Actions"
8. Click **Create policy**
9. Go back to the user creation tab and refresh the policy list
10. Search for and select `GitHubActionsDeployPolicy`
11. Click **Next** and **Create user**

## Step 3: Create Access Keys

### 3.1 Generate Keys

1. After creating the user, click on the username
2. Click the **Security credentials** tab
3. Scroll down to **Access keys**
4. Click **Create access key**

### 3.2 Choose Use Case

1. Select **Third-party service** or **Command Line Interface (CLI)**
2. Check the confirmation box at the bottom
3. Click **Next**

### 3.3 Set Description

1. Add description: `GitHub Actions deployment for TfL Bus Checker`
2. Click **Create access key**

### 3.4 Save Your Keys

**IMPORTANT:** This is the ONLY time you'll see the secret access key!

You'll see:
- **Access key ID**: Something like `AKIAIOSFODNN7EXAMPLE`
- **Secret access key**: Something like `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

**DO NOT close this page yet!** Keep it open while you add them to GitHub.

## Step 4: Add Secrets to GitHub

### 4.1 Navigate to Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab (top right)
3. In the left sidebar, expand **Secrets and variables**
4. Click **Actions**

### 4.2 Add AWS_ACCESS_KEY_ID

1. Click **New repository secret**
2. Name: `AWS_ACCESS_KEY_ID`
3. Secret: Paste your **Access key ID** from AWS
4. Click **Add secret**

### 4.3 Add AWS_SECRET_ACCESS_KEY

1. Click **New repository secret** again
2. Name: `AWS_SECRET_ACCESS_KEY`
3. Secret: Paste your **Secret access key** from AWS
4. Click **Add secret**

### 4.4 Verify

You should now see both secrets listed (values are hidden):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**Now you can close the AWS access key page.**

## Step 5: Test Your Setup

### 5.1 Update SAM Template (if needed)

Make sure your `infrastructure/template.yaml` has the correct settings:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: TfL Bus Checker Alexa Skill

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - prod

Resources:
  TfLBusCheckerFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub tfl-bus-checker-${Environment}
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      CodeUri: ../lambda/
      Timeout: 10
      MemorySize: 256
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
```

### 5.2 Trigger a Deployment

**Option A: Manual Trigger (Recommended for First Deployment)**

1. Go to your GitHub repository
2. Click the **Actions** tab
3. Select **Deploy to AWS Lambda** workflow
4. Click **Run workflow** dropdown
5. Select environment: `dev`
6. Click **Run workflow**

**Option B: Automatic Trigger**

Push changes to the `main` branch:

```bash
git add .
git commit -m "Configure AWS deployment"
git push origin main
```

### 5.3 Monitor Deployment

1. Go to the **Actions** tab
2. Click on the running workflow
3. Watch the deployment steps
4. Check for any errors

### 5.4 Verify in AWS Console

After successful deployment:

1. Go to AWS Lambda console: [https://console.aws.amazon.com/lambda](https://console.aws.amazon.com/lambda)
2. Change region to **eu-west-2** (or your chosen region)
3. You should see: `tfl-bus-checker-dev`
4. Click on it to view details

## Security Best Practices

### 1. Rotate Access Keys Regularly

Rotate your access keys every 90 days:

1. Create a new access key in IAM
2. Update GitHub Secrets with new keys
3. Test deployment works
4. Delete old access key in IAM

### 2. Use Least Privilege Principle

- Don't use your root AWS account
- Only grant necessary permissions
- Use the custom policy (Option B) instead of managed policies when possible

### 3. Monitor Usage

1. In IAM console, check the user's **Last activity**
2. Review CloudTrail logs for suspicious activity
3. Enable AWS Budgets to avoid unexpected costs

### 4. Never Commit Credentials

- Never put AWS keys in code
- Never commit them to GitHub
- Use GitHub Secrets or AWS Secrets Manager
- Check `.gitignore` includes sensitive files

### 5. Enable MFA for AWS Account

Enable Multi-Factor Authentication on your root AWS account for extra security.

## Regional Considerations

The deployment defaults to **eu-west-2** (London). To change:

1. Edit `.github/workflows/deploy.yml`:
   ```yaml
   aws-region: eu-west-2  # Change this
   ```

2. Edit `infrastructure/template.yaml` if it specifies a region

3. Update `Makefile` regional references

Available regions for Lambda:
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `eu-west-2` (London)
- `ap-southeast-1` (Singapore)
- And many more...

## Troubleshooting

### Error: "User is not authorized to perform: lambda:CreateFunction"

**Fix:** The IAM user needs Lambda permissions. Add the `AWSLambda_FullAccess` policy or use the custom policy above.

### Error: "Could not assume role"

**Fix:** The IAM user needs `iam:PassRole` permission. This is included in the custom policy.

### Error: "Access Denied" when creating S3 bucket

**Fix:** Add S3 permissions to the IAM user.

### Error: GitHub Actions can't find secrets

**Fix:**
1. Verify secret names are EXACTLY: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
2. Check they're added to **Repository secrets** (not Environment secrets)
3. Refresh the Actions page

### Deployment succeeds but skill doesn't work

**Fix:**
1. Check Lambda function logs in CloudWatch
2. Verify the function has internet access (for TfL API)
3. Check environment variables are set correctly
4. Test the function directly in Lambda console

## Cost Considerations

### Free Tier

AWS Lambda includes:
- **1 million free requests per month**
- **400,000 GB-seconds of compute time per month**

Your skill should easily stay within free tier limits.

### Potential Costs

Small potential costs for:
- CloudFormation (usually free)
- S3 storage for deployment artifacts (pennies per month)
- CloudWatch Logs (free tier: 5GB/month)

**Typical monthly cost for this skill: $0-1**

## Next Steps

After AWS is set up:

1. ✅ Deploy to dev environment first
2. ✅ Test the Lambda function directly
3. ✅ Connect the Lambda to your Alexa skill
4. ✅ Test the full Alexa skill
5. ✅ Deploy to prod when ready

## Connecting Lambda to Alexa Skill

After deploying your Lambda:

1. Copy the Lambda ARN from AWS Console (looks like: `arn:aws:lambda:eu-west-2:123456789:function:tfl-bus-checker-dev`)
2. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
3. Open your skill
4. Go to **Endpoint**
5. Select **AWS Lambda ARN**
6. Paste your Lambda ARN
7. Click **Save Endpoints**

Now your skill is connected and ready to test!

## Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Alexa Skills Kit Documentation](https://developer.amazon.com/docs/ask-overviews/build-skills-with-the-alexa-skills-kit.html)
