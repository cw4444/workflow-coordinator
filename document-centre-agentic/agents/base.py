from __future__ import annotations

from abc import ABC, abstractmethod

from tools.models import AgentResult, Job


class BaseAgent(ABC):
    name = "Base Agent"

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def run(self, job: Job) -> AgentResult:
        raise NotImplementedError

