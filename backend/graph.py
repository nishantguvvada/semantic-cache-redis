from typing import Dict, Any, Literal, Annotated
from typing_extensions import TypedDict
from operator import add
from langgraph.graph import StateGraph
from model import llm
from cache import rcache
import time

class WorkflowState(TypedDict):

    original_question: str
    cached_response: str
    cache_hit: bool
    response: str
    metadata: Annotated[list[str], add]

def check_cache_node(state: WorkflowState):
    print("checking cache")
    response = rcache.cache.check(prompt=state["original_question"], num_results=1)
    cache_flag = False
    output = ""
    if len(response) > 0:
        print("cache hit")
        cache_flag = True
        output = response[0]["response"]
    else:
        print("cache miss")
        cache_flag = False
    return { "cached_response": output, "cache_hit": cache_flag, "metadata": [f"check_cache_node: {time.perf_counter()}"] }

def knowledge_base_node(state: WorkflowState):
    print("checking knowledge base")
    time.sleep(3)
    return { "metadata": [f"knowledge_base_node: {time.perf_counter()}"] }

def synthesize_node(state: WorkflowState):
    print("synthesizing output")
    query_input = ""

    if state["cache_hit"]:
        response = state["cached_response"]
    else:
        query_input = f"Based on the user question: {state["original_question"]}\n\n generate a conversational response."
        response = llm.invoke(query_input)
    
    return { "response": response, "metadata": [f"synthesize_node: {time.perf_counter()}"] }

def route(state: WorkflowState) -> Literal["synthesize_node", "knowledge_base_node"]:
    if state["cache_hit"]:
        print("routing to synthesize_node")
        return "synthesize_node"
    else:
        print("routing to knowledge_base_node")
        return "knowledge_base_node"


graph = StateGraph(WorkflowState)
graph.add_node("check_cache_node", check_cache_node)
graph.add_node("knowledge_base_node", knowledge_base_node)
graph.add_node("synthesize_node", synthesize_node)
graph.set_entry_point("check_cache_node")

graph.add_conditional_edges("check_cache_node", route, { "knowledge_base_node": "knowledge_base_node", "synthesize_node": "synthesize_node" })

compiled_graph = graph.compile()

output = compiled_graph.invoke({"original_question":"Talk about VPN"})
print(output)