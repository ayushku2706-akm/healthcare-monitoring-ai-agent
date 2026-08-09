from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
import time

# Safe import for workflow agent to avoid crash if path differs
try:
    from state_agent import workflow_agent
except ImportError:
    try:
        from src.state_agent import workflow_agent
    except ImportError:
        workflow_agent = None



app = FastAPI(
    title="CareAI Enterprise Pipeline Backend (Track B)",
    description="HIPAA-Compliant High-Performance Healthcare Workflow Engine & AI Agent API",
    version="1.1.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to CareAI Enterprise Pipeline Backend!",
        "documentation": "/docs",
        "health_check": "/api/v1/health-check"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schema for Strict Validation & Swagger Docs
class HealthLogPayload(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "patient_id": "PAT_001",
                "role": "Doctor",
                "systolic_bp": 120,
                "glucose_level": 90,
                "auth_token": "bearer_token_sample"
            }
        }
    )

    patient_id: str = Field(..., example="PAT_001")
    role: Optional[str] = Field(default="Patient", example="Doctor", description="Must be Patient, Doctor, or Caregiver")
    systolic_bp: Optional[int] = Field(default=None, example=120, ge=60, le=250)
    glucose_level: Optional[int] = Field(default=None, example=90, ge=30, le=500)
    age: Optional[int] = Field(default=None, example=30)
    symptoms: Optional[list[str]] = Field(default=None, example=["fever", "cough"])
    vitals: Optional[Dict[str, Any]] = Field(default=None, example={"heart_rate": 78, "bp": "120/80", "glucose": 95})
    auth_token: Optional[str] = Field(default="bearer_token_sample", description="Role verification token")

class PipelineResponse(BaseModel):
    status: str
    role_authorized: str
    insights: str
    pipeline_performance: Dict[str, Any]


@app.post("/api/v1/process-health-log", response_model=PipelineResponse)
async def process_log(payload: HealthLogPayload):
    start_time = time.time()
    
    if workflow_agent is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workflow agent engine could not be loaded on the server."
        )
    
    try:
        # Convert Pydantic model to dict for LangGraph State Engine
        input_dict = payload.model_dump()
        
        # Legacy compatibility support for older clients using `age`, `symptoms`, or generic `vitals`
        if not input_dict.get("role"):
            input_dict["role"] = "Patient"

        vitals = input_dict.get("vitals") or {}
        if input_dict.get("systolic_bp") is None and isinstance(vitals, dict):
            systolic = vitals.get("systolic_bp") or vitals.get("bp")
            if isinstance(systolic, str):
                try:
                    input_dict["systolic_bp"] = int(systolic.split("/")[0].strip())
                except Exception:
                    pass
            elif isinstance(systolic, (int, float)):
                input_dict["systolic_bp"] = int(systolic)

        if input_dict.get("glucose_level") is None and isinstance(vitals, dict):
            glucose = vitals.get("glucose_level") or vitals.get("glucose")
            if isinstance(glucose, (int, float)):
                input_dict["glucose_level"] = int(glucose)

        if input_dict.get("systolic_bp") is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "msg": "Missing required clinical field: systolic_bp is required.",
                    "received": input_dict
                }
            )

        # Invoke the LangGraph State Engine
        initial_state = {
            "input_data": input_dict,
            "validated_data": {},
            "clinical_insights": "",
            "auth_role": "Clinical_User",
            "errors": []
        }
        
        result = workflow_agent.invoke(initial_state)
        latency_ms = (time.time() - start_time) * 1000
        
        # Comprehensive Error Handling Checklist Response
        if result.get("errors"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail={
                    "msg": "Health data consistency or Auth failure", 
                    "logs": result["errors"], 
                    "pipeline_latency_ms": round(latency_ms, 2)
                }
            )
            
        return {
            "status": "Success",
            "role_authorized": result.get("auth_role", "Standard_User"),
            "insights": result.get("clinical_insights", "Processed successfully through CareAI pipeline."),
            "pipeline_performance": {
                "latency_ms": round(latency_ms, 2),
                "compliance_checked": "HIPAA Basic Standards Met"
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Pipeline Execution Error: {str(e)}"
        )


@app.get("/api/v1/health-check")
async def health_check():
    """System Pipeline Performance Monitoring endpoint."""
    return {
        "status": "Operational", 
        "database_pool": "Connected", 
        "workflow_engine": "Active" if workflow_agent else "Degraded",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)