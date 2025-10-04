from services.agent.models.models import Project
from typing import List


class Projects:
    projects = []

    def Put(self, project: Project):
        self.projects.append(project)

    def GetAll(self) -> List[Project]:
        return self.projects

projects_volume = Projects()