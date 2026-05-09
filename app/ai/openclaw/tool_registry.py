"""
Tool Registry — OpenClaw tool definitions for Featherless native tool calling.
These tools are available to AI agents via Qwen3's function calling.
"""

INVESTIGATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_evidence",
            "description": "Semantic search across all case evidence using natural language",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language search query"},
                    "case_id": {"type": "string", "description": "Case ID to search within"}
                },
                "required": ["query", "case_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_suspect_connections",
            "description": "Get relationship graph connections for a suspect from Neo4j",
            "parameters": {
                "type": "object",
                "properties": {
                    "person_name": {"type": "string", "description": "Full name of the suspect"}
                },
                "required": ["person_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline_events",
            "description": "Get chronological events for a case within an optional time range",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "Case ID"},
                    "start_time": {"type": "string", "description": "Start time filter (ISO format)"},
                    "end_time": {"type": "string", "description": "End time filter (ISO format)"}
                },
                "required": ["case_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_risk_score",
            "description": "Calculate risk assessment score for a case based on all evidence",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "Case ID to assess"}
                },
                "required": ["case_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_case_graph",
            "description": "Get the full relationship graph (nodes and edges) for a case",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "Case ID"}
                },
                "required": ["case_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_cctv_events",
            "description": "Get CCTV detection events and suspicious activity for a case",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "Case ID"}
                },
                "required": ["case_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_autopsy_analysis",
            "description": "Analyze autopsy or medical forensic report for a case",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "Case ID"},
                    "report_text": {"type": "string", "description": "Raw autopsy or medical report text"}
                },
                "required": ["case_id"]
            }
        }
    }
]
