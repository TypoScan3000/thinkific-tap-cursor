"""Stream type classes for tap-cursor."""

from __future__ import annotations

import typing as t
from datetime import datetime, timezone, timedelta
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers
from typing_extensions import override

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
            th.DateTimeType,
            description="Date in epoch milliseconds",
        ),
        th.Property(
            "isActive",
            th.BooleanType,
            description="User active on this day",
        ),
        th.Property(
            "totalLinesAdded",
            th.IntegerType,
            description="Lines of code added",
        ),
        th.Property(
            "totalLinesDeleted",
            th.IntegerType,
            description="Lines of code deleted",
        ),
        th.Property(
            "acceptedLinesAdded",
            th.IntegerType,
            description="Lines added from accepted AI suggestions",
        ),
        th.Property(
            "acceptedLinesDeleted",
            th.IntegerType,
            description="Lines deleted from accepted AI suggestions",
        ),
        th.Property(
            "totalApplies",
            th.IntegerType,
            description="Apply operations",
        ),
        th.Property(
            "totalAccepts",
            th.IntegerType,
            description="Accepted suggestions",
        ),
        th.Property(
            "totalRejects",
            th.IntegerType,
            description="Rejected suggestions",
        ),
        th.Property(
            "totalTabsShown",
            th.IntegerType,
            description="Tab completions shown",
        ),
        th.Property(
            "totalTabsAccepted",
            th.IntegerType,
            description="Tab completions accepted",
        ),
        th.Property(
            "composerRequests",
            th.IntegerType,
            description="Composer requests",
        ),
        th.Property(
            "chatRequests",
            th.IntegerType,
            description="Chat requests",
        ),
        th.Property(
            "agentRequests",
            th.IntegerType,
            description="Agent requests",
        ),
        th.Property(
            "cmdkUsages",
            th.IntegerType,
            description="Command palette (Cmd+K) uses",
        ),
        th.Property(
            "subscriptionIncludedReqs",
            th.IntegerType,
            description="Subscription requests",
        ),
        th.Property(
            "apiKeyReqs",
            th.IntegerType,
            description="API key requests",
        ),
        th.Property(
            "usageBasedReqs",
            th.IntegerType,
            description="Pay-per-use requests",
        ),
        th.Property(
            "bugbotUsages",
            th.IntegerType,
            description="Bug detection uses",
        ),
        th.Property(
            "mostUsedModel",
            th.StringType,
            description="Most frequent AI model",
        ),
        th.Property(
            "applyMostUsedExtension",
            th.StringType,
            description="Most used file extension for applies",
        ),
        th.Property(
            "tabMostUsedExtension",
            th.StringType,
            description="Most used file extension for tabs",
        ),
        th.Property(
            "clientVersion",
            th.StringType,
            description="Cursor version",
        ),
        th.Property(
            "email",
            th.StringType,
            description="User email",
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
        # Get start date from incremental replication or config
        starting_timestamp = self.get_starting_timestamp(context)
        
        if starting_timestamp:
            # Use the last replication key value for incremental sync
            # Align to midnight UTC for date boundary consistency
            start_date = starting_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            start_epoch_ms = int(start_date.timestamp() * 1000)
            self.logger.info(f"Using incremental start date: {start_date}")
        else:
            # First run or no state - use config or default
            start_date = self.config.get("start_date")
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                # Align to midnight UTC for date boundary consistency
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                start_epoch_ms = int(start_date.timestamp() * 1000)
            else:
                # Default to 30 days ago if no start date provided
                thirty_days_ago = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
                start_epoch_ms = int(thirty_days_ago.timestamp() * 1000)
            self.logger.info(f"Using config/default start date: {start_date or '30 days ago'}")
        
        # Get end date from config
        end_date = self.config.get("end_date")
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            # Align to midnight UTC for date boundary consistency
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_epoch_ms = int(end_date.timestamp() * 1000)
        else:
            # Default to yesterday to ensure we only pull complete days of data
            yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end_epoch_ms = int(yesterday.timestamp() * 1000)
        
        return {
            "startDate": start_epoch_ms,
            "endDate": end_epoch_ms,
        }

    @override
    def post_process(
        self,
        row: dict,
        context: t.Any | None = None,
    ) -> dict | None:
        """Convert epoch milliseconds to datetime for replication key.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        # Convert epoch milliseconds to datetime for the replication key
        if "date" in row and row["date"] is not None:
            # Convert epoch milliseconds to datetime
            row["date"] = datetime.fromtimestamp(row["date"] / 1000, tz=timezone.utc)
        
        return row


class MembersStream(CursorStream):
    """Define custom stream for Cursor team members."""

    name = "members"
    path = "/teams/members"
    primary_keys: t.ClassVar[list[str]] = ["email"]
    rest_method = "GET"
    
    # Override the records_jsonpath to extract data from the response
    records_jsonpath = "$.teamMembers[*]"
    
    schema = th.PropertiesList(
        th.Property(
            "name",
            th.StringType,
            description="Member's name",
        ),
        th.Property(
            "email",
            th.StringType,
            description="Member's email address",
        ),
        th.Property(
            "role",
            th.StringType,
            description="Member's role in the team",
        ),
    ).to_dict()
