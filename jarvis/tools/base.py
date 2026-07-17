from abc import ABC, abstractmethod


class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        ...

    def spec(self) -> dict:
        return {"name": self.name, "description": self.description}
