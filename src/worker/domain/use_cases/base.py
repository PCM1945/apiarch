from abc import ABC, abstractmethod

class BaseUseCase(ABC):
    """Contrato para todos os casos de uso do worker."""

    @abstractmethod
    async def execute(self, data: str) -> str:
        """Executa a lógica principal e retorna o resultado."""
        pass