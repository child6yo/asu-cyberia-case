from services.agent.models.models import Project
from typing import List
from pydantic import BaseModel


class ProjectResponse(BaseModel):
    response: List[Project]
