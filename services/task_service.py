from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from collections import Counter # For finding most common elements
from datetime import datetime

from database import crud, models, vectordb
from api.schemas.task import TaskCreate, TaskUpdate, TaskTimeEstimation
from api.schemas.ai import TaskSuggestionRequest, TaskSuggestionResponse # Import new AI schemas

# NEW IMPORTS for AI modules
from ai.models.time_estimator import TimeEstimatorModel
from ai.features import extract_task_features
from ai.llm_chains import task_suggestion_chain # NEW IMPORT: Our LangChain task suggestion chain


class TaskService:
    """
    Service layer for handling task-related business logic,
    including CRUD operations and AI integrations.
    """

    def __init__(self, db: Session):
        self.db = db
        # Initialize AI models (can be singleton or passed in via dependency injection in larger apps)
        self.time_estimator_model = TimeEstimatorModel()

    def _prepare_metadata_for_chromadb(self, task: models.Task) -> Dict[str, Any]:
        """
        Prepares metadata dictionary for ChromaDB, handling None values.
        """
        return {
            "owner_id": task.owner_id,
            "task_id": task.id,
            "project_id": task.project_id if task.project_id is not None else -1, # Use -1 or 0 for None
            "category_id": task.category_id if task.category_id is not None else -1, # Use -1 or 0 for None
            "priority": task.priority if task.priority is not None else 5, # Default priority if None
            "status": task.status if task.status is not None else "Unknown", # Default status if None
            "tags": task.tags if task.tags is not None else "", # Use empty string for None tags
            "urgency_score": task.urgency_score if task.urgency_score is not None else 0.0,
            "importance_score": task.importance_score if task.importance_score is not None else 0.0,
            "ai_estimated_time_hours": task.ai_estimated_time_hours if task.ai_estimated_time_hours is not None else 0.0,
            "actual_time_spent_hours": task.actual_time_spent_hours if task.actual_time_spent_hours is not None else 0.0,
        }

    def create_task(self, task: TaskCreate, user_id: int) -> models.Task:
        """
        Creates a new task.
        Can include initial AI suggestions if desired.
        """
        # --- Basic task creation logic (similar to existing crud) ---
        db_task = crud.create_user_task(self.db, task=task, user_id=user_id)
        print(f"DEBUG: Task created in DB with ID: {db_task.id}")

        # --- AI Integration: Add task to Vector DB for future suggestions ---
        task_text = f"{db_task.title} {db_task.description or ''}".strip()
        if task_text:
            metadata = self._prepare_metadata_for_chromadb(db_task)
            vectordb.add_task_embedding(
                task_id=db_task.id,
                task_text=task_text,
                owner_id=db_task.owner_id,
                metadata=metadata
            )
            print(f"DEBUG: Task {db_task.id} embedding added to ChromaDB.")
        else:
            print(f"DEBUG: Task {db_task.id} has no text, skipping embedding.")

        return db_task

    def get_task(self, task_id: int) -> Optional[models.Task]:
        """Retrieves a single task by ID."""
        return crud.get_task(self.db, task_id=task_id)

    def get_tasks_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Task]:
        """Retrieves all tasks for a specific user."""
        return crud.get_user_tasks(self.db, user_id=user_id, skip=skip, limit=limit)

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Optional[models.Task]:
        """
        Updates an existing task.
        Can include re-embedding if title/description changes.
        """
        db_task = crud.update_task(self.db, task_id=task_id, task_update=task_update)
        print(f"DEBUG: Task {task_id} updated in DB.")

        # --- AI Integration: Re-embed if relevant fields changed ---
        if db_task and (
            task_update.title is not None or 
            task_update.description is not None or
            task_update.category_id is not None or 
            task_update.project_id is not None or
            task_update.tags is not None or
            task_update.priority is not None or
            task_update.urgency_score is not None or
            task_update.importance_score is not None or
            task_update.ai_estimated_time_hours is not None or
            task_update.actual_time_spent_hours is not None
        ):
            updated_title = db_task.title
            updated_description = db_task.description
            
            task_text = f"{updated_title} {updated_description or ''}".strip()
            if task_text:
                updated_metadata = self._prepare_metadata_for_chromadb(db_task)
                vectordb.update_task_embedding(
                    task_id=db_task.id,
                    new_task_text=task_text,
                    owner_id=db_task.owner_id,
                    new_metadata=updated_metadata
                )
                print(f"DEBUG: Task {db_task.id} embedding updated in ChromaDB.")
            else:
                print(f"DEBUG: Task {db_task.id} has no text after update, skipping embedding update.")
        else:
            print(f"DEBUG: No relevant fields changed for task {task_id}, skipping embedding update.")

        return db_task

    def delete_task(self, task_id: int) -> Optional[models.Task]:
        """Deletes a task by ID."""
        print(f"DEBUG: Deleting embedding for task {task_id} from ChromaDB.")
        vectordb.delete_task_embedding(task_id) 
        db_task = crud.delete_task(self.db, task_id=task_id)
        print(f"DEBUG: Task {task_id} deleted from DB.")
        return db_task

    async def get_ai_suggestions_for_task(self, request: TaskSuggestionRequest, user_id: int) -> TaskSuggestionResponse:
        """
        Provides AI-driven suggestions for task attributes based on title and description.
        This version uses a LangChain LLM to generate suggestions.
        """
        print(f"DEBUG: Generating AI suggestions for user {user_id} with title: '{request.title}' using LLM.")

        # 1. Query similar tasks from ChromaDB for context
        query_text = f"{request.title} {request.description or ''}".strip()
        similar_tasks_results = vectordb.query_similar_tasks(
            query_text=query_text,
            n_results=5, # Increased results for better context
            owner_id=user_id
        )

        # Format similar tasks into a readable string for the LLM
        similar_tasks_context = "Không có tác vụ tương tự nào được tìm thấy."
        if similar_tasks_results:
            similar_tasks_context_list = []
            for i, res in enumerate(similar_tasks_results):
                task_meta = res['metadata']
                # Ensure all metadata fields are not None before formatting
                task_id_val = task_meta.get('task_id', 'N/A')
                title_val = res.get('document', 'N/A')[:50] + '...' if res.get('document') else 'N/A'
                category_val = task_meta.get('category_id', 'N/A')
                project_val = task_meta.get('project_id', 'N/A')
                priority_val = task_meta.get('priority', 'N/A')
                status_val = task_meta.get('status', 'N/A')
                tags_val = task_meta.get('tags', 'N/A')
                urgency_val = task_meta.get('urgency_score', 'N/A')
                importance_val = task_meta.get('importance_score', 'N/A')
                actual_time_val = task_meta.get('actual_time_spent_hours', 'N/A')

                similar_tasks_context_list.append(
                    f"- Task ID: {task_id_val}, "
                    f"Title: '{title_val}', "
                    f"Category: {category_val}, "
                    f"Project: {project_val}, "
                    f"Priority: {priority_val}, "
                    f"Status: {status_val}, "
                    f"Tags: {tags_val}, "
                    f"Urgency: {urgency_val}, "
                    f"Importance: {importance_val}, "
                    f"Actual Time: {actual_time_val} hours"
                )
            similar_tasks_context = "\n".join(similar_tasks_context_list)
            print(f"DEBUG: Formatted similar tasks context:\n{similar_tasks_context}")
        else:
            print("DEBUG: No similar tasks found for context.")

        # 2. Get available categories and projects for the user
        available_categories = crud.get_user_categories(self.db, user_id=user_id)
        available_projects = crud.get_user_projects(self.db, user_id=user_id)

        available_categories_projects_context = "Danh mục:\n"
        if available_categories:
            for cat in available_categories:
                available_categories_projects_context += f"- ID: {cat.id}, Name: '{cat.name}'\n"
        else:
            available_categories_projects_context += "Không có danh mục nào.\n"

        available_categories_projects_context += "Dự án:\n"
        if available_projects:
            for proj in available_projects:
                available_categories_projects_context += f"- ID: {proj.id}, Name: '{proj.name}'\n"
        else:
            available_categories_projects_context += "Không có dự án nào.\n"
        
        print(f"DEBUG: Formatted available categories/projects context:\n{available_categories_projects_context}")

        # 3. Invoke the LangChain LLM chain
        try:
            llm_response: TaskSuggestionResponse = await task_suggestion_chain.ainvoke({
                "title": request.title,
                "description": request.description or "",
                "similar_tasks_context": similar_tasks_context,
                "available_categories_projects_context": available_categories_projects_context
            })
            print(f"DEBUG: LLM raw response: {llm_response}")

            # The parser already ensures the output is a TaskSuggestionResponse object
            # We can optionally add a confidence score based on similarity if LLM doesn't provide it
            # For this version, we'll use a simple distance-based confidence as a fallback/complement
            confidence = 0.0
            if similar_tasks_results:
                avg_distance = sum(res['distance'] for res in similar_tasks_results) / len(similar_tasks_results)
                max_expected_distance = 1.0 # This needs tuning based on your embedding model's output
                confidence = max(0.0, 1.0 - (avg_distance / max_expected_distance))
                confidence = round(confidence, 2)
            
            # If LLM response doesn't have confidence, use our calculated one
            if llm_response.confidence_score is None:
                llm_response.confidence_score = confidence

            # Ensure urgency/importance scores are float, default to 0.0 if LLM returns None
            llm_response.urgency_score = llm_response.urgency_score if llm_response.urgency_score is not None else 0.0
            llm_response.importance_score = llm_response.importance_score if llm_response.importance_score is not None else 0.0

            print(f"DEBUG: Final AI suggestions: {llm_response.model_dump_json(indent=2)}")
            return llm_response

        except Exception as e:
            print(f"ERROR: Failed to get AI suggestions from LLM: {e}")
            # Fallback to a default or empty response in case of LLM error
            return TaskSuggestionResponse(
                category_id=None,
                project_id=None,
                tags=None,
                priority=None,
                urgency_score=0.0, # Default to 0.0
                importance_score=0.0, # Default to 0.0
                confidence_score=0.0
            )


    def estimate_task_completion_time(self, task_data: TaskCreate, user_id: int) -> TaskTimeEstimation:
        """
        Estimates the completion time for a task using an AI model.
        """
        print(f"DEBUG: Estimating time for task '{task_data.title}' for user {user_id}.")

        # 1. Extract features from task_data
        # Convert TaskCreate to a dictionary for feature extraction
        # Ensure all fields expected by extract_task_features are present, even if None
        task_data_dict = task_data.model_dump(mode='json', exclude_none=False) # Include None values for features
        
        # Add default priority if it's not provided by the schema or is None
        if 'priority' not in task_data_dict or task_data_dict['priority'] is None:
            task_data_dict['priority'] = 5 # Default priority for new tasks
        
        # Ensure description is not None for feature extraction
        if task_data_dict.get('description') is None:
            task_data_dict['description'] = ""

        # Ensure deadline is in a format extract_task_features can handle (ISO 8601 string or datetime object)
        if task_data_dict.get('deadline') is not None and isinstance(task_data_dict['deadline'], datetime):
            task_data_dict['deadline'] = task_data_dict['deadline'].isoformat() # Convert datetime to ISO string

        print(f"DEBUG: Features extracted for estimation: {task_data_dict}")
        features = extract_task_features(task_data_dict)
        print(f"DEBUG: Processed features for model: {features.to_dict()}")

        # 2. Use the initialized AI model to predict time
        estimated_time = self.time_estimator_model.predict(features.to_dict()) # Pass as dict for consistency
        confidence = self.time_estimator_model.get_confidence(features.to_dict()) # Pass as dict for consistency
        
        print(f"DEBUG: Estimated time: {estimated_time:.2f} hours, Confidence: {confidence:.2f}")

        return TaskTimeEstimation(
            ai_estimated_time_hours=estimated_time,
            confidence_score=confidence
        )

    def update_task_ai_estimated_time(self, task_id: int, ai_estimated_time_hours: float, confidence_score: Optional[float] = None) -> Optional[models.Task]:
        """
        Updates the AI-estimated time and confidence for a task in the database.
        """
        print(f"DEBUG: Updating AI estimated time for task {task_id} to {ai_estimated_time_hours:.2f} hours (Confidence: {confidence_score}).")
        return crud.update_task_ai_estimated_time(self.db, task_id=task_id, ai_estimated_time_hours=ai_estimated_time_hours, confidence_score=confidence_score)

    def update_task_urgency_importance(self, task_id: int, urgency_score: float, importance_score: float, priority: int) -> Optional[models.Task]:
        """
        Updates urgency, importance, and priority scores of a task (typically by AI).
        """
        print(f"DEBUG: Updating urgency/importance/priority for task {task_id}.")
        return crud.update_task_urgency_importance(self.db, task_id=task_id, urgency_score=urgency_score, importance_score=importance_score, priority=priority)

