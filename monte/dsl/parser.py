"""Simple parser for the Monte DSL.

The goal of this module is not to be a full blown parser but to provide
an ergonomic and well tested way to describe scenarios in early project
stages.  The grammar that we support is purposely small and documented in
:func:`parse_scenario`.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List

from .model import Dataset, Metric, Scenario, Task


class DSLParseError(RuntimeError):
    """Raised when the provided DSL snippet cannot be parsed."""


_SCENARIO_RE = re.compile(r"scenario\s+\"(?P<name>[^\"]+)\"\s*{(?P<body>.*)}\s*\Z", re.DOTALL)
_DATASET_RE = re.compile(r"dataset\s+\"(?P<name>[^\"]+)\"\s+from\s+\"(?P<path>[^\"]+)\"$")
_PARAMETER_RE = re.compile(r"parameter\s+(?P<name>[a-zA-Z_][\w]*)\s*=\s*(?P<value>.+)$")
_METRIC_RE = re.compile(r"metric\s+\"(?P<name>[^\"]+)\"\s+using\s+(?P<aggregator>.+)$")
_TASK_RE = re.compile(r"task\s+(?P<name>[a-zA-Z_][\w]*)\s*{\s*$")
_ASSIGNMENT_RE = re.compile(r"(?P<key>[a-zA-Z_][\w]*)\s*=\s*(?P<value>.+)$")


@dataclass
class _ParserState:
    lines: List[str]
    index: int = 0

    def has_next(self) -> bool:
        return self.index < len(self.lines)

    def peek(self) -> str:
        return self.lines[self.index]

    def consume(self) -> str:
        value = self.lines[self.index]
        self.index += 1
        return value


def _strip_comments(text: str) -> str:
    cleaned: List[str] = []
    for line in text.splitlines():
        result: List[str] = []
        in_quote = False
        escaped = False
        index = 0
        while index < len(line):
            char = line[index]

            if char == "\\" and not escaped:
                escaped = True
                result.append(char)
                index += 1
                continue

            if char == '"' and not escaped:
                in_quote = not in_quote
                result.append(char)
                index += 1
                continue

            if not in_quote and char == "/" and index + 1 < len(line) and line[index + 1] == "/":
                break

            result.append(char)
            escaped = False
            index += 1

        stripped = "".join(result).rstrip()
        if stripped:
            cleaned.append(stripped)
    return "\n".join(cleaned)


def _normalize(text: str) -> List[str]:
    return [line.strip() for line in _strip_comments(text).splitlines() if line.strip()]


def _parse_value(raw: str):  # type: ignore[override]
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw.isdigit():
        return int(raw)
    try:
        return float(raw)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise DSLParseError(f"Unsupported literal: {raw}") from exc


def _parse_task(state: _ParserState, header: str) -> Task:
    match = _TASK_RE.match(header)
    if not match:
        raise DSLParseError(f"Malformed task declaration: {header}")

    options = {}
    while state.has_next():
        line = state.consume()
        if line == "}":
            break
        assignment = _ASSIGNMENT_RE.match(line)
        if not assignment:
            raise DSLParseError(f"Invalid task option: {line}")
        options[assignment.group("key")] = _parse_value(assignment.group("value"))
    else:  # pragma: no cover - defensive branch
        raise DSLParseError("Task block not closed with '}'")

    engine = options.pop("engine", None)
    if engine is None:
        raise DSLParseError("Task block must define an engine")
    if not isinstance(engine, str):
        raise DSLParseError("Task engine must be a string literal")

    return Task(name=match.group("name"), engine=engine, options=options)


def parse_scenario(text: str) -> Scenario:
    """Parse a DSL scenario and return a :class:`Scenario` object.

    Supported constructs
    --------------------
    - ``scenario "name" { ... }`` wraps the declaration and is mandatory.
    - ``dataset "name" from "path"`` registers a dataset.
    - ``parameter name = literal`` stores a parameter (numbers or strings).
    - ``task name { engine = "engine" [, option = literal]* }`` defines a task.
    - ``metric "name" using aggregator`` registers a metric to compute.

    Literal values are either quoted strings, integers or floats. Comments are
    supported via ``//``.
    """

    match = _SCENARIO_RE.match(text.strip())
    if not match:
        raise DSLParseError("A scenario must start with 'scenario \"name\" { ... }'")

    body_lines = _normalize(match.group("body"))
    state = _ParserState(lines=body_lines)

    scenario = Scenario(name=match.group("name"))

    while state.has_next():
        line = state.consume()
        if line == "}":
            # Trailing braces are ignored to make the parser more permissive.
            continue
        if dataset_match := _DATASET_RE.match(line):
            scenario.datasets.append(
                Dataset(name=dataset_match.group("name"), path=dataset_match.group("path"))
            )
            continue
        if parameter_match := _PARAMETER_RE.match(line):
            scenario.parameters[parameter_match.group("name")] = _parse_value(
                parameter_match.group("value")
            )
            continue
        if line.startswith("task "):
            scenario.tasks.append(_parse_task(state, header=line))
            continue
        if metric_match := _METRIC_RE.match(line):
            scenario.metrics.append(
                Metric(
                    name=metric_match.group("name"),
                    aggregator=metric_match.group("aggregator"),
                )
            )
            continue
        raise DSLParseError(f"Unable to parse line: {line}")

    return scenario


__all__ = ["parse_scenario", "DSLParseError"]
