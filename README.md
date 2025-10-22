# tap-cursor

`tap-cursor` is a Singer tap for extracting daily usage data from the Cursor Admin API.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

This tap is designed to be used within a Meltano project. Install it in your Meltano project:

```bash
# Add to your meltano.yml or install directly
meltano add extractor tap-cursor

# Or install from GitHub
meltano add extractor tap-cursor --variant git+https://github.com/ORG_NAME/tap-cursor.git@main
```

**Note**: This tap is not intended to be run standalone. It should be installed and configured within a Meltano project for proper data pipeline orchestration.

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-cursor --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

This tap requires a Cursor Admin API key for authentication. You can obtain this API key from your Cursor account settings under the Admin API section.

The tap uses Basic Authentication with the API key as the username and an empty password.

### Required Environment Variables

- `TAP_CURSOR_API_KEY`: Your Cursor Admin API key (required)

### Optional Environment Variables

- `TAP_CURSOR_START_DATE`: The earliest record date to sync daily usage data (defaults to 30 days ago)
- `TAP_CURSOR_END_DATE`: The latest record date to sync daily usage data (defaults to today)

## Usage

This tap is designed to be used within a Meltano project for data pipeline orchestration.

### Running with Meltano

```bash
# Discover available streams
meltano invoke tap-cursor --discover

# Run the tap (with a target)
meltano run tap-cursor target-jsonl

# Run with specific configuration
meltano run tap-cursor target-jsonl --state-id=incremental
```

### Configuration in Meltano

Configure the tap in your `meltano.yml`:

```yaml
extractors:
  - name: tap-cursor
    variant: tap-cursor
    config:
      start_date: "2024-01-01T00:00:00Z"
      end_date: "2024-01-31T23:59:59Z"
```

**Note**: The API URL is hard-coded to `https://api.cursor.com` and cannot be configured.

Additionally, the start and end date can also be set via envrionment variables.  Env vars take precendence over the config in meltano.yml.

### Incremental Replication

The `daily_usage_data` stream supports incremental replication using the `date` field as the replication key. This means:

- **First run**: Syncs data from the `start_date` (or 30 days ago if not specified) to `end_date` (or today)
- **Subsequent runs**: Only syncs new data since the last successful run
- **Efficient**: Avoids re-syncing historical data on each run

**Note**: Syncs are not resumable if interrupted - the tap must run to completion for the state to be properly updated.

To use incremental replication in Meltano:

```bash
# First run - syncs historical data
meltano run tap-cursor target-jsonl

# Subsequent runs - only syncs new data since last run
meltano run tap-cursor target-jsonl --state-id=incremental
```

Meltano automatically manages the state file, which tracks the last replication key value processed.

### Environment Variable Configuration

Set the following environment variables in your Meltano project:

```bash
export TAP_CURSOR_API_KEY="your_cursor_admin_api_key_here"
export TAP_CURSOR_START_DATE="2024-01-01T00:00:00Z"
export TAP_CURSOR_END_DATE="2024-01-31T23:59:59Z"
```

Or create a `.env` file in your Meltano project directory:

```bash
# Create .env file in your Meltano project
TAP_CURSOR_API_KEY=your_cursor_admin_api_key_here
TAP_CURSOR_START_DATE=2024-01-01T00:00:00Z
TAP_CURSOR_END_DATE=2024-01-31T23:59:59Z
```

### Data Schema

The tap extracts daily usage data with the following fields:

- `date`: The date for the usage data
- `total_requests`: Total number of requests made on this date
- `total_tokens`: Total number of tokens consumed on this date
- `active_users`: Number of active users on this date
- `requests_per_user`: Average requests per user on this date
- `tokens_per_user`: Average tokens per user on this date

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

Prerequisites:

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and
then run:

```bash
uv run pytest
```

You can also test the `tap-cursor` CLI interface directly using `uv run`:

```bash
uv run tap-cursor --help
```

### Testing with [Meltano](https://www.meltano.com)

This tap is designed to be used within a Meltano project. To test it:

1. **Create a new Meltano project** (if you don't have one):
```bash
# Install meltano
uv tool install meltano

# Initialize a new meltano project
meltano init my-cursor-project
cd my-cursor-project
```

2. **Add this tap to your Meltano project**:
```bash
# Add the tap
meltano add extractor tap-cursor

# Add a target (e.g., JSONL for testing)
meltano add loader target-jsonl
```

3. **Configure and test**:
```bash
# Configure the tap
meltano config tap-cursor set api_key "your_api_key_here"

# Test discovery
meltano invoke tap-cursor --discover

# Run a test pipeline
meltano run tap-cursor target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
