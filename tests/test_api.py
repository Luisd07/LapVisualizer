"""Tests for the LapVisualizer HTTP API."""

from fastapi import status
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from tests.data import SAMPLE_LOG


def _upload(client: TestClient):
    """Upload the synthetic sample log and return the response."""
    return client.post(
        "/api/sessions/upload",
        files={"file": ("test.rmon.log", SAMPLE_LOG, "text/plain")},
    )


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_upload_stores_session(client: TestClient):
    response = _upload(client)
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["driver_count"] == 3
    assert body["total_laps"] == 15
    assert body["duplicate"] is False
    assert body["track_name"] == "Test Circuit"
    assert body["warnings"] == []


def test_duplicate_upload_is_detected(client: TestClient):
    _upload(client)
    second = _upload(client)
    assert second.json()["duplicate"] is True
    assert len(client.get("/api/sessions").json()) == 1


def test_upload_rejects_empty_file(client: TestClient):
    response = client.post(
        "/api/sessions/upload",
        files={"file": ("empty.log", b"", "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_upload_rejects_non_rmonitor_file(client: TestClient):
    response = client.post(
        "/api/sessions/upload",
        files={"file": ("cat.jpg", b"not a timing log", "text/plain")},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_upload_rejects_oversized_file(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_mb", 0)
    assert _upload(client).status_code == status.HTTP_413_CONTENT_TOO_LARGE


def test_session_detail_lists_drivers_and_state(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    detail = client.get(f"/api/sessions/{session_id}").json()
    assert detail["driver_count"] == 3
    assert {d["reg_number"] for d in detail["drivers"]} == {"11", "22", "33"}
    # Resolved from the $F/$I records.
    assert detail["flag_status"] == "Finish"
    assert detail["race_time_seconds"] == 360.0
    assert detail["session_date"] == "17 may 26"


def test_driver_detail_includes_resolved_standings(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    driver = client.get(f"/api/sessions/{session_id}/drivers/11").json()
    # From the $G record:
    assert driver["finish_position"] == 1
    assert driver["laps_completed"] == 5
    assert driver["total_time_seconds"] == 283.0
    # From the $H record:
    assert driver["best_lap_position"] == 1
    assert driver["official_best_lap_number"] == 2
    assert driver["official_best_lap_time"] == 44.0


def test_delete_session(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    assert client.delete(f"/api/sessions/{session_id}").status_code == status.HTTP_204_NO_CONTENT
    assert client.get(f"/api/sessions/{session_id}").status_code == status.HTTP_404_NOT_FOUND


def test_missing_session_returns_404(client: TestClient):
    response = client.get("/api/sessions/does-not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_leaderboard_orders_by_best_lap(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    board = client.get(f"/api/sessions/{session_id}/leaderboard").json()
    assert [row["reg_number"] for row in board] == ["11", "22", "33"]
    assert board[0]["position"] == 1
    assert board[0]["gap_to_leader"] == 0.0
    assert board[1]["gap_to_leader"] == 2.0


def test_leaderboard_filters_by_class(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    board = client.get(
        f"/api/sessions/{session_id}/leaderboard",
        params={"race_class": "Class B"},
    ).json()
    assert [row["reg_number"] for row in board] == ["33"]


def test_stats_flags_outlier_lap(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    stats = client.get(
        f"/api/sessions/{session_id}/stats",
        params={"drivers": "33"},
    ).json()
    assert len(stats) == 1
    assert stats[0]["outlier_lap_numbers"] == [4]


def test_comparison_aligns_drivers(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    result = client.get(
        f"/api/sessions/{session_id}/comparison",
        params={"drivers": "11,22"},
    ).json()
    assert [d["reg_number"] for d in result["drivers"]] == ["11", "22"]
    assert len(result["rows"]) == 5
    assert result["rows"][0]["times"] == {"11": 45.0, "22": 46.5}


def test_comparison_requires_two_drivers(client: TestClient):
    session_id = _upload(client).json()["session_id"]
    response = client.get(
        f"/api/sessions/{session_id}/comparison",
        params={"drivers": "11"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
