"""Tests for the ingestion service."""

import pytest

from backend.app.services.ingest import InvalidTimingLogError, ingest_log
from tests.data import SAMPLE_LOG


def test_ingest_stores_session(db_session):
    session, duplicate = ingest_log(db_session, filename="test.log", raw=SAMPLE_LOG)
    assert duplicate is False
    assert len(session.drivers) == 3
    assert session.warnings == []


def test_ingest_deduplicates_identical_uploads(db_session):
    first, _ = ingest_log(db_session, filename="a.log", raw=SAMPLE_LOG)
    second, duplicate = ingest_log(db_session, filename="b.log", raw=SAMPLE_LOG)
    assert duplicate is True
    assert second.id == first.id


def test_ingest_rejects_non_rmonitor_file(db_session):
    with pytest.raises(InvalidTimingLogError):
        ingest_log(db_session, filename="cat.jpg", raw=b"not a timing log at all")


def test_ingest_records_parse_warnings(db_session):
    raw = b"this line is not a record\n" + SAMPLE_LOG
    session, _ = ingest_log(db_session, filename="warn.log", raw=raw)
    # The bad leading line is recorded as a warning; the rest still parses.
    assert session.warnings
    assert len(session.drivers) == 3
