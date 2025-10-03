"""Stream type classes for tap-cursor."""

from __future__ import annotations

import typing as t
from datetime import datetime, timezone
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_cursor.client import CursorStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = resources.files(__package__) / "schemas"


class DailyUsageDataStream(CursorStream):
    """Define custom stream for Cursor daily usage data."""

    name = "daily_usage_data"
    path = "/teams/daily-usage-data"
    primary_keys: t.ClassVar[list[str]] = ["date"]
    replication_key = "date"
    rest_method = "POST"
    
    # Override the records_jsonpath to extract data from the response
    records_jsonpath = "$.data[*]"
    
    schema = th.PropertiesList(
        th.Property(
            "date",
            th.DateType,
            description="The date for the usage data",
        ),
        th.Property(
            "total_requests",
            th.IntegerType,
            description="Total number of requests made on this date",
        ),
        th.Property(
            "total_tokens",
            th.IntegerType,
            description="Total number of tokens consumed on this date",
        ),
        th.Property(
            "active_users",
            th.IntegerType,
            description="Number of active users on this date",
        ),
        th.Property(
            "requests_per_user",
            th.NumberType,
            description="Average requests per user on this date",
        ),
        th.Property(
            "tokens_per_user",
            th.NumberType,
            description="Average tokens per user on this date",
        ),
    ).to_dict()

    @override
    def prepare_request_payload(
        self,
        context: t.Any | None,
        next_page_token: t.Any | None,
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # Get start and end dates from config
        start_date = self.config.get("start_date")
        end_date = self.config.get("end_date")
        
        # Convert to epoch milliseconds as required by the API
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            start_epoch_ms = int(start_date.timestamp() * 1000)
        else:
            # Default to 30 days ago if no start date provided
            start_epoch_ms = int((datetime.now(timezone.utc).timestamp() - 30 * 24 * 60 * 60) * 1000)
            
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            end_epoch_ms = int(end_date.timestamp() * 1000)
        else:
            # Default to now if no end date provided
            end_epoch_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        return {
            "startDate": start_epoch_ms,
            "endDate": end_epoch_ms,
        }
