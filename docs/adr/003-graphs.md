# ADR 003: Two LangGraphs

Status: accepted

The explain pipeline stays a linear six-step StateGraph (Planner through Summarizer).
Ingest is a second graph that routes by document kind, validates Pydantic extracts, and
pauses on low confidence. Checkpoints are `graph_checkpoints` rows locally. PostgresSaver
is the production target, not a second control-flow library.
