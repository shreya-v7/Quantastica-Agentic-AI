from app.agents.orchestrator import PIPELINE


def test_langgraph_pipeline_order():
    assert PIPELINE == (
        "planner",
        "researcher",
        "retrieve",
        "risk",
        "insight",
        "summarizer",
    )
