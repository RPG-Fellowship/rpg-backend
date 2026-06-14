from neontology import init_neontology

from app.core.config import settings


def connect_db() -> None:
    init_neontology(
        neo4j_uri=settings.NEO4J_URI,
        neo4j_username=settings.NEO4J_USERNAME,
        neo4j_password=settings.NEO4J_PASSWORD,
    )
