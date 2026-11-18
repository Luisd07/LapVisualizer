"""Parser for the AMB / RMonitor timing protocol (v1.0).

The protocol is a stream of comma-separated records, one per line, each
beginning with a ``$`` command token. Records may arrive in any order and most
record types are re-broadcast periodically ("refresh"); only ``$J`` passing
records are guaranteed unique. This parser accumulates state across the whole
log and resolves it once at the end: re-broadcast records (``$F``/``$G``/``$H``
and the competitor/class/setting records) resolve to their latest value, while
``$J`` records accumulate into each driver's lap list.

Reference: *RMonitor Timing Protocol*, Track Timing, v1.0 (2001-10-01) — see
``docs/AMB RMonitor Timing Protocol.pdf``.

Field reuse note: real-world karting exports (Orbits) place the kart *chassis*
brand in the protocol's "Nationality" field and the *team* name in the
``$COMP`` "Additional data" field. The parser maps them to ``chassis``/``team``.
"""

import csv
from dataclasses import dataclass

# Minimum field count per record type, including the command token itself.
_MIN_FIELDS = {
    "$F": 6,
    "$A": 8,
    "$COMP": 8,
    "$B": 3,
    "$C": 3,
    "$E": 3,
    "$G": 5,
    "$H": 5,
    "$I": 3,
    "$J": 4,
}

_TRACK_NAME_KEY = "TRACKNAME"
_TRACK_LENGTH_KEY = "TRACKLENGTH"
_SECONDS_PER_MINUTE = 60

# Cap the warning list so a pathologically malformed file cannot bloat storage.
_MAX_WARNINGS = 100


def parse_clock(value: str) -> float | None:
    """Convert an ``HH:MM:SS.DDD`` clock string to a float number of seconds.

    Also accepts ``MM:SS.DDD`` and bare ``SS.DDD`` forms. Returns ``None`` for
    an empty or malformed value.

    Args:
        value: The clock string from a timing record.

    Returns:
        The duration in seconds, or ``None`` if it cannot be parsed.
    """
    text = value.strip()
    if not text:
        return None
    try:
        pieces = [float(piece) for piece in text.split(":")]
    except ValueError:
        return None
    total = 0.0
    for piece in pieces:
        total = total * _SECONDS_PER_MINUTE + piece
    return total


def _to_int(value: str) -> int | None:
    """Return `value` as an int, or ``None`` if it is empty or non-numeric."""
    try:
        return int(value)
    except TypeError, ValueError:
        return None


def _to_float(value: str) -> float | None:
    """Return `value` as a float, or ``None`` if it is empty or non-numeric."""
    try:
        return float(value)
    except TypeError, ValueError:
        return None


@dataclass
class ParsedLap:
    """A single completed lap derived from a `$J` passing record."""

    lap_number: int
    lap_time_seconds: float
    total_time_seconds: float


@dataclass
class ParsedDriver:
    """A competitor, their laps, and their resolved standings.

    The standings come from the `$G` (race) and `$H` (practice/qualifying)
    records: their last-broadcast value is the driver's final classification.
    """

    reg_number: str
    car_number: str
    first_name: str
    last_name: str
    transponder: str | None
    chassis: str | None
    team: str | None
    race_class: str | None
    laps: list[ParsedLap]
    # Resolved from the final `$G` race-information record.
    finish_position: int | None
    laps_completed: int | None
    total_time_seconds: float | None
    # Resolved from the final `$H` practice/qualifying record.
    best_lap_position: int | None
    official_best_lap_number: int | None
    official_best_lap_time: float | None


@dataclass
class ParsedSession:
    """The fully resolved result of parsing one RMonitor log."""

    name: str
    run_number: int | None
    track_name: str | None
    track_length: float | None
    # Resolved from the final `$F` heartbeat and any `$I` init record.
    flag_status: str | None
    race_time_seconds: float | None
    time_of_day: str | None
    session_date: str | None
    drivers: list[ParsedDriver]
    warnings: list[str]


@dataclass
class _Competitor:
    """Mutable accumulator for competitor fields seen across `$A`/`$COMP`."""

    reg_number: str
    car_number: str = ""
    first_name: str = ""
    last_name: str = ""
    transponder: str | None = None
    chassis: str | None = None
    team: str | None = None
    class_number: int | None = None


@dataclass
class _RaceInfo:
    """Latest `$G` race-information snapshot for a competitor."""

    position: int | None = None
    laps: int | None = None
    total_time: float | None = None


