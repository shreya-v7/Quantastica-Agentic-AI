"""
Firestore data routes -- replaces the old Express.js server (endpoints/server.js).

Exposes the same API:
  GET /firestore/user/{phone}/{doc_name}
"""

from fastapi import APIRouter, HTTPException

from app.services.firebase_admin_svc import get_db

router = APIRouter()


@router.get("/test")
def firestore_test():
    """Health-check for the Firestore service."""
    return {"message": "Firestore endpoint is working!"}


@router.get("/user/{phone}/{doc_name}")
async def get_user_document(phone: str, doc_name: str):
    """
    Fetch a document from Firestore.

    Path mirrors the Express.js server:
        users/{phone}/data/{doc_name}/items/singleton
    """
    try:
        db = get_db()
        doc_ref = (
            db.collection("users")
            .document(phone)
            .collection("data")
            .document(doc_name)
            .collection("items")
            .document("singleton")
        )
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"data": doc.to_dict()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
