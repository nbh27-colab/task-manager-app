# api/schemas/analytics.py

from pydantic import BaseModel
from datetime import date
from typing import Dict, List, Optional

class DailyPerformance(BaseModel):
    """Schema for daily performance metrics."""
    date: date
    tasks_completed: int
    total_time_spent_hours: float
    overdue_tasks_completed: int
    average_completion_time_hours: Optional[float] = None

class WeeklyPerformance(BaseModel):
    """Schema for weekly performance metrics."""
    week_start_date: date
    tasks_completed: int
    total_time_spent_hours: float
    overdue_tasks_completed: int
    average_completion_time_hours: Optional[float] = None
    tasks_by_category: Dict[str, int]
    tasks_by_project: Dict[str, int]

class MonthlyPerformance(BaseModel):
    """Schema for monthly performance metrics."""
    month: str # e.g., "2024-07"
    tasks_completed: int
    total_time_spent_hours: float
    overdue_tasks_completed: int
    average_completion_time_hours: Optional[float] = None
    tasks_by_category: Dict[str, int]
    tasks_by_project: Dict[str, int]

class PerformanceSummary(BaseModel):
    """Overall performance summary."""
    total_tasks_completed: int
    total_time_spent_hours: float
    average_tasks_per_day: float
    completion_rate: float # Percentage of tasks completed vs total
    on_time_completion_rate: float # Percentage of tasks completed on time
    most_productive_category: Optional[str] = None
    most_productive_project: Optional[str] = None

class AnalyticsData(BaseModel):
    """Comprehensive analytics data."""
    daily_data: List[DailyPerformance]
    weekly_data: List[WeeklyPerformance]
    monthly_data: List[MonthlyPerformance]
    summary: PerformanceSummary
