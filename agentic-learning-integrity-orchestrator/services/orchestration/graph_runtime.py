from __future__ import annotations

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    END = "END"
    START = "START"
    StateGraph = None

from services.orchestration.learning_integrity_orchestrator import ORCHESTRATOR, OrchestratorInput


def build_hub_and_spoke_graph():
    if StateGraph is None:
        return None

    class GraphState(dict):
        pass

    graph = StateGraph(GraphState)

    def orchestrator_node(state: GraphState) -> GraphState:
        payload = OrchestratorInput(**state)
        result = ORCHESTRATOR.invoke(payload)
        return {"result": result.model_dump(mode="json")}

    graph.add_node("learning_integrity_orchestrator", orchestrator_node)
    graph.add_edge(START, "learning_integrity_orchestrator")
    graph.add_edge("learning_integrity_orchestrator", END)
    return graph.compile()
