"""Tests for the lap-analysis service."""

from backend.app import models
from backend.app.schemas.analysis import SessionType
from backend.app.services import analysis
from backend.app.services.ingest import ingest_log
from tests.data import RACE_LOG, SAMPLE_LOG


def _ingest(db_session) -> models.Session:
    """Ingest the practice sample log and return the stored session."""
    session, _ = ingest_log(db_session, filename="test.log", raw=SAMPLE_LOG)
    return session


def test_classify_session_type_uses_the_run_name():
    assert analysis.classify_session_type("Heat 1") is SessionType.RACE
    assert analysis.classify_session_type("Pre-Final") is SessionType.RACE
    # "Final Practice" is a practice — the practice keyword wins over "final".
    assert analysis.classify_session_type("Final Practice - Q1") is SessionType.PRACTICE
    assert analysis.classify_session_type("Qualifying 2") is SessionType.PRACTICE


def test_build_leaderboard_ranks_practice_by_best_lap(db_session):
    board = analysis.build_leaderboard(_ingest(db_session))
    # `PydanticSchema` is configured with `use_enum_values`, so the field
    # round-trips to the enum's string value — compare with `==`, not `is`.
    assert board.session_type == SessionType.PRACTICE
    assert [entry.reg_number for entry in board.entries] == ["11", "22", "33"]
    assert board.entries[0].position == 1
    assert board.entries[0].gap_to_leader == 0.0
    assert board.entries[1].gap_to_leader == 2.0


def test_build_leaderboard_orders_race_by_finishing_position(db_session):
    session, _ = ingest_log(db_session, filename="race.log", raw=RACE_LOG)
    board = analysis.build_leaderboard(session)
    assert board.session_type == SessionType.RACE
    assert [entry.reg_number for entry in board.entries] == ["11", "22", "33"]
    # #22 finished on the lead lap — a time gap to the winner.
    assert board.entries[1].gap_to_leader == 11.5
    # #33 finished a lap down — counted in laps, with no time gap.
    assert board.entries[2].laps_down == 1
    assert board.entries[2].gap_to_leader is None


def test_build_leaderboard_filters_by_class(db_session):
    board = analysis.build_leaderboard(_ingest(db_session), race_class="Class B")
    assert [entry.reg_number for entry in board.entries] == ["33"]


def test_build_progression_marks_personal_best(db_session):
    progressions = analysis.build_progression(_ingest(db_session), ["11"])
    assert len(progressions) == 1
    laps = progressions[0].laps
    assert len(laps) == 5
    assert sum(lap.is_personal_best for lap in laps) >= 1


def test_build_comparison_aligns_by_lap_number(db_session):
    result = analysis.build_comparison(_ingest(db_session), ["11", "22"])
    assert [d.reg_number for d in result.drivers] == ["11", "22"]
    assert len(result.rows) == 5
    assert set(result.rows[0].times) == {"11", "22"}


def test_build_stats_flags_outlier(db_session):
    stats = analysis.build_stats(_ingest(db_session), ["33"])
    assert len(stats) == 1
    assert stats[0].lap_count == 5
    assert stats[0].outlier_lap_numbers == [4]
