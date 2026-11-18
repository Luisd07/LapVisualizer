"""Tests for the RMonitor timing-log parser."""

from pathlib import Path

import pytest

from backend.app.services.parser import parse_clock, parse_log
from tests.data import SAMPLE_LOG

_REAL_SAMPLE = Path(__file__).resolve().parent.parent / "sample_data" / "practice_session.log"

# A minimal log whose $I init record clears crossings recorded before it.
_RESET_LOG = """\
$B,1,"Reset Test"
$A,"5","5",1,"Pat","Park","K",1
$COMP,"5","5",1,"Pat","Park","K","T"
$J,"5","00:00:00.000","00:01:00.000"
$J,"5","00:00:40.000","00:01:40.000"
$I,"10:00:00.000","18 may 26"
$J,"5","00:00:00.000","00:02:00.000"
$J,"5","00:00:42.000","00:02:42.000"
"""

# Driver 7's second lap time is garbage; its third and fourth laps must keep their numbers.
_BAD_LAP_LOG = """$B,1,"Bad Lap Test"
$A,"7","7",1,"Sam","Slow","K",1
$COMP,"7","7",1,"Sam","Slow","K","T"
$J,"7","00:00:00.000","00:01:00.000"
$J,"7","00:00:40.000","00:01:40.000"
$J,"7","garbage","00:02:20.000"
$J,"7","00:00:41.000","00:03:01.000"
$J,"7","00:00:42.000","00:03:43.000"
"""


def test_parse_clock_converts_hms_to_seconds():
    assert parse_clock("00:01:18.204") == pytest.approx(78.204)
    assert parse_clock("01:00:00.000") == pytest.approx(3600.0)
    assert parse_clock("00:00:45.000") == pytest.approx(45.0)


def test_parse_clock_returns_none_for_bad_input():
    assert parse_clock("") is None
    assert parse_clock("not-a-time") is None


def test_parse_log_extracts_session_metadata():
    session = parse_log(SAMPLE_LOG.decode())
    assert session.name == "Test Practice"
    assert session.run_number == 1
    assert session.track_name == "Test Circuit"
    assert session.track_length == pytest.approx(1.2)
    assert len(session.drivers) == 3
    assert session.warnings == []


def test_parse_log_resolves_session_state():
    session = parse_log(SAMPLE_LOG.decode())
    # The final $F heartbeat and the $I init record win.
    assert session.flag_status == "Finish"
    assert session.race_time_seconds == pytest.approx(360.0)
    assert session.time_of_day == "09:06:00"
    assert session.session_date == "17 may 26"


def test_parse_log_resolves_driver_fields():
    session = parse_log(SAMPLE_LOG.decode())
    alice = next(d for d in session.drivers if d.reg_number == "11")
    assert alice.first_name == "Alice"
    assert alice.chassis == "KartCo"  # RMonitor "Nationality" field
    assert alice.team == "Team One"  # $COMP "Additional data" field
    assert alice.race_class == "Class A"


def test_parse_log_derives_timed_laps():
    session = parse_log(SAMPLE_LOG.decode())
    alice = next(d for d in session.drivers if d.reg_number == "11")
    # Six crossings yield five timed laps; the first crossing has no lap time.
    assert len(alice.laps) == 5
    assert alice.laps[0].lap_number == 1
    assert alice.laps[0].lap_time_seconds == pytest.approx(45.0)
    assert min(lap.lap_time_seconds for lap in alice.laps) == pytest.approx(44.0)


def test_parse_log_skips_unparseable_lap_time_and_keeps_passing_order():
    session = parse_log(_BAD_LAP_LOG)
    driver = session.drivers[0]
    # Lap 2 is absent; laps 3 and 4 keep their passing-order numbers (a gap, no renumber).
    assert [lap.lap_number for lap in driver.laps] == [1, 3, 4]
    assert driver.laps[1].lap_time_seconds == pytest.approx(41.0)
    assert len(session.warnings) == 1
    assert "registration 7" in session.warnings[0]
    assert "line 6" in session.warnings[0]


def test_parse_log_first_crossing_is_skipped_without_warning():
    session = parse_log(_RESET_LOG)
    assert session.warnings == []
    assert [lap.lap_number for lap in session.drivers[0].laps] == [1]


def test_parse_log_resolves_driver_standings():
    session = parse_log(SAMPLE_LOG.decode())
    alice = next(d for d in session.drivers if d.reg_number == "11")
    # From the final $G record:
    assert alice.finish_position == 1
    assert alice.laps_completed == 5
    assert alice.total_time_seconds == pytest.approx(283.0)
    # From the final $H record (early all-zero $H records are superseded):
    assert alice.best_lap_position == 1
    assert alice.official_best_lap_number == 2
    assert alice.official_best_lap_time == pytest.approx(44.0)


def test_parse_log_init_record_clears_scoreboard():
    session = parse_log(_RESET_LOG)
    assert session.session_date == "18 may 26"
    driver = session.drivers[0]
    # The two crossings before the $I reset are discarded.
    assert len(driver.laps) == 1
    assert driver.laps[0].lap_time_seconds == pytest.approx(42.0)


def test_parse_log_handles_the_real_sample():
    if not _REAL_SAMPLE.exists():
        pytest.skip(f"real sample log not found at {_REAL_SAMPLE}")
    session = parse_log(_REAL_SAMPLE.read_text(encoding="utf-8", errors="replace"))
    assert session.track_name == "Las Vegas Motorspeedway"
    assert len(session.drivers) == 48
    assert sum(len(d.laps) for d in session.drivers) > 0
    # The $F/$G records are now parsed too.
    assert session.flag_status is not None
    assert any(d.finish_position is not None for d in session.drivers)
