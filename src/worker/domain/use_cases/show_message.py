from domain.use_cases.base_use_case import BaseUseCase

class ShowMessageUseCase(BaseUseCase):
    async def execute(self, data: str) -> str:
        print(f"Showing message: {data}")
        # Lógica simulada.
        return f"[ShowMessage]: {data}"