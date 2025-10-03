class ProcessRequestUseCase:
    """Use case: process received data and return result."""

    async def execute(self, data: str) -> str:
        # Here goes the actual business logic (e.g.: external API call)
        return data[::-1]  # simple example: reverse string