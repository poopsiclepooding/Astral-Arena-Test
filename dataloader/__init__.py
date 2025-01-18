from agentverse.registry import Registry

dataloader_registry = Registry(name="dataloader")

from .commongen import CommongenLoader
from .gsm8k import GSM8KLoader
from .humaneval import HumanevalLoader
from .logic_grid import LogicGridLoader
from .mgsm import MGSMLoader
from .responsegen import ResponseGenLoader
