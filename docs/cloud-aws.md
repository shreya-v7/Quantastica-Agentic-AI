# Running on AWS

Set `PLATFORM=aws`. The factory wires DynamoDB, Bedrock, SQS, and S3.

## Required env

| Variable | Purpose |
|---|---|
| `AWS_REGION` | Region for all AWS services |
| `DDB_TABLE_PREFIX` | Prefix for the DynamoDB tables |
| `SQS_QUEUE_URL` | Queue for run events |
| `S3_BUCKET` | Bucket for exported run reports |
| `BEDROCK_MODEL_ID` | For example `anthropic.claude-3-haiku-20240307-v1:0` |

The repository uses tables named `{DDB_TABLE_PREFIX}_portfolios`,
`{DDB_TABLE_PREFIX}_holdings`, `{DDB_TABLE_PREFIX}_transactions`,
`{DDB_TABLE_PREFIX}_findings`, and `{DDB_TABLE_PREFIX}_runs`.

## Least privilege IAM policy

Scope the role to one table prefix, one queue, one bucket, and one model. No FullAccess.
Replace `REGION`, `ACCOUNT`, `PREFIX`, `QUEUE`, and `BUCKET`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoTables",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT:table/PREFIX_*"
    },
    {
      "Sid": "Queue",
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:REGION:ACCOUNT:QUEUE"
    },
    {
      "Sid": "Bucket",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::BUCKET/*"
    },
    {
      "Sid": "Model",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "arn:aws:bedrock:REGION::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
    }
  ]
}
```

## Credentials

Use the ECS task role or Lambda execution role. Never use static keys in prod.

## Deploy

1. Backend container (`apps/server/Dockerfile`) to ECS Fargate, or Lambda plus API Gateway
   via Mangum.
2. Frontend: build with `VITE_API_URL` set, then
   `aws s3 sync apps/web/dist s3://<bucket>` behind CloudFront.
3. Verify `GET /api/platform`, then run the smoke test against the public URL.

## CI emulator

The DynamoDB implementation is tested in CI against dynamodb-local, selected by the
`DDB_ENDPOINT_URL` environment variable. `DynamoRepository.ensure_tables` creates the
tables for the emulator. In production the tables are provisioned by your infrastructure
and the role does not need `CreateTable`.
