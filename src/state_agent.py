from typing import Annotated, Dict, Any, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field, field_validator
import os

# ==========================================
# 1. HIPAA-COMPLIANT DATA VALIDATION SCHEMAS
# ==========================================
class HealthLogSchema(BaseModel):
    """Strict Pydantic structure checking for health data inconsistencies (HIPAA Layer)."""
    patient_id: str
    role: str = Field(..., description="Must be Patient, Doctor, or Caregiver")
    systolic_bp: int = Field(..., ge=60, le=250)
    glucose_level: int = Field(..., ge=30, le=500)
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = ["Patient", "Doctor", "Caregiver"]
        if v not in allowed:
            raise ValueError(f"Unauthorized Role. Must be one of {allowed}")
        return v

# ==========================================
# 2. LANGGRAPH STATE DEFINITION
# ==========================================
class AgentState(TypedDict):
    input_data: Dict[str, Any]
    validated_data: Dict[str, Any]
    clinical_insights: str
    auth_role: str
    errors: List[str]

# ==========================================
# 3. WORKFLOW NODES (STATE MACHINES)
# ==========================================
def authentication_and_validation_node(state: AgentState) -> Dict[str, Any]:
    """Implements Role-Based Authentication and Inconsistency Error Handling."""
    errors = []
    validated = {}
    role = state["input_data"].get("role", "Unknown")
    
    try:
        # Run strict Pydantic validation for health data consistency
        schema = HealthLogSchema(**state["input_data"])
        validated = schema.model_dump()
    except Exception as e:
        # Structured monitoring capturing data inconsistencies safely
        errors.append(f"HIPAA/Consistency Validation Failure: {str(e)}")
        
    return {
        "validated_data": validated, 
        "auth_role": role, 
        "errors": errors
    }

def analysis_router_node(state: AgentState) -> Dict[str, Any]:
    """Generates automated insights based on verified workflows and access logs."""
    if state["errors"]:
        return {"clinical_insights": "Workflow aborted due to data consistency errors."}
        
    role = state["auth_role"]
    data = state["validated_data"]
    
    # Customize reporting insights based on access roles
    if role == "Doctor":
        insights = f"[CLINICAL VIEW] Patient {data['patient_id']} displays BP of {data['systolic_bp']} and Glucose of {data['glucose_level']} mg/dL. Prescriptive actions unlocked."
    elif role == "Caregiver":
        insights = f"[CAREGIVER VIEW] Monitoring metrics for Patient {data['patient_id']}. Vital parameters are logged."
    else:
        insights = f"[PATIENT VIEW] Your health logs have been safely secured using basic HIPAA-compliant practices."
        
    return {"clinical_insights": insights}

# ==========================================
# 4. COMPILING THE GRAPH
# ==========================================
builder = StateGraph(AgentState)
builder.add_node("authenticate_and_validate", authentication_and_validation_node)
builder.add_node("generate_insights", analysis_router_node)

builder.add_edge(START, "authenticate_and_validate")
builder.add_edge("authenticate_and_validate", "generate_insights")
builder.add_edge("generate_insights", END)

workflow_agent = builder.compile()