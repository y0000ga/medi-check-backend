from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from typing import Any

from app.db.session import SessionLocal
from app.services.jobs.history import (
    DEFAULT_MISSED_GRACE_PERIOD,
    create_missed_histories,
)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def run_missed_histories_job(
    *,
    from_datetime: datetime,
    to_datetime: datetime | None = None,
    grace_period: timedelta = DEFAULT_MISSED_GRACE_PERIOD,
) -> int:
    db = SessionLocal()
    try:
        return create_missed_histories(
            db=db,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            grace_period=grace_period,
        )
    finally:
        db.close()


def _run_missed_histories_command(args: argparse.Namespace) -> None:
    to_datetime = args.to_datetime or datetime.now(UTC)
    from_datetime = args.from_datetime or (to_datetime - timedelta(hours=args.lookback_hours))
    created_count = run_missed_histories_job(
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        grace_period=timedelta(hours=args.grace_hours),
    )

    print(
        "missed histories job completed: "
        f"created_count={created_count}, "
        f"from_datetime={from_datetime.isoformat()}, "
        f"to_datetime={to_datetime.isoformat()}, "
        f"grace_hours={args.grace_hours}"
    )


def _register_missed_histories_command(subparsers: Any) -> None:
    parser = subparsers.add_parser(
        "missed-histories",
        help="Create missed history records for due schedule occurrences.",
    )
    parser.add_argument(
        "--from-datetime",
        type=_parse_datetime,
        help="UTC ISO datetime. Defaults to now minus --lookback-hours.",
    )
    parser.add_argument(
        "--to-datetime",
        type=_parse_datetime,
        help="UTC ISO datetime. Defaults to current time.",
    )
    parser.add_argument(
        "--lookback-hours",
        type=int,
        default=24,
        help="Used when --from-datetime is omitted. Default: 24.",
    )
    parser.add_argument(
        "--grace-hours",
        type=int,
        default=int(DEFAULT_MISSED_GRACE_PERIOD.total_seconds() // 3600),
        help="Grace period in hours before a schedule is marked missed. Default: 2.",
    )
    parser.set_defaults(handler=_run_missed_histories_command)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run background jobs manually.",
    )
    subparsers = parser.add_subparsers(
        dest="job_name",
        required=True,
        help="Background job to run.",
    )

    _register_missed_histories_command(subparsers)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
