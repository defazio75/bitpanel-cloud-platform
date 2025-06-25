from fastapi import APIRouter, HTTPException
from utils.firebase_db import get_document  # We'll assume you have a helper to get a doc from Firebase

router = APIRouter()

@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    try:
        # Path in Firebase: users/{user_id}/live/balances/portfolio_snapshot
        doc_path = f"users/{user_id}/live/balances/portfolio_snapshot"
        
        # Fetch document from Firebase
        portfolio_snapshot = get_document(doc_path)
        
        if not portfolio_snapshot:
            raise HTTPException(status_code=404, detail="Portfolio snapshot not found")

        # Return the portfolio snapshot data as-is
        return portfolio_snapshot

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))