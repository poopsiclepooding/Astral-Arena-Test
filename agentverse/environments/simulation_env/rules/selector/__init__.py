from agentverse.registry import Registry

selector_registry = Registry(name="SelectorRegistry")

from .base import BaseSelector
from .basic import BasicSelector
from .classroom import ClassroomSelector
from .pokemon import PokemonSelector
from .sde_team import SdeTeamSelector
from .sde_team_given_tests import SdeTeamGivenTestsSelector
