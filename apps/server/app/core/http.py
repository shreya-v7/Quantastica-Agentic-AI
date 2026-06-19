"""ETag support for cacheable GETs (Phase K).

A weak ETag is derived from the response payload. When the client sends a matching
`If-None-Match`, we answer 304 with no body. Only safe, non-money, non-auth reads use this.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from app.core.envelope import success


def etag_for(data: Any) -> str:
    encoded = jsonable_encoder(data)
    blob = json.dumps(encoded, sort_keys=True, default=str)
    return 'W/"' + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32] + '"'


def etag_json(request: Request, data: Any) -> Response:
    tag = etag_for(data)
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304, headers={"ETag": tag})
    response = JSONResponse(content=jsonable_encoder(success(data)))
    response.headers["ETag"] = tag
    return response
