python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.dag_service import DAGService

router = APIRouter(prefix="/api/org", tags=["组织治理"])

dag_service = DAGService()

class CycleResult(BaseModel):
    cycles: List[List[str]]
    has_cycle: bool

class FixResult(BaseModel):
    success: bool
    removed_edge: Optional[dict]

@router.get("/cycles", response_model=CycleResult)
async def get_cycles():
    cycles = dag_service.detect_cycles()
    return CycleResult(
        cycles=cycles,
        has_cycle=len(cycles) > 0
    )

@router.post("/fix-cycle")
async def fix_cycle(cycle: List[str], strategy: str = "lowest_importance"):
    result = dag_service.fix_cycle(cycle, strategy)
    return result

@router.get("/tree/{root_id}")
async def get_tree(root_id: str):
    tree = dag_service.get_organizational_tree(root_id)
    return tree
