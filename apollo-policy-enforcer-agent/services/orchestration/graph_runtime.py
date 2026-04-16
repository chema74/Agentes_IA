from __future__ import annotations

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    END = "END"
    START = "START"
    StateGraph = None

from services.orchestration.policy_orchestrator import ORCHESTRATOR, OrchestratorInput


def build_hub_and_spoke_graph():
    if StateGraph is None:
        return None

    class GraphState(dict):
        pass

    graph = StateGraph(GraphState)

    def orchestrator_node(state: GraphState) -> GraphState:
        result = ORCHESTRATOR.enforce(
            OrchestratorInput(
                request_text=state["request_text"],
                actor_id=state["actor_id"],
                target_resource=state["target_resource"],
                context=state.get("context", {}),
            )
        )
        return {"result": result.model_dump(mode="json")}

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", END)
    return graph.compile()
