from base import BaseUseCase

class ShowMessageUseCase(BaseUseCase):
    async def execute(self, data: str) -> str:
        # Lógica simulada.
        return f"[ShowMessage]: {data}"