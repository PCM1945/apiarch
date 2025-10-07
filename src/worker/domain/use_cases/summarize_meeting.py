from base import BaseUseCase

class SummarizeMeetingUseCase(BaseUseCase):
    async def execute(self, data: str) -> str:
        # Lógica simulada — poderia chamar um modelo de IA, etc.
        return f"[Resumo da Reunião]: {data[:50]}..."