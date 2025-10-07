from base import BaseUseCase

class SummarizeTextUseCase(BaseUseCase):
    async def execute(self, data: str) -> str:
        # Lógica simulada — poderia chamar um modelo de IA, etc.
        return f"[Resumo]: {data[:50]}..."