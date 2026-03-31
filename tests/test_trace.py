"""Unit tests for coglet.trace: OpenTelemetry-based CogletTrace."""
from __future__ import annotations

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from coglet.trace import CogletTrace


def test_trace_record_spans():
    """CogletTrace records transmit/enact as OTel spans."""
    mem = InMemorySpanExporter()
    trace = CogletTrace(exporter=mem)
    trace.record("TestCoglet", "transmit", "ch1", {"key": "value"})
    trace.record("TestCoglet", "enact", "cmd1", "data")
    trace.close()

    spans = mem.get_finished_spans()
    assert len(spans) == 2
    assert spans[0].attributes["coglet.type"] == "TestCoglet"
    assert spans[0].attributes["coglet.op"] == "transmit"
    assert spans[0].attributes["coglet.target"] == "ch1"
    assert '"key"' in spans[0].attributes["coglet.data"]
    assert spans[1].attributes["coglet.op"] == "enact"
    assert spans[1].attributes["coglet.target"] == "cmd1"


def test_trace_otel_fields():
    """Spans have trace_id and span_id."""
    mem = InMemorySpanExporter()
    trace = CogletTrace(exporter=mem)
    trace.record("A", "transmit", "ch", 1)
    trace.close()

    span = mem.get_finished_spans()[0]
    assert span.context.trace_id != 0
    assert span.context.span_id != 0


def test_trace_in_memory_exporter():
    """InMemorySpanExporter captures spans for test inspection."""
    mem = InMemorySpanExporter()
    trace = CogletTrace(exporter=mem)
    trace.record("TestCoglet", "transmit", "ch1", {"key": "value"})
    trace.record("TestCoglet", "enact", "cmd1", "data")
    trace.close()

    spans = mem.get_finished_spans()
    assert len(spans) == 2
    assert spans[0].name == "coglet.transmit"
    assert spans[0].attributes["coglet.type"] == "TestCoglet"
    assert spans[0].attributes["coglet.target"] == "ch1"
    assert spans[1].name == "coglet.enact"
    assert spans[1].attributes["coglet.target"] == "cmd1"


def test_trace_unserializable_data():
    """Non-JSON-serializable data is repr'd instead of crashing."""
    mem = InMemorySpanExporter()
    trace = CogletTrace(exporter=mem)
    trace.record("A", "transmit", "ch", object())
    trace.close()

    spans = mem.get_finished_spans()
    assert len(spans) == 1
    assert isinstance(spans[0].attributes["coglet.data"], str)


def test_trace_no_exporter():
    """CogletTrace works with no exporter (noop)."""
    trace = CogletTrace()
    trace.record("A", "transmit", "ch", "data")
    trace.close()


def test_trace_span_names():
    """Span names follow coglet.{op} convention."""
    mem = InMemorySpanExporter()
    trace = CogletTrace(exporter=mem)
    trace.record("Cog", "transmit", "out", "x")
    trace.record("Cog", "enact", "cmd", "y")
    trace.close()

    names = [s.name for s in mem.get_finished_spans()]
    assert names == ["coglet.transmit", "coglet.enact"]
