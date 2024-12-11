import os
from langfuse import Langfuse

class TracingService:
    def __init__(self):
        if not all(
            [
                os.getenv("LANGFUSE_SECRET_KEY"),
                os.getenv("LANGFUSE_PUBLIC_KEY"),
                os.getenv("LANGFUSE_BASEURL"),
            ]
        ):
            raise ValueError(
                "LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY and LANGFUSE_BASEURL must be set"
            )
        self.langfuse = Langfuse()

    def start_trace(self, conversation_id: str, **kwargs):
        return self.langfuse.trace(
            session_id=conversation_id,
            input={"conversation_id": conversation_id, **kwargs},
        )

    def finalize_trace(self) -> None:
        self.langfuse.flush()

    def create_event(self, trace_id: str, event_name: str, event_data: dict) -> None:
        pass

    def start_span(self, trace_id: str, span_name: str, span_data: dict) -> str:
        return "span_id"

    def finalize_span(self, trace_id: str, span_id: str) -> None:
        pass

    def start_generation(
        self, trace_id: str, generation_name: str, generation_data: dict
    ) -> str:
        return "generation_id"

    def finalize_generation(self, trace_id: str, generation_id: str) -> None:
        pass
