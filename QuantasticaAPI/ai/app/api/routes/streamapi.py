from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import requests

app = FastAPI()

def stream_batches(url, payload):
    try:
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_lines():
                if chunk:  # Filter out keep-alive new lines
                    yield chunk.decode('utf-8') + "\n"
    except requests.exceptions.RequestException as e:
        yield f"Error: {str(e)}\n"

@app.post("/stream-batches")
def stream_post_batches(url:str, payload: dict):
    return StreamingResponse(stream_batches(url, payload), media_type="application/json")