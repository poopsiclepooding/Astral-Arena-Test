from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, List

from pydantic import BaseModel

from agentverse.message import Message

from . import selector_registry as SelectorRegistry

if TYPE_CHECKING:
    from agentverse.environments import BaseEnvironment


@SelectorRegistry.register("base")
class BaseSelector(BaseModel):
    """
    Base class for all selecters
    """

    @abstractmethod
    def select_message(
        self, environment: BaseEnvironment, messages: List[Message]
    ) -> List[Message]:
        """Selects a set of valid messages from all messages"""
        pass

    def reset(self) -> None:
        pass
