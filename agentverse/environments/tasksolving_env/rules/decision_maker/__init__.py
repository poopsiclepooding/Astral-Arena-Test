from agentverse.registry import Registry

decision_maker_registry = Registry(name="DecisionMakerRegistry")

from .base import BaseDecisionMaker, DummyDecisionMaker
from .brainstorming import BrainstormingDecisionMaker
from .central import CentralDecisionMaker
from .concurrent import ConcurrentDecisionMaker
from .dynamic import DynamicDecisionMaker
from .horizontal import HorizontalDecisionMaker
from .horizontal_tool import HorizontalToolDecisionMaker
from .vertical import VerticalDecisionMaker
from .vertical_solver_first import VerticalSolverFirstDecisionMaker
