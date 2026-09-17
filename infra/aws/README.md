# Running on AWS (portable)

The production *target* is GCP `asia-south1`. See
[adr/007-residency.md](adr/007-residency.md). This tree keeps Bedrock, S3, and
SQS adapters so a Mumbai AWS port is a factory swap.

Do not treat this folder as applied infrastructure. There is no AWS account
binding in CI.
