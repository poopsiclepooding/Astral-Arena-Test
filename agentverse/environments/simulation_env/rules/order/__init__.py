from agentverse.registry import Registry

order_registry = Registry(name="OrderRegistry")

from .base import BaseOrder
from .classroom import ClassroomOrder
from .concurrent import ConcurrentOrder
from .prisoner import PrisonerOrder
from .random import RandomOrder
from .sde_team import SdeTeamOrder
from .sde_team_given_tests import SdeTeamGivenTestsOrder
from .sequential import SequentialOrder
