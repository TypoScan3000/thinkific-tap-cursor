# tap-cursor

`tap-cursor` is a Singer tap for extracting daily usage data from the Cursor Admin API.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPI repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPI:

```bash
uv tool install tap-cursor
```

Install from GitHub:

```bash
uv tool install git+https://github.com/ORG_NAME/tap-cursor.git@main
```

-->

## Configuration

### Accepted Config Options

<!--
Developer TODO: Provide a list of config options accepted by the tap.

This section can be created by copy-pasting the CLI output from:

```
tap-cursor --about --format=markdown
```
-->

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

- `TAP_CURSOR_API_URL`: The Cursor Admin API base URL (defaults to "https://api.cursor.com")
- `TAP_CURSOR_START_DATE`: The earliest record date to sync daily usage data (defaults to 30 days ago)
- `TAP_CURSOR_END_DATE`: The latest record date to sync daily usage data (defaults to today)
- `TAP_CURSOR_USER_AGENT`: Custom User-Agent header for requests

## Usage

You can easily run `tap-cursor` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-cursor --version
tap-cursor --help
tap-cursor --discover > ./catalog.json
```

Note: When using environment variables, you don't need to specify a `--config` parameter as the tap will automatically load configuration from environment variables.

### Incremental Replication

The `daily_usage_data` stream supports incremental replication using the `date` field as the replication key. This means:

- **First run**: Syncs data from the `start_date` (or 30 days ago if not specified) to `end_date` (or today)
- **Subsequent runs**: Only syncs new data since the last successful run
- **Efficient**: Avoids re-syncing historical data on each run

**Note**: Syncs are not resumable if interrupted - the tap must run to completion for the state to be properly updated.

To use incremental replication:

```bash
# First run - syncs historical data
tap-cursor --config config.json > output.jsonl

# Subsequent runs - only syncs new data since last run
tap-cursor --config config.json --state state.json > output.jsonl
```

The tap automatically manages the state file, which tracks the last replication key value processed.

### Environment Variable Configuration

Set the following environment variables for your Cursor Admin API credentials:

```bash
export TAP_CURSOR_API_KEY="your_cursor_admin_api_key_here"
export TAP_CURSOR_API_URL="https://api.cursor.com"
export TAP_CURSOR_START_DATE="2024-01-01T00:00:00Z"
export TAP_CURSOR_END_DATE="2024-01-31T23:59:59Z"
export TAP_CURSOR_USER_AGENT="tap-cursor/1.0.0"
```

Or create a `.env` file in your working directory:

```bash
# Copy the example file and fill in your values
cp .env.example .env

# Edit the .env file with your actual credentials
TAP_CURSOR_API_KEY=your_cursor_admin_api_key_here
TAP_CURSOR_API_URL=https://api.cursor.com
TAP_CURSOR_START_DATE=2024-01-01T00:00:00Z
TAP_CURSOR_END_DATE=2024-01-31T23:59:59Z
TAP_CURSOR_USER_AGENT=tap-cursor/1.0.0
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

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
uv tool install meltano
# Initialize meltano within this directory
cd tap-cursor
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-cursor --version

# OR run a test ELT pipeline:
meltano run tap-cursor target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
