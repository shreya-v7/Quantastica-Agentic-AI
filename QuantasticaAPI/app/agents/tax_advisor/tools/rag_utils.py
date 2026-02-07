def retrieve_tax_answer(query: str) -> str:
    # Placeholder RAG tool (Replace with real Vertex AI Search or FAISS)
    sample_knowledge = {
        "80C": "Section 80C allows deductions up to ₹1.5 lakh under the old regime.",
        "HRA": "HRA deduction is only available under the old regime, not new (115BAC).",
        "new regime": "The new regime offers lower slab rates but removes most deductions."
    }
    for k in sample_knowledge:
        if k in query.lower():
            return sample_knowledge[k]
    return "Sorry, I couldn't find a specific tax rule matching your query."
