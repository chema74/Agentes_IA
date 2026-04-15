from __future__ import annotations

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    END = "END"
    START = "START"
    StateGraph = None

from services.orchestration.psychological_orchestrator import ORCHESTRATOR, OrchestratorInput


def build_hub_and_spoke_graph():
    if StateGraph is None:
        return None

    class GraphState(dict):
        pass

    graph = StateGraph(GraphState)

    def orchestrator_node(state: GraphState) -> GraphState:
        payload = OrchestratorInput(user_id=state["user_id"], message=state["message"])
        result = ORCHESTRATOR.invoke(payload)
        return {"result": result.model_dump(mode="json")}

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", END)
    return graph.compile()
