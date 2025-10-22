"""Cursor tap class."""

from __future__ import annotations

import sys

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_cursor import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapCursor(Tap):
    """Cursor tap class."""

    name = "tap-cursor"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            description="The Cursor Admin API key for authentication (TAP_CURSOR_API_KEY env var)",
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=True),
            description="The earliest record date to sync daily usage data (TAP_CURSOR_START_DATE env var). Used for initial sync only - subsequent runs use incremental replication.",
        ),
        th.Property(
            "end_date",
            th.DateTimeType(nullable=True),
            description="The latest record date to sync daily usage data (TAP_CURSOR_END_DATE env var, defaults to yesterday)",
        ),
    ).to_dict()


    @override
    def discover_streams(self) -> list[streams.CursorStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.DailyUsageDataStream(self),
            streams.MembersStream(self),
        ]


if __name__ == "__main__":
    TapCursor.cli()
