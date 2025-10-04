from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from services.agent.models.models import SystemState
from services.agent.tools import tools_list
from services.agent.nodes.entry import entry_node
from services.agent.nodes.parsing import (
    parse_customer_node,
    parse_project_name_node,
    parse_project_type_node,
    parse_project_description_node,
    parse_budget_node,
    parse_budget_analysis_node,
)
from services.agent.nodes.project_flow import (
    project_type_node,
    detalize_node,
    check_details_node,
    correcting_node,
    budget_node,
    budget_analysis_node,
    budget_correcting_node,
    mid_node,
)
from services.agent.nodes.final import final_node
from services.agent.routing.conditions import (
    route_after_input,
    route_before_tools,
)


def build_graph():
    graph = StateGraph(SystemState)

    tool_node = ToolNode(tools=tools_list)

    graph.add_node("entry", entry_node)
    graph.add_node("parse_customer", parse_customer_node)
    graph.add_node("parse_project_name", parse_project_name_node)
    graph.add_node("project_type", project_type_node)
    graph.add_node("parse_project_type", parse_project_type_node)
    graph.add_node("parse_project_description", parse_project_description_node)
    graph.add_node("detalize", detalize_node)
    graph.add_node("check_details", check_details_node)
    graph.add_node("correcting", correcting_node)
    graph.add_node("final", final_node)
    graph.add_node("mid", mid_node)
    graph.add_node("tools_after_detalize", tool_node)
    graph.add_node("budget", budget_node)
    graph.add_node("parse_budget", parse_budget_node)
    graph.add_node("budget_analysis", budget_analysis_node)
    graph.add_node("parse_budget_analysis", parse_budget_analysis_node)
    graph.add_node("budget_correcting", budget_correcting_node)
    graph.add_node("tools_after_budget", tool_node)

    graph.add_edge(START, "entry")
    graph.add_edge("entry", "parse_customer")
    graph.add_edge("parse_customer", "parse_project_name")
    graph.add_edge("parse_project_name", "project_type")
    graph.add_edge("project_type", "parse_project_type")
    graph.add_edge("parse_project_type", "parse_project_description")
    graph.add_edge("parse_project_description", "detalize")

    graph.add_conditional_edges(
        "detalize",
        route_before_tools,
        {"continue": "tools_after_detalize", "end": "mid"},
    )
    graph.add_edge("tools_after_detalize", "detalize")
    graph.add_edge("mid", "check_details")

    graph.add_conditional_edges(
        "check_details", route_after_input, {"continue": "budget", "back": "correcting"}
    )
    graph.add_edge("correcting", "detalize")

    graph.add_edge("budget", "parse_budget")
    graph.add_edge("parse_budget", "budget_analysis")
    graph.add_conditional_edges(
        "budget_analysis",
        route_before_tools,
        {"continue": "tools_after_budget", "end": "parse_budget_analysis"},
    )
    graph.add_edge("tools_after_budget", "budget_analysis")

    graph.add_conditional_edges(
        "parse_budget_analysis",
        route_after_input,
        {"continue": "final", "back": "budget_correcting"},
    )
    graph.add_edge("budget_correcting", "correcting")
    graph.add_edge("final", END)

    memory = MemorySaver()
    return graph.compile(
        checkpointer=memory,
        interrupt_after=[
            "entry",
            "project_type",
            "mid",
            "budget",
            "parse_budget_analysis",
        ],
    )
