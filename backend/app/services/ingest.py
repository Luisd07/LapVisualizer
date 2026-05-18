"""Ingestion service: turn an uploaded RMonitor log into stored rows."""

import hashlib
from uuid import uuid4

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app import models
from backend.app.services.parser import parse_log


class InvalidTimingLogError(Exception):
    """Raised when an uploaded file is not a usable RMonitor timing log."""


def _decode(raw: bytes) -> str:
    """Decode log bytes, tolerating a BOM and non-UTF-8 timing exports."""
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def ingest_log(
    db: Session,
    *,
    filename: str,
    raw: bytes,
) -> tuple[models.Session, bool]:
    """Parse and persist an uploaded RMonitor log.

    Uploads are de-duplicated by SHA-256 content hash: re-uploading identical
    bytes returns the existing session instead of creating a copy.

    Args:
        db: An active database session.
        filename: The original upload filename, kept for reference.
        raw: The raw bytes of the uploaded log.

    Returns:
        A tuple of the stored session and a flag that is true when the upload
        duplicated an existing session.

    Raises:
        InvalidTimingLogError: When the file parses to no competitors and is
            therefore not a usable RMonitor timing log.
    """
    content_hash = hashlib.sha256(raw).hexdigest()
    existing = db.scalar(
        select(models.Session).where(models.Session.content_hash == content_hash),
    )
    if existing is not None:
        logger.info(
            "Duplicate upload {!r} ignored; returning session {}",
            filename,
            existing.id,
        )
        return existing, True

    parsed = parse_log(_decode(raw))
    if not parsed.drivers:
        logger.warning("Rejected upload {!r}: no competitors found", filename)
        msg = "The file is not a valid RMonitor timing log (no competitors found)."
        raise InvalidTimingLogError(msg)

    session = models.Session(
        id=uuid4().hex,
        name=parsed.name,
        run_number=parsed.run_number,
        track_name=parsed.track_name,
        track_length=parsed.track_length,
        flag_status=parsed.flag_status,
        race_time_seconds=parsed.race_time_seconds,
        time_of_day=parsed.time_of_day,
        session_date=parsed.session_date,
        source_filename=filename,
        content_hash=content_hash,
        warnings=parsed.warnings,
    )
    for parsed_driver in parsed.drivers:
        session.drivers.append(
            models.Driver(
                reg_number=parsed_driver.reg_number,
                car_number=parsed_driver.car_number,
                first_name=parsed_driver.first_name,
                last_name=parsed_driver.last_name,
                transponder=parsed_driver.transponder,
                chassis=parsed_driver.chassis,
                team=parsed_driver.team,
                race_class=parsed_driver.race_class,
                finish_position=parsed_driver.finish_position,
                laps_completed=parsed_driver.laps_completed,
                total_time_seconds=parsed_driver.total_time_seconds,
                best_lap_position=parsed_driver.best_lap_position,
                official_best_lap_number=parsed_driver.official_best_lap_number,
                official_best_lap_time=parsed_driver.official_best_lap_time,
                laps=[
                    models.Lap(
                        lap_number=lap.lap_number,
                        lap_time_seconds=lap.lap_time_seconds,
                        total_time_seconds=lap.total_time_seconds,
                    )
                    for lap in parsed_driver.laps
                ],
            ),
        )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(
        "Ingested session {} from {!r}: {} drivers, {} laps, {} warnings",
        session.id,
        filename,
        len(parsed.drivers),
        sum(len(driver.laps) for driver in parsed.drivers),
        len(parsed.warnings),
    )
    return session, False
