from domain.use_cases.base_use_case import BaseUseCase

data = "This is a sample meeting transcript that needs to be summarized. It contains various points discussed during the meeting, including project updates, deadlines, and action items."


class SummarizeMeetingUseCase(BaseUseCase):
    async def execute(self, data: str) -> str:
        # Lógica simulada — poderia chamar um modelo de IA, etc.
        return f"[Resumo da Reunião]: {data[:50]}..."