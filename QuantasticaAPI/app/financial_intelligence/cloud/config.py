import os
from typing import Literal, cast


CloudProvider = Literal["aws", "azure", "gcp"]
CLOUD = cast(CloudProvider, os.getenv("CLOUD_PROVIDER", "gcp"))
