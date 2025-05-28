from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import time



#  API Models
class ProblemRequest(BaseModel):
    problem: str

class FeedbackRequest(BaseModel):
    feedback: str
    approved: bool = False

class ApprovalRequest(BaseModel):
    approved: bool = True
    feedback: Optional[str] = None

class PauseRequest(BaseModel):
    reason: Optional[str] = "User requested pause"
    
class ResumeRequest(BaseModel):
    continue_from: Optional[str] = None  # Optional parameter to specify where to resume

class TaskResponse(BaseModel):
    task_id: str
    message: str = "Task submitted successfully"
    timestamp: float = time.time()

class StatusResponse(BaseModel):
    task_id: str
    current_agent: str
    agent_status: Dict[str, str]
    completed_agents: List[str]
    progress: int
    step_messages: List[str]
    created_at: float
    updated_at: float
    complete: bool
    error: Optional[str] = None
    agent_feedback: Dict[str, Optional[str]]
    revision_counts: Dict[str, int]
    awaiting_feedback: bool
    awaiting_user_approval: bool = False
    paused: bool = False
    pause_reason: Optional[str] = None
    pause_timestamp: Optional[float] = None

class AgentOutputResponse(BaseModel):
    agent: str
    output: Optional[str] = None

class ResultResponse(BaseModel):
    result: str = ""  # Default to empty string instead of None
    complete: bool
    error: Optional[str] = None
