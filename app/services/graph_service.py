"""Graph Intelligence Service — Neo4j relationship graph. No LLM dependency."""
from neo4j import GraphDatabase
from app.config import settings

driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))


def add_entities_to_graph(entities: dict, evidence_id: str, case_id: str = None):
    with driver.session() as session:
        for person in entities.get("persons", []):
            session.run(
                "MERGE (p:Person {name: $name}) MERGE (e:Evidence {id: $eid}) MERGE (p)-[:LINKED_TO]->(e)",
                name=person, eid=evidence_id
            )
            if case_id:
                session.run(
                    "MERGE (p:Person {name: $name}) MERGE (c:Case {id: $cid}) MERGE (p)-[:INVOLVED_IN]->(c)",
                    name=person, cid=case_id
                )
        for location in entities.get("locations", []):
            session.run(
                "MERGE (l:Location {name: $name}) MERGE (e:Evidence {id: $eid}) MERGE (l)-[:MENTIONED_IN]->(e)",
                name=location, eid=evidence_id
            )
            if case_id:
                session.run(
                    "MERGE (l:Location {name: $name}) MERGE (c:Case {id: $cid}) MERGE (l)-[:PART_OF]->(c)",
                    name=location, cid=case_id
                )
        for org in entities.get("organizations", []):
            session.run(
                "MERGE (o:Organization {name: $name}) MERGE (e:Evidence {id: $eid}) MERGE (o)-[:MENTIONED_IN]->(e)",
                name=org, eid=evidence_id
            )


def find_connected_suspects(person_name: str) -> list:
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Person {name: $name})-[*1..3]-(connected) RETURN connected, labels(connected) as type LIMIT 50",
            name=person_name
        )
        return [{"node": dict(r["connected"]), "type": r["type"]} for r in result]


def get_full_case_graph(case_id: str) -> dict:
    with driver.session() as session:
        nodes_result = session.run(
            "MATCH (n)-[:PART_OF|INVOLVED_IN|LINKED_TO*0..2]->(c:Case {id: $cid}) "
            "RETURN n, labels(n) as type LIMIT 100", cid=case_id
        )
        edges_result = session.run(
            "MATCH (a)-[r]->(b) WHERE (a)-[:INVOLVED_IN*0..3]->(:Case {id: $cid}) "
            "RETURN a.name as source, type(r) as rel, b.name as target LIMIT 200", cid=case_id
        )
        return {
            "nodes": [{"id": dict(r["n"]).get("name", ""), "type": r["type"][0]} for r in nodes_result],
            "edges": [{"source": r["source"], "relation": r["rel"], "target": r["target"]} for r in edges_result]
        }


def detect_mastermind(case_id: str) -> list:
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Person)-[:INVOLVED_IN]->(:Case {id: $cid}) "
            "WITH p, size((p)--()) as connections ORDER BY connections DESC "
            "RETURN p.name as name, connections LIMIT 5", cid=case_id
        )
        return [{"suspect": r["name"], "connection_count": r["connections"]} for r in result]


def add_relationship(source_name, source_type, target_name, target_type, relationship):
    with driver.session() as session:
        session.run(
            f"MERGE (a:{source_type} {{name: $sname}}) MERGE (b:{target_type} {{name: $tname}}) "
            f"MERGE (a)-[:{relationship}]->(b)",
            sname=source_name, tname=target_name
        )
    return {"status": "created", "source": source_name, "target": target_name, "rel": relationship}
