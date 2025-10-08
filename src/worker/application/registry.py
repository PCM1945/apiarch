from typing import Dict, Type
from domain.use_cases.base_use_case import BaseUseCase
from domain.use_cases.summarize_text import SummarizeTextUseCase
from domain.use_cases.show_message import ShowMessageUseCase
from domain.use_cases.summarize_meeting import SummarizeMeetingUseCase  

class UseCaseRegistry:
    """Maps routing keys to specific use cases."""

    _registry: Dict[str, Type[BaseUseCase]] = {
        "task.ai.summary.generate_summary_text": SummarizeTextUseCase,
        "task.ai.summary.generate_summary_meeting": SummarizeMeetingUseCase,
        "task.app.show_message": ShowMessageUseCase,
    }

    @classmethod
    def get_use_case(cls, routing_key: str) -> BaseUseCase:
        use_case_cls = cls._registry.get(routing_key)
        if not use_case_cls:
            raise ValueError(f"No use case registered for '{routing_key}'")
        return use_case_cls()
