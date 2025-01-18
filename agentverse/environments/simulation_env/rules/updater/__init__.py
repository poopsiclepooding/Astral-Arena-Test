from agentverse.registry import Registry

updater_registry = Registry(name="UpdaterRegistry")

from .base import BaseUpdater
from .basic import BasicUpdater
from .classroom import ClassroomUpdater
from .pokemon import PokemonUpdater
from .sde_team import SdeTeamUpdater
