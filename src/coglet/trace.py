"""CogletTrace — OpenTelemetry-based tracing for coglet event flows.

Pass to CogletRuntime(trace=CogletTrace()) to transparently record
all transmit() and enact() events as OpenTelemetry spans. Supports
OTLP export and custom exporters.
"""

from __future__ import annotations

import json
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
)
from opentelemetry.sdk.resources import Resource


class CogletTrace:
    """OpenTelemetry-based tracer for coglet event flows.

    Usage:
        # OTLP export to a collector
        trace = CogletTrace(otlp_endpoint="http://localhost:4317")

        # Custom exporter
        trace = CogletTrace(exporter=my_exporter)

        # In-memory (for tests)
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
        mem = InMemorySpanExporter()
        trace = CogletTrace(exporter=mem)

        runtime = CogletRuntime(trace=trace)
        # ... run coglets ...
        trace.close()
    """

    def __init__(
        self,
        *,
        otlp_endpoint: str | None = None,
        exporter: SpanExporter | None = None,
        service_name: str = "coglet",
    ):
        resource = Resource.create({"service.name": service_name})
        self._provider = TracerProvider(resource=resource)

        if exporter is not None:
            self._provider.add_span_processor(SimpleSpanProcessor(exporter))
        elif otlp_endpoint is not None:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            self._provider.add_span_processor(
                SimpleSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
            )

        self._tracer = self._provider.get_tracer("coglet", "0.1.0")

    @property
    def tracer(self) -> trace.Tracer:
        return self._tracer

    @property
    def provider(self) -> TracerProvider:
        return self._provider

    def record(self, coglet_type: str, op: str, target: str, data: Any) -> None:
        """Record a transmit/enact event as an OTel span."""
        with self._tracer.start_as_current_span(
            f"coglet.{op}",
            attributes={
                "coglet.type": coglet_type,
                "coglet.op": op,
                "coglet.target": target,
            },
        ) as span:
            try:
                serialized = json.dumps(data, default=str)
            except (TypeError, ValueError):
                serialized = repr(data)
            span.set_attribute("coglet.data", serialized)

    def close(self) -> None:
        self._provider.shutdown()
