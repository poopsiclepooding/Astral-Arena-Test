import json
import re

from . import dataloader_registry
from .dataloader import DataLoader


@dataloader_registry.register("tasksolving/gsm8k")
class GSM8KLoader(DataLoader):
    def __init__(self, path: str):
        self.answer_pat = re.compile(r"#### (-?\d+)")
        super().__init__(path)

    def load(self):
        with open(self.path) as f:
            for line in f:
                line = json.loads(line)
                self.examples.append(
                    {
                        "input": line["question"],
                        "answer": line["answer"].split("#### ")[-1],
                    }
                )
