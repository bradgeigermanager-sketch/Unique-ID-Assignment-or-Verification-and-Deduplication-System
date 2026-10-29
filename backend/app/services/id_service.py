python
import uuid
import time
from typing import Optional
from neo4j import GraphDatabase
from app.config import get_settings

class IDService:
    def __init__(self):
        settings = get_settings()
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def generate_uuid(self, entity_type: str = "") -> str:
        """生成 UUID"""
        base = str(uuid.uuid4())
        if entity_type:
            return f"{entity_type.upper()}-{base}"
        return base
    
    def generate_snowflake(self, entity_type: str = "", prefix: str = "") -> str:
        """生成雪花 ID（简化版）"""
        timestamp = int(time.time() * 1000)
        random_part = int(time.time() * 1000) % 10000
        base = f"{timestamp}{random_part}"
        if prefix:
            return f"{prefix}-{base}"
        return base
    
    def is_id_unique(self, entity_type: str, id_value: str) -> bool:
        """检查 ID 是否唯一"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e) WHERE e.id = $id_value AND e.entity_type = $entity_type
                RETURN count(e) as count
            """, id_value=id_value, entity_type=entity_type)
            record = result.single()
            return record['count'] == 0
    
    def reserve_id(self, entity_type: str, id_value: str, ttl: int = 3600) -> bool:
        """预留 ID"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (r:IDReservation {entity_type: $entity_type, id_value: $id_value})
                ON CREATE SET r.reserved_at = datetime(), r.expires_at = datetime() + duration({seconds: $ttl})
                ON MATCH SET r.reserved_at = datetime()
                RETURN r
            """, entity_type=entity_type, id_value=id_value, ttl=ttl)
            return result.single() is not None
    
    def close(self):
        self.driver.close()
