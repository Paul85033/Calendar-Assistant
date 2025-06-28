from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict, Any
from app.agent.nodes import nodes  


class TimeSlot(TypedDict):
    start: str
    end: str

class AgentState(TypedDict, total=False):
    user_input: str
    access_token: str
    intent: str
    requested_datetime: str
    busy_slots: List[Dict[str, Any]]
    suggested_slots: List[TimeSlot]
    bot_reply: str


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "")
    if intent == "intent:book":
        return "extract_datetime"
    return "confirm_booking"  


def run_agent(initial_state: dict) -> dict:
    graph = StateGraph(state_schema=AgentState)
    graph.add_node("detect_intent", nodes["intent"])
    graph.add_node("extract_datetime", nodes["extract_datetime"])
    graph.add_node("check_calendar", nodes["check_calendar"])
    graph.add_node("suggest_slots", nodes["suggest_slots"])
    graph.add_node("confirm_booking", nodes["confirm_booking"])

    graph.set_entry_point("detect_intent")
    graph.add_conditional_edges("detect_intent", route_by_intent, {
        "extract_datetime": "extract_datetime",
        "confirm_booking": "confirm_booking"
    })

    graph.add_edge("extract_datetime", "check_calendar")
    graph.add_edge("check_calendar", "suggest_slots")
    graph.add_edge("suggest_slots", "confirm_booking")
    graph.set_finish_point("confirm_booking")

    executable_graph = graph.compile()
    return executable_graph.invoke(initial_state)
