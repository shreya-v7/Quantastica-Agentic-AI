from app.financial_intelligence.cloud import aws, azure, gcp
from app.financial_intelligence.cloud.base import CloudServices
from app.financial_intelligence.cloud.config import CLOUD

cloud: CloudServices = aws if CLOUD == "aws" else azure if CLOUD == "azure" else gcp
