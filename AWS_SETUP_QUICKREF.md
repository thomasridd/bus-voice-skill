# AWS Setup Quick Reference

Visual checklist for setting up AWS deployment. For detailed instructions, see [AWS_SETUP.md](AWS_SETUP.md).

## Quick Checklist

```
□ Step 1: Create IAM User
  └─ Go to AWS Console → IAM → Users → Create user
  └─ Name: github-actions-deploy

□ Step 2: Attach Permissions
  └─ Option A: Attach managed policies
     • AWSLambda_FullAccess
     • IAMFullAccess
     • AmazonS3FullAccess
     • CloudFormationFullAccess
  └─ Option B: Create custom policy (more secure)
     • Use JSON from AWS_SETUP.md

□ Step 3: Create Access Keys
  └─ User → Security credentials → Create access key
  └─ Choose: Third-party service or CLI
  └─ SAVE BOTH KEYS (you won't see secret again!)
     • Access key ID: AKIA...
     • Secret access key: wJal...

□ Step 4: Add to GitHub Secrets
  └─ GitHub repo → Settings → Secrets and variables → Actions
  └─ New repository secret → AWS_ACCESS_KEY_ID
  └─ New repository secret → AWS_SECRET_ACCESS_KEY

□ Step 5: Test Deployment
  └─ GitHub → Actions → Deploy to AWS Lambda → Run workflow
  └─ Select: dev environment
  └─ Watch it deploy!
```

## IAM Policy (Copy-Paste Ready)

For Step 2, Option B (custom policy):

<details>
<summary>Click to expand JSON policy</summary>

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

</details>

## GitHub Secrets Format

```
Name: AWS_ACCESS_KEY_ID
Value: AKIAIOSFODNN7EXAMPLE
       ^^^^^^^^^^^^^^^^^^^^^ (paste your key here)

Name: AWS_SECRET_ACCESS_KEY
Value: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ (paste your secret here)
```

## Common Issues

| Issue | Fix |
|-------|-----|
| Can't find IAM in AWS Console | Search "IAM" in top search bar |
| "Not authorized to perform: lambda:CreateFunction" | User needs Lambda permissions |
| Secret access key not showing | You can only see it once - create new key if lost |
| GitHub Actions can't find secrets | Check spelling: `AWS_ACCESS_KEY_ID` (exact) |
| Deployment works but skill doesn't | Check Lambda logs in CloudWatch |

## Security Reminder

- ❌ Never commit AWS keys to code
- ❌ Never share keys publicly
- ✅ Rotate keys every 90 days
- ✅ Use least privilege (custom policy)
- ✅ Enable MFA on AWS root account

## After Setup

1. Deploy to `dev` first
2. Test in AWS Lambda console
3. Connect Lambda ARN to Alexa skill
4. Test end-to-end
5. Deploy to `prod` when ready

## Need Help?

See [AWS_SETUP.md](AWS_SETUP.md) for:
- Detailed step-by-step instructions with screenshots
- Troubleshooting guide
- Security best practices
- Cost information
- Regional configuration
