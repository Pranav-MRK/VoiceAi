
from langgraph.graph import StateGraph, START, END

from app.rag.graph.state import SamvadState
from app.rag.graph.nodes import (
    retrieve_node,
    context_node,
    generate_node,
)

def create_workflow():
    graph = StateGraph(SamvadState)

    # nodes 
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("context",context_node)
    graph.add_node("generate",generate_node)

    #  add edges

    graph.add_edge(START,"retrieve")
    graph.add_edge("retrieve","context")
    graph.add_edge("context","generate")
    graph.add_edge("generate",END)

    return graph.compile()

rag_workflow = create_workflow()