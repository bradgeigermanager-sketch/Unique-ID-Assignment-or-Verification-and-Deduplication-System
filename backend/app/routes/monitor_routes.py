from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/api/monitor", tags=["监控"])

monitor_service = MonitoringService()

class SystemMetrics(BaseModel):
    organization_nodes: int
    reporting_relationships: int
    active_cycles: int
    operations_24h: int
    timestamp: str

class PerformanceMetrics(BaseModel):
    avg_latency_ms: float
    max_latency_ms: float
    query_count_1h: int
    timestamp: str

class Alert(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    timestamp: str

class AuditLogEntry(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: str
    user: str
    timestamp: str
    details: dict

class AuditLogResponse(BaseModel):
    total: int
    logs: List[AuditLogEntry]

@router.get("/metrics/system", response_model=SystemMetrics)
async def get_system_metrics():
    return SystemMetrics(**monitor_service.get_system_metrics())

@router.get("/metrics/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    return PerformanceMetrics(**monitor_service.get_performance_metrics())

@router.get("/alerts", response_model=List[Alert])
async def get_alerts(threshold: int = 5):
    return monitor_service.get_alerts(threshold)

@router.get("/audit", response_model=AuditLogResponse)
async def get_audit_log(limit: int = 100, offset: int = 0):
    return AuditLogResponse(**monitor_service.get_audit_log(limit, offset))

@router.post("/audit")
async def record_audit(action: str, entity_type: str, entity_id: str, 
                       user: str, details: dict = None):
    monitor_service.record_audit(action, entity_type, entity_id, user, details)
    return {"status": "recorded"}
