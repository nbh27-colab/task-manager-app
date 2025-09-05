# api/schemas/ai.py

from pydantic import BaseModel, Field
from typing import Optional, List

# Re-import TaskTimeEstimation if you prefer to group all AI-related schemas here.
# Otherwise, it can remain in task.py
# from .task import TaskTimeEstimation # Uncomment if you move it here

class TaskSuggestionRequest(BaseModel):
    """
    Schema for requesting AI suggestions for a task.
    """
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task for which suggestions are requested.")
    description: Optional[str] = Field(None, description="Optional detailed description of the task.")

class TaskSuggestionResponse(BaseModel):
    """
    Schema for returning AI suggestions for task attributes.
    """
    # AI can suggest any of these fields
    category_id: Optional[int] = Field(None, description="Suggested category ID for the task.")
    project_id: Optional[int] = Field(None, description="Suggested project ID for the task.")
    tags: Optional[str] = Field(None, description="Suggested comma-separated tags for the task.")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Suggested priority (1-10) for the task.")
    urgency_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Suggested urgency score (0.0-1.0) for the task.")
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Suggested importance score (0.0-1.0) for the task.")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score of the AI's suggestions (0.0-1.0).")

class AgentChatInput(BaseModel):
    """Schema for input to the agent chat endpoint.
    Moved here from api/endpoints/agent.py to centralize schemas.
    """
    message: str = Field(..., description="The user's message to the AI agent.")
    chat_history: Optional[List[dict]] = Field(None, description="Optional chat history for context.")

class AgentChatResponse(BaseModel):
    """Schema for the AI agent's response.
    Moved here from api/endpoints/agent.py to centralize schemas.
    """
    response: str = Field(..., description="The AI agent's textual response.")
    # Optionally, you could return the updated chat history here too
    # updated_chat_history: List[Dict] = Field(...)