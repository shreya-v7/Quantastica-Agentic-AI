from app.financial_intelligence.cloud.index import cloud
from app.financial_intelligence.core.types import FinancialSnapshot


async def ask_financial_question(question: str, snapshot: FinancialSnapshot) -> str:
    prompt = (
        "Analyze this user financial snapshot and answer the question in a concise, "
        "actionable way. Include 2-3 practical recommendations."
    )
    context = {"question": question, "snapshot": snapshot.model_dump()}
    return await cloud.ai(prompt, context=context)
