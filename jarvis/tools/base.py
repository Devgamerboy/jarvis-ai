from abc import ABC, abstractmethod

from .permissions import RISK_SAFE


class Tool(ABC):
    """Abstract base class all JARVIS tools must subclass.

    Subclasses **must** override ``execute()`` and should set a
    descriptive ``name``, ``description``, ``risk`` level and
    ``category`` at construction time.
    """

    def __init__(
        self,
        name: str,
        description: str,
        category: str = "Utilities",
        risk: str = RISK_SAFE,
    ):
        self.name = name
        self.description = description
        self.category = category
        self.risk = risk

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        ...

    def spec(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "risk": self.risk,
        }

    def parameter_schema(self) -> dict:
        return {}
