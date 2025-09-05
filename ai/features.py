# ai/features.py

from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd # Added for structured feature output

def extract_task_features(task_data: Dict[str, Any]) -> pd.Series:
    """
    Extracts numerical and categorical features from task data for AI models.
    This version prepares features for a scikit-learn-like model.

    Args:
        task_data (Dict[str, Any]): A dictionary containing task attributes
                                     (e.g., from TaskCreate schema or Task model).

    Returns:
        pd.Series: A pandas Series of extracted features, with named indices.
                   This format is convenient for scikit-learn models.
    """
    features = {}

    # --- Numerical Features ---
    title = task_data.get("title", "")
    description = task_data.get("description", "")

    features["title_length"] = len(title)
    features["description_length"] = len(description)

    # Convert priority to a numerical scale (assuming 1 is highest, 10 is lowest)
    # A lower number means higher priority. We might want to invert this for some models
    # or keep it as is if the model learns the inverse relationship.
    # Here, we'll keep it as 1-10.
    features["priority"] = task_data.get("priority", 5) # Default priority

    # Time-based features
    deadline: Optional[datetime] = task_data.get("deadline")
    if deadline:
        # Ensure deadline is timezone-aware if it's a datetime object
        if isinstance(deadline, str):
            try:
                # Handle ISO 8601 format with or without timezone
                if deadline.endswith('Z'):
                    deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                else:
                    deadline = datetime.fromisoformat(deadline)
            except ValueError:
                deadline = None # Invalid format
        elif not isinstance(deadline, datetime):
             deadline = None # Not a datetime object

        if deadline:
            # If deadline is naive, assume UTC or local depending on application context.
            # For consistency, let's make it timezone-aware (e.g., UTC) if it's naive.
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc) # Compare with current UTC time
            time_until_deadline_seconds = (deadline - now).total_seconds()
            features["days_until_deadline"] = max(0, time_until_deadline_seconds / (3600 * 24)) # Days
            features["has_deadline"] = 1 # Binary feature
        else:
            features["days_until_deadline"] = -1 # Indicate no deadline
            features["has_deadline"] = 0
    else:
        features["days_until_deadline"] = -1 # Indicate no deadline
        features["has_deadline"] = 0

    # --- Categorical Features (for simplicity, treated as numerical for now) ---
    # In a real model, these would often be one-hot encoded or embedded.
    # For a simple linear model, we'll pass them as integers.
    features["project_id"] = task_data.get("project_id", 0) # Use 0 for None
    features["category_id"] = task_data.get("category_id", 0) # Use 0 for None

    # --- Text-based Features (derived from tags) ---
    tags_str: Optional[str] = task_data.get("tags")
    if tags_str:
        tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        features["num_tags"] = len(tags)
        # Example binary features for common tags
        features["has_urgent_tag"] = 1 if "urgent" in tags else 0
        features["has_meeting_tag"] = 1 if "meeting" in tags else 0
        features["has_report_tag"] = 1 if "report" in tags else 0
    else:
        features["num_tags"] = 0
        features["has_urgent_tag"] = 0
        features["has_meeting_tag"] = 0
        features["has_report_tag"] = 0
    
    # Ensure all expected features are present, even if with default values
    # This is crucial for consistent input to the model
    expected_features = [
        "title_length", "description_length", "priority", "days_until_deadline",
        "has_deadline", "project_id", "category_id", "num_tags",
        "has_urgent_tag", "has_meeting_tag", "has_report_tag"
    ]
    for feature_name in expected_features:
        if feature_name not in features:
            features[feature_name] = 0 # Default to 0 if not set

    # Convert to pandas Series for consistent order and easy model input
    return pd.Series(features, index=expected_features)

