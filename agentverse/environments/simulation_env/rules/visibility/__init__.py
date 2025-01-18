from typing import Dict

from agentverse.registry import Registry

visibility_registry = Registry(name="VisibilityRegistry")

from .all import AllVisibility
from .base import BaseVisibility
from .classroom import ClassroomVisibility
from .oneself import OneselfVisibility
from .pokemon import PokemonVisibility
from .prisoner import PrisonerVisibility
from .sde_team import SdeTeamVisibility
