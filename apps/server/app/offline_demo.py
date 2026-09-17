"""Local-only offline proof desk. No database, model, credentials, or cloud services."""
from __future__ import annotations

import argparse
import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from quantastica_kernel.api import calculate, canonical, replay

from app.exceptions.fixtures import demo_books
from app.ingest.extractors import MockVLM, parse_form16
from app.speech.provider import MockSpeech

TIERS = {"small": 10, "medium": 1_000, "large": 100_000}


def household(index: int, seed: int = 42):
    books = demo_books()
    if index < 2:
        return books[index]
    rng = random.Random(f"{seed}:{index}")
    book = books[index % 2].model_copy(deep=True)
    book.household_id = f"hh_synthetic_{index:06d}"
    book.household_name = f"Synthetic household {index:06d}"
    for i, lot in enumerate(book.lots):
        lot.id = f"{book.household_id}_lot_{i}"
        lot.quantity = rng.randint(1, 2000)
    return book


def proof(index: int, seed: int) -> dict:
    book = household(index, seed)
    receipt = calculate("exceptions", {"book": book.model_dump(mode="json")})
    replay(receipt)
    return {
        "name": book.household_name, "synthetic": True, "receipt": receipt,
        "overview": {
            "total_market": book.total_market,
            "holdings": [
                {"symbol": lot.symbol, "name": lot.name, "sector": lot.sector,
                 "quantity": lot.quantity, "market_value": lot.market_value}
                for lot in book.lots
            ],
        },
    }


PAGE_PATH = Path(__file__).with_name("offline_demo.html")


def serve(tier: str, seed: int, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            status = 200
            content_type = "application/json"
            try:
                if url.path == "/":
                    content_type = "text/html; charset=utf-8"
                    body = PAGE_PATH.read_bytes()
                elif url.path == "/proof":
                    index = int(parse_qs(url.query).get("index", ["0"])[0])
                    if not 0 <= index < TIERS[tier]:
                        raise ValueError(f"index must be between 0 and {TIERS[tier] - 1}")
                    body = canonical(proof(index, seed)).encode()
                elif url.path == "/mock":
                    speech = MockSpeech()
                    extraction = parse_form16(MockVLM().extract("form16", None))
                    body = canonical({
                        "mock": True, "form16": extraction.model_dump(mode="json"),
                        "transcript": speech.transcribe("text:What fired for Mehta"),
                        "audio": speech.speak("Offline mock speech. Informational only."),
                    }).encode()
                else:
                    status, body = 404, b'{"error":"Not found"}'
            except (ValueError, KeyError) as exc:
                status, body = 400, json.dumps({"error": str(exc)}).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    print(f"Offline proof desk: http://127.0.0.1:{port} | {tier} | seed={seed}", flush=True)
    with HTTPServer(("127.0.0.1", port), Handler) as server:
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=TIERS, default="small")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        for index in (0, 1, TIERS[args.tier] - 1):
            proof(index, args.seed)
        parse_form16(MockVLM().extract("form16", None))
        assert MockSpeech().transcribe("text:hello") == "hello"
        assert MockSpeech().speak("hello") == "mock-audio:hello"
        print("PASS offline books, receipt replay, mock VLM, STT and TTS")
    else:
        serve(args.tier, args.seed, args.port)


if __name__ == "__main__":
    main()
