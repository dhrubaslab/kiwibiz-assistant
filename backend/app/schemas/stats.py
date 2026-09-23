from datetime import date

from pydantic import BaseModel


class CategoryCount(BaseModel):
    category: str
    count: int


class DailyCount(BaseModel):
    date: date
    count: int


class StatsDashboardResponse(BaseModel):
    by_category: list[CategoryCount]
    upload_activity: list[DailyCount]
    qa_usage: list[DailyCount]