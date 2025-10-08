from pydantic import BaseModel


class TaskStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    avg_estimated_time: float
    overdue_tasks: int