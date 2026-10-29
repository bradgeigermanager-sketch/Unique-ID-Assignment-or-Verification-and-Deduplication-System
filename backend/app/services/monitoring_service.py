from datetime import datetime, timedelta
from typing import Dict, List, Optional
from neo4j import GraphDatabase
from app.config import get_settings
import time

class MonitoringService:
    def __init__(self):
        settings = get_settings()
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        with self.driver.session() as session:
            # 组织节点数
            org_count = session.run("MATCH (e:Employee) RETURN count(e) as count").single()['count']
            
            # 汇报关系数
            rel_count = session.run("MATCH ()-[r:REPORTS_TO]->() RETURN count(r) as count").single()['count']
            
            # 环数量
            cycle_count = session.run("""
                MATCH path = (n:Employee)-[:REPORTS_TO*2..10]->(n)
                WHERE n.is_active = true
                RETURN count(path) as count
            """).single()['count']
            
            # 最近 24 小时操作
            operations = session.run("""
                MATCH (a:AuditLog)
                WHERE a.timestamp >= datetime() - duration({hours: 24})
                RETURN count(a) as count
            """).single()['count']
            
            return {
                "organization_nodes": org_count,
                "reporting_relationships": rel_count,
                "active_cycles": cycle_count,
                "operations_24h": operations,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        with self.driver.session() as session:
            # 查询延迟统计
            latency = session.run("""
                MATCH (a:PerformanceLog)
                WHERE a.timestamp >= datetime() - duration({hours: 1})
                RETURN 
                    avg(a.query_time_ms) as avg_latency,
                    max(a.query_time_ms) as max_latency,
                    count(a) as query_count
            """).single()
            
            return {
                "avg_latency_ms": latency['avg_latency'] or 0,
                "max_latency_ms": latency['max_latency'] or 0,
                "query_count_1h": latency['query_count'] or 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_alerts(self, threshold: int = 5) -> List[Dict]:
        """获取告警列表"""
        with self.driver.session() as session:
            alerts = session.run("""
                MATCH (a:Alert)
                WHERE a.severity IN ['high', 'critical']
                AND a.timestamp >= datetime() - duration({hours: 24})
                RETURN 
                    a.id as id,
                    a.type as type,
                    a.severity as severity,
                    a.message as message,
                    a.timestamp as timestamp
                ORDER BY a.timestamp DESC
                LIMIT 20
            """)
            
            return [dict(record) for record in alerts]
    
    def get_audit_log(self, limit: int = 100, offset: int = 0) -> Dict:
        """获取审计日志"""
        with self.driver.session() as session:
            total = session.run("""
                MATCH (a:AuditLog) RETURN count(a) as count
            """).single()['count']
            
            logs = session.run("""
                MATCH (a:AuditLog)
                ORDER BY a.timestamp DESC
                SKIP $offset LIMIT $limit
                RETURN 
                    a.id as id,
                    a.action as action,
                    a.entity_type as entity_type,
                    a.entity_id as entity_id,
                    a.user as user,
                    a.timestamp as timestamp,
                    a.details as details
            """, offset=offset, limit=limit)
            
            return {
                "total": total,
                "logs": [dict(record) for record in logs]
            }
    
    def record_audit(self, action: str, entity_type: str, entity_id: str, 
                     user: str, details: Dict = None):
        """记录审计日志"""
        with self.driver.session() as session:
            session.run("""
                CREATE (a:AuditLog {
                    id: randomUUID(),
                    action: $action,
                    entity_type: $entity_type,
                    entity_id: $entity_id,
                    user: $user,
                    details: $details,
                    timestamp: datetime()
                })
            """, action=action, entity_type=entity_type, entity_id=entity_id, 
               user=user, details=details or {})
    
    def record_performance(self, query_type: str, query_time_ms: float):
        """记录性能日志"""
        with self.driver.session() as session:
            session.run("""
                CREATE (p:PerformanceLog {
                    id: randomUUID(),
                    query_type: $query_type,
                    query_time_ms: $query_time_ms,
                    timestamp: datetime()
                })
            """, query_type=query_type, query_time_ms=query_time_ms)
    
    def close(self):
        self.driver.close()
