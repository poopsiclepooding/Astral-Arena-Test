from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, List, Tuple

from pydantic import BaseModel

from agentverse.agents import BaseAgent

from . import role_assigner_registry

if TYPE_CHECKING:
    from agentverse.agents import CriticAgent, RoleAssignerAgent


class BaseRoleAssigner(BaseModel):
    """
    The base class of role assignment class.
    """

    @abstractmethod
    async def astep(
        self,
        role_assigner: RoleAssignerAgent,
        group_members: List[CriticAgent],
        advice: str = "No advice yet.",
        task_description: str = "",
        *args,
        **kwargs,
    ) -> List[CriticAgent]:
        pass

    def reset(self):
        pass


@role_assigner_registry.register("dummy")
class DummyRoleAssigner(BaseRoleAssigner):
    """
    The base class of role assignment class.
    """

    async def astep(
        self,
        role_assigner: RoleAssignerAgent,
        group_members: List[CriticAgent],
        advice: str = "No advice yet.",
        task_description: str = "",
        *args,
        **kwargs,
    ) -> List[CriticAgent]:
        return group_members

    def reset(self):
        pass