@dataclass
class _PracticeInfo:
    """Latest `$H` practice/qualifying snapshot for a competitor."""

    position: int | None = None
    best_lap_number: int | None = None
    best_lap_time: float | None = None


class RMonitorParser:
    """Accumulates RMonitor records and produces a `ParsedSession`."""

    def __init__(self) -> None:
        """Initialise empty accumulators for a fresh parse."""
        self._competitors: dict[str, _Competitor] = {}
        self._classes: dict[int, str] = {}
        self._run_number: int | None = None
        self._run_name: str = ""
        self._track_name: str | None = None
        self._track_length: float | None = None
        self._flag_status: str | None = None
        self._race_time: float | None = None
        self._time_of_day: str | None = None
        self._session_date: str | None = None
        self._passings: dict[str, list[tuple[float | None, float]]] = {}
        self._lineno = 0
        self._race_info: dict[str, _RaceInfo] = {}
        self._practice_info: dict[str, _PracticeInfo] = {}
        self._warnings: list[str] = []
        self._handlers = {
            "$F": self._handle_heartbeat,
            "$A": self._handle_competitor_a,
            "$COMP": self._handle_competitor_comp,
            "$B": self._handle_run,
            "$C": self._handle_class,
            "$E": self._handle_setting,
            "$G": self._handle_race_info,
            "$H": self._handle_practice_info,
            "$I": self._handle_init,
            "$J": self._handle_passing,
        }

    def parse(self, text: str) -> ParsedSession:
        """Parse a full RMonitor log and return the resolved session.

        Args:
            text: The decoded contents of an `rmon.log` file.

        Returns:
            A `ParsedSession` with drivers, laps, and any parse warnings.
        """
        for lineno, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            if not line.startswith("$"):
                self._warn(lineno, "line does not start with '$'")
                continue
            try:
                fields = next(csv.reader([line]))
            except csv.Error as exc:
                self._warn(lineno, f"could not split record: {exc}")
                continue
            self._dispatch(fields, lineno)
        return self._build()

    def _dispatch(self, fields: list[str], lineno: int) -> None:
        """Route one record to its handler after validating its field count."""
        command = fields[0]
        self._lineno = lineno
        handler = self._handlers.get(command)
        if handler is None:
            self._warn(lineno, f"unknown record type {command!r}")
            return
        if len(fields) < _MIN_FIELDS[command]:
            self._warn(lineno, f"{command} record has too few fields")
            return
        handler(fields)

    def _competitor(self, reg_number: str) -> _Competitor:
        """Return the accumulator for `reg_number`, creating it on first use."""
        return self._competitors.setdefault(reg_number, _Competitor(reg_number))

    def _handle_heartbeat(self, fields: list[str]) -> None:
        """Handle `$F` — session heartbeat: keep the latest clock and flag."""
        time_of_day = fields[3].strip()
        if time_of_day:
            self._time_of_day = time_of_day
        race_time = parse_clock(fields[4])
        if race_time is not None:
            self._race_time = race_time
        flag = fields[5].strip()
        if flag:
            self._flag_status = flag

    def _handle_competitor_a(self, fields: list[str]) -> None:
        """Handle `$A` — competitor registration with transponder and class."""
        comp = self._competitor(fields[1])
        comp.car_number = fields[2]
        comp.transponder = fields[3] or None
        comp.first_name = fields[4]
        comp.last_name = fields[5]
        comp.chassis = fields[6] or None
        comp.class_number = _to_int(fields[7]) or comp.class_number

    def _handle_competitor_comp(self, fields: list[str]) -> None:
        """Handle `$COMP` — competitor registration with team and class."""
        comp = self._competitor(fields[1])
        comp.car_number = fields[2]
        comp.class_number = _to_int(fields[3]) or comp.class_number
        comp.first_name = fields[4]
        comp.last_name = fields[5]
        comp.chassis = fields[6] or None
        comp.team = fields[7] or None

    def _handle_run(self, fields: list[str]) -> None:
        """Handle `$B` — run number and description."""
        self._run_number = _to_int(fields[1])
        self._run_name = fields[2]

    def _handle_class(self, fields: list[str]) -> None:
        """Handle `$C` — a class number and its name."""
        class_number = _to_int(fields[1])
        if class_number is not None:
            self._classes[class_number] = fields[2]

    def _handle_setting(self, fields: list[str]) -> None:
        """Handle `$E` — track name and length settings."""
        key = fields[1].strip().upper()
        value = fields[2].strip()
        if key == _TRACK_NAME_KEY:
            self._track_name = value or None
        elif key == _TRACK_LENGTH_KEY:
            self._track_length = parse_clock(value) if ":" in value else _to_float(value)

    def _handle_race_info(self, fields: list[str]) -> None:
        """Handle `$G` — race information: keep the latest standing per driver."""
        self._race_info[fields[2]] = _RaceInfo(
            position=_to_int(fields[1]),
            laps=_to_int(fields[3]),
            total_time=parse_clock(fields[4]),
        )

    def _handle_practice_info(self, fields: list[str]) -> None:
        """Handle `$H` — practice/qualifying info: keep the latest best lap."""
        self._practice_info[fields[2]] = _PracticeInfo(
            position=_to_int(fields[1]),
            best_lap_number=_to_int(fields[3]),
            best_lap_time=parse_clock(fields[4]),
        )

    def _handle_init(self, fields: list[str]) -> None:
        """Handle `$I` — init record: capture the date and clear the scoreboard."""
        time_of_day = fields[1].strip()
        if time_of_day:
            self._time_of_day = time_of_day
        session_date = fields[2].strip()
        if session_date:
            self._session_date = session_date
        # An init record clears the timing scoreboard; drop accumulated results.
        self._passings.clear()
        self._race_info.clear()
        self._practice_info.clear()

    def _handle_passing(self, fields: list[str]) -> None:
        """Handle `$J` — one timing-loop crossing for a competitor."""
        reg_number = fields[1]
        lap_time = parse_clock(fields[2])
        if lap_time is None:
            self._warn(
                self._lineno, f"unparseable lap time {fields[2]!r} for registration {reg_number}"
            )
        total_time = parse_clock(fields[3]) or 0.0
        self._passings.setdefault(reg_number, []).append((lap_time, total_time))

    def _build(self) -> ParsedSession:
        """Resolve all accumulated state into a `ParsedSession`."""
        drivers = [
            self._build_driver(reg_number, comp) for reg_number, comp in self._competitors.items()
        ]
        drivers.sort(key=_driver_sort_key)
        return ParsedSession(
            name=self._run_name or "Untitled session",
            run_number=self._run_number,
            track_name=self._track_name,
            track_length=self._track_length,
            flag_status=self._flag_status,
            race_time_seconds=self._race_time,
            time_of_day=self._time_of_day,
            session_date=self._session_date,
            drivers=drivers,
            warnings=self._warnings,
        )

    def _build_driver(self, reg_number: str, comp: _Competitor) -> ParsedDriver:
        """Resolve one competitor's laps and standings into a `ParsedDriver`."""
        laps: list[ParsedLap] = []
        for index, (lap_time, total_time) in enumerate(self._passings.get(reg_number, [])):
            # The first crossing has no measured lap time; skip it. An unparseable
            # time (None, already warned) is skipped too, leaving a gap in the numbers.
            if lap_time is None or lap_time <= 0.0:
                continue
            laps.append(ParsedLap(index, lap_time, total_time))
        race = self._race_info.get(reg_number)
        practice = self._practice_info.get(reg_number)
        race_class = self._classes.get(comp.class_number) if comp.class_number is not None else None
        return ParsedDriver(
            reg_number=reg_number,
            car_number=comp.car_number,
            first_name=comp.first_name,
            last_name=comp.last_name,
            transponder=comp.transponder,
            chassis=comp.chassis,
            team=comp.team,
            race_class=race_class,
            laps=laps,
            finish_position=race.position if race is not None else None,
            laps_completed=race.laps if race is not None else None,
            total_time_seconds=race.total_time if race is not None else None,
            best_lap_position=practice.position if practice is not None else None,
            # A best lap of 0 means the driver set no timed lap — treat as None.
            official_best_lap_number=(
                practice.best_lap_number or None if practice is not None else None
            ),
            official_best_lap_time=(
                practice.best_lap_time or None if practice is not None else None
            ),
        )

    def _warn(self, lineno: int, message: str) -> None:
        """Record a non-fatal parse warning, capped at `_MAX_WARNINGS`."""
        if len(self._warnings) < _MAX_WARNINGS:
            self._warnings.append(f"line {lineno}: {message}")
        elif len(self._warnings) == _MAX_WARNINGS:
            self._warnings.append("additional warnings suppressed")


def _driver_sort_key(driver: ParsedDriver) -> tuple[int, int, str]:
    """Sort drivers by car number, numerically when possible."""
    number = driver.car_number
    if number.isdigit():
        return (0, int(number), number)
    return (1, 0, number)


def parse_log(text: str) -> ParsedSession:
    """Parse RMonitor log `text` and return the resolved session."""
    return RMonitorParser().parse(text)
