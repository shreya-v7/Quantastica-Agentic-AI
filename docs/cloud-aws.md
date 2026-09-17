# Running on AWS

Production target is **Mumbai `ap-south-1`**. See [system-design.md](system-design.md).

Set `PLATFORM=aws`. The factory today wires **Postgres**, Bedrock, Redis, and S3.
This file previously claimed DynamoDB as the book of record. That is stale. The
book is Postgres + pgvector everywhere. EventBridge and SQS are the **target**
bus for exception recompute; they are not wired yet.

## Required env

| Variable | Purpose |
|---|---|
| `AWS_REGION` | Use `ap-south-1` in production |
| `S3_BUCKET` | Exported run reports and ingest artifacts |
| `BEDROCK_MODEL_ID` | In-country Claude id from the Bedrock console |

The book is RDS (or local) Postgres. Do not provision DynamoDB.

## Least privilege IAM (target)

Scope the role to one bucket, one Bedrock model, and later one SQS queue / EventBridge
bus. No FullAccess. RDS access is via the instance security group and IAM DB auth,
not DynamoDB.

```json
{
  "Version": "2012-10-17",
  "Statement": [
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
      "Resource": "arn:aws:bedrock:ap-south-1::foundation-model/*"
    }
  ]
}
```

Add SQS/EventBridge actions only when the outbox relay is deployed.

## Credentials

Use the ECS task role. Never use static keys in prod.

## Deploy

1. Backend container (`apps/server/Dockerfile`) to ECS Fargate in `ap-south-1`.
2. Frontend: build with `VITE_API_URL` set, then
   `aws s3 sync apps/web/dist s3://<bucket>` behind CloudFront.
3. Verify `GET /api/platform`, then run the smoke test against the public URL.

App Runner is Mumbai-only. Prefer Fargate (Mumbai and Hyderabad).
