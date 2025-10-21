"""Cursor tap class."""

from __future__ import annotations

import os
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
            th.StringType(nullable=False),
            required=True,
            secret=True,  # Flag config as protected.
            title="API Key",
            description="The API key to authenticate against the Cursor Admin API (TAP_CURSOR_API_KEY env var)",
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=True),
            description="The earliest record date to sync daily usage data (TAP_CURSOR_START_DATE env var). Used for initial sync only - subsequent runs use incremental replication.",
        ),
        th.Property(
            "end_date",
            th.DateTimeType(nullable=True),
            description="The latest record date to sync daily usage data (TAP_CURSOR_END_DATE env var, defaults to today)",
        ),
        th.Property(
            "api_url",
            th.StringType(nullable=False),
            title="API URL",
            default="https://api.cursor.com",
            description="The base URL for the Cursor Admin API (TAP_CURSOR_API_URL env var)",
        ),
        th.Property(
            "user_agent",
            th.StringType(nullable=True),
            description=(
                "A custom User-Agent header to send with each request (TAP_CURSOR_USER_AGENT env var). Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
    ).to_dict()

    def load_config(self, config: dict | None = None) -> dict:
        """Load configuration from environment variables and provided config.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            Configuration dictionary with environment variables loaded
        """
        if config is None:
            config = {}
            
        # Load from environment variables
        env_config = {
            "api_key": os.getenv("TAP_CURSOR_API_KEY"),
            "start_date": os.getenv("TAP_CURSOR_START_DATE"),
            "end_date": os.getenv("TAP_CURSOR_END_DATE"),
            "api_url": os.getenv("TAP_CURSOR_API_URL", "https://api.cursor.com"),
            "user_agent": os.getenv("TAP_CURSOR_USER_AGENT"),
        }
        
        # Remove None values from env_config
        env_config = {k: v for k, v in env_config.items() if v is not None}
        
        # Merge with provided config (provided config takes precedence)
        config.update(env_config)
        
        return super().load_config(config)

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
