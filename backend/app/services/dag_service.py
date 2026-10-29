python
from neo4j import GraphDatabase
from typing import List, Dict, Optional
from app.config import get_settings

class DAGService:
    def __init__(self):
        settings = get_settings()
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def detect_cycles(self) -> List[List[str]]:
        """检测组织层级中的环"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (n:Employee)-[:REPORTS_TO*2..10]->(n)
                WHERE n.is_active = true
                RETURN [node IN nodes(path) | node.employee_id] as cycle
                LIMIT 100
            """)
            return [record['cycle'] for record in result]
    
    def get_organizational_tree(self, root_id: str) -> Dict:
        """获取组织树"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (root:Employee {employee_id: $root_id})
                OPTIONAL MATCH path = (root)-[:REPORTS_TO*0..5]->(sub:Employee)
                WHERE sub.is_active = true
                RETURN root, collect(DISTINCT sub) as subordinates
            """, root_id=root_id)
            record = result.single()
            return self._build_tree(record['root'], record['subordinates'])
    
    def _build_tree(self, root, subordinates) -> Dict:
        """递归构建组织树"""
        node = {
            'employee_id': root['employee_id'],
            'name': root['name'],
            'title': root['title'],
            'children': []
        }
        # 简化：实际需更复杂的树构建逻辑
        return node
    
    def fix_cycle(self, cycle: List[str], strategy: str = "lowest_importance") -> Dict:
        """修复环"""
        with self.driver.session() as session:
            # 找到环中重要性最低的边
            result = session.run("""
                MATCH path = (n:Employee)-[:REPORTS_TO*2..10]->(n)
                WHERE n.is_active = true AND n.employee_id IN $cycle
                WITH nodes(path) as nodes, relationships(path) as rels
                UNWIND rels as r
                WITH r, 
                     coalesce(startNode(r).importance_score, 1.0) as s1,
                     coalesce(endNode(r).importance_score, 1.0) as s2
                ORDER BY MIN(s1, s2) ASC
                LIMIT 1
                DELETE r
                RETURN r AS removed_edge
            """, cycle=cycle)
            
            removed = result.single()
            return {
                "success": removed is not None,
                "removed_edge": dict(removed['removed_edge']) if removed else None
            }
    
    def close(self):
        self.driver.close()
