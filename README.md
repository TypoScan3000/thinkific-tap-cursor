# tap-cursor

`tap-cursor` is a Singer tap for extracting daily usage data from the Cursor Admin API, built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

This is a custom tap developed and owned by Thinkific's data team and is not currently published to Meltano Hub.

## Installation

This tap is designed to be used within a Meltano project. Install it in your Meltano project by manually adding a block to `meltano.yml` and running:

```bash
# Add to your meltano.yml or install directly
meltano install tap-cursor
```

**Note**: This tap is not intended to be run standalone. It should be installed and configured within a Meltano project for proper data pipeline orchestration.

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
meltano invoke tap-cursor --about
```

### Configure using environment variables

Settings can be configured through environment variables using the format `TAP_CURSOR_<SETTING_NAME>`, or in a `config` block in `meltano.yml`.  Environment variables take precedence.

### Source Authentication and Authorization

This tap requires a Cursor Admin API key for authentication. You can obtain this API key from a company Cursor admin.

The tap uses Basic Authentication with the API key as the username and an empty password.

### Required Settings

- `api_key`: Your Cursor Admin API key (can be set via `TAP_CURSOR_API_KEY` env var)

### Optional Settings

- `start_date`: The earliest record date to sync daily usage data (can be set via `TAP_CURSOR_START_DATE` env var, defaults to 30 days ago)
- `end_date`: The latest record date to sync daily usage data (can be set via `TAP_CURSOR_END_DATE` env var, defaults to today)

## Usage

This tap is designed to be used within a Meltano project for data pipeline orchestration.

### Running with Meltano

```bash
# Discover available streams
meltano invoke tap-cursor --discover

# Run the tap (with a target)
meltano run tap-cursor target-jsonl
```

### Configuration in Meltano

Configure the tap in your `meltano.yml`:

```yaml
extractors:
  [... other extractors ...]
  - name: tap-cursor
    namespace: tap_cursor
    python: '3.11'
    pip_url: git+https://github.com/thinkific/tap-gong.git@[SHA1 to pin to a commit]
    capabilities:
    - state
    - catalog
    - discover
    - about
    settings: # normally handled in Meltano hub, but this is a custom tap so Meltano needs this to introspect the env vars
    - name: api_key
      kind: password
      description: The Cursor Admin API key for authentication
    - name: start_date
      kind: date_iso8601
      description: The earliest record date to sync daily usage data
    - name: end_date
      kind: date_iso8601
      description: The latest record date to sync daily usage data
    # config: # normally we'd have configs but we rely on defaults or env vars for now
      # start_date: '2025-10-01T00:00:00Z' # Don't provide dates; the tap defaults to the max (30 days ago up to current date)
      # end_date: '2050-12-31T00:00:00Z'   # incremental sync replaces the latest (partial) date's data with full date when the next sync is run
    select:
    - daily_usage_data.*
    metadata:
      daily_usage_data:
        replication-method: INCREMENTAL
        replication-key: date
```

The `.env` file in your Meltano project should contain:
```bash
TAP_CURSOR_API_KEY=your_cursor_admin_api_key_here
TAP_CURSOR_START_DATE=2024-01-01T00:00:00Z # optional
TAP_CURSOR_END_DATE=2024-01-31T23:59:59Z # optional
```

**Note**: The API URL is hard-coded to `https://api.cursor.com` and is not separately configured.

### Incremental Replication

The `daily_usage_data` stream supports incremental replication using the `date` field as the replication key, stored in the configured state. This means:

- **First run**: Syncs data from the `start_date` (or 30 days ago if not specified) to `end_date` (or today)
- **Subsequent runs**: Only syncs new data since the last successful run

**Note**: Syncs are not resumable if interrupted - the tap must run to completion for the state to be properly updated.

Meltano automatically manages the state file (stored in Google Cloud Storage by default), which tracks the last replication key value processed.

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
