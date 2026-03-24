"""
Firebase Admin SDK -- singleton initialisation from .env credentials.

No separate JSON key file needed. All fields come from the single .env file
via app.config.settings.
"""

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

_app = None
_db = None


def _init():
    global _app, _db
    if _app is None:
        cred = credentials.Certificate(settings.service_account_info)
        _app = firebase_admin.initialize_app(cred)
        _db = firestore.client()


def get_db():
    """Return the Firestore client (initialises on first call)."""
    _init()
    return _db
