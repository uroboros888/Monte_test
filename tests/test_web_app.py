from __future__ import annotations

from typing import Generator

import pytest

pytest.importorskip("flask")

from monte.web.app import DEFAULT_DSL, create_app


@pytest.fixture()
def client() -> Generator:
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_index_renders_form(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Monte Simulation Playground" in body
    assert "Сценарий Monte DSL" in body


def test_form_submission_returns_results(client) -> None:
    response = client.post("/", data={"dsl": DEFAULT_DSL})
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "roi_p90" in body
    assert "Генерируемая конфигурация" in body


def test_api_run_returns_metrics(client) -> None:
    response = client.post("/api/run", json={"dsl": DEFAULT_DSL})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert "metrics" in payload
    assert pytest.approx(1.19, rel=1e-2) == payload["metrics"]["roi_mean"]


def test_api_run_validates_empty_payload(client) -> None:
    response = client.post("/api/run", json={"dsl": "   "})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload == {"error": "Scenario DSL cannot be empty"}
