# api/endpoints/agent.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from database import models
from database.connection import get_db
from api.dependencies import get_current_user
from agent.workflows import run_task_management_agent # Import our main agent workflow
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage # For chat history typing

router = APIRouter()

class AgentChatInput(BaseModel):
    """Schema for input to the agent chat endpoint."""
    message: str = Field(..., description="The user's message to the AI agent.")
    # chat_history will be a list of dicts, which Pydantic can convert to BaseMessage
    chat_history: Optional[List[Dict]] = Field(None, description="Optional chat history for context.")

class AgentChatResponse(BaseModel):
    """Schema for the AI agent's response."""
    response: str = Field(..., description="The AI agent's textual response.")
    # Optionally, you could return the updated chat history here too
    # updated_chat_history: List[Dict] = Field(...)

@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    chat_input: AgentChatInput,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db) # We might not need db directly here, but it's good practice to pass if needed by dependencies
):
    """
    Send a message to the AI task management agent and get a response.
    Requires authentication.
    """
    # Convert chat_history from list of dicts to list of BaseMessage objects
    # This is necessary because Pydantic deserializes to dicts, but LangChain expects BaseMessage objects.
    converted_chat_history: List[BaseMessage] = []
    if chat_input.chat_history:
        for msg_dict in chat_input.chat_history:
            if msg_dict.get("type") == "human":
                converted_chat_history.append(HumanMessage(content=msg_dict.get("content")))
            elif msg_dict.get("type") == "ai":
                converted_chat_history.append(AIMessage(content=msg_dict.get("content")))
            # Add more message types (e.g., tool, system) if needed in history

    try:
        # Call the main agent workflow
        ai_response_content = run_task_management_agent(
            user=current_user,
            input_message=chat_input.message,
            chat_history=converted_chat_history
        )
        return AgentChatResponse(response=ai_response_content)
    except Exception as e:
        print(f"Error running AI agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {e}"
        )

