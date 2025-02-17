from agentverse.registry import Registry

executor_registry = Registry(name="ExecutorRegistry")

from .base import BaseExecutor, NoneExecutor
from .code_test import CodeTestExecutor
from .coverage_test import CoverageTestExecutor
from .tool_using import ToolUsingExecutor
