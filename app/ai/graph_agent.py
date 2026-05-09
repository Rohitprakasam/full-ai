"""Graph Intelligence Agent — AI reasoning over Neo4j relationship graphs."""
from app.ai.openclaw.agent_runner import run_agent

PROMPT = """You are a forensic graph intelligence AI agent.
Given a relationship graph of persons, locations, organizations, and evidence, your job is to:
- Identify the most connected individuals (potential masterminds or key players)
- Detect hidden relationships and indirect connections
- Find suspicious clusters of activity
- Map organizational hierarchies or criminal networks
- Identify intermediaries, money mules, or accomplices
- Highlight isolated entities that may be undetected suspects

Present findings as a structured network analysis with relationship chains."""


def analyze_graph(case_id: str, nodes: list, edges: list) -> str:
    context = f"Case ID: {case_id}\n\nGraph Nodes ({len(nodes)}):\n"
    for node in nodes[:30]:
        context += f"- [{node.get('type', 'Unknown')}] {node.get('id', 'N/A')}\n"

    context += f"\nGraph Edges ({len(edges)}):\n"
    for edge in edges[:50]:
        context += f"- {edge.get('source', '?')} --[{edge.get('relation', '?')}]--> {edge.get('target', '?')}\n"

    return run_agent("graph_agent", PROMPT, context)
