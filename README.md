# auto-illumina-run-qc-check
Automated run-level QC check for illumina sequencing runs.

# Installation

# Usage
Start the tool as follows:

```bash
auto-illumina-run-qc-check --config config.json
```

See the Configuration section of this document for details on preparing a configuration file.

More detailed logs can be produced by controlling the log level using the `--log-level` flag:

```bash
auto-illumina-run-qc-check --config config.json --log-level debug
```

# Configuration
This tool takes a single config file, in JSON format, with the following structure:

```json
{
    "excluded_runs_list": "excluded_runs.csv",
    "scan_interval_seconds": 10,
    "run_parent_dirs": [
	"/path/to/M00123/23",
	"/path/to/VH00123/23"
    ],
    "qc_thresholds": [
	{
	    "metric": "ErrorRate",
	    "threshold": 0.3,
	    "pass_above_or_below": "below",
	    "run_type": "MiSeq"
	},
	{
	    "metric": "ErrorRate",
	    "threshold": 0.3,
	    "pass_above_or_below": "below",
	    "run_type": "NextSeq"
	},
	{
	    "metric": "PercentGtQ30",
	    "threshold": 0.75,
	    "pass_above_or_below": "above",
	    "run_type": "MiSeq"
	},
	{
	    "metric": "PercentGtQ30",
	    "threshold": 0.75,
	    "pass_above_or_below": "above",
	    "run_type": "NextSeq"
	}
    ]
}
```

# Logging
This tool outputs [structured logs](https://www.honeycomb.io/blog/structured-logging-and-your-team/) in [JSON Lines](https://jsonlines.org/) format:

Every log line should include the fields:

- `timestamp`
- `level`
- `module`
- `function_name`
- `line_num`
- `message`

...and the contents of the `message` key will be a JSON object that includes at `event_type`. The remaining keys inside the `message` will vary by event type.

```json
{"timestamp": "2022-09-22T11:32:52.287", "level": "INFO", "module", "core", "function_name": "scan", "line_num", 56, "message": {"event_type": "scan_start"}}
```
