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

# Outputs

This tool will write a file named `qc_check_complete.json`, with the following format:

```
{
  "checked_metrics": [
    {
      "metric": "ErrorRate",
      "value": 0.34,
      "threshold": 3.0,
      "pass_above_or_below": "below",
      "pass_fail": "PASS"
    },
    {
      "metric": "PercentGtQ30",
      "value": 89.62,
      "threshold": 70.0,
      "pass_above_or_below": "above",
      "pass_fail": "PASS"
    },
    {
      "metric": "PercentPf",
      "value": 77.4,
      "threshold": 60.0,
      "pass_above_or_below": "above",
      "pass_fail": "PASS"
    }
  ],
  "overall_pass_fail": "PASS",
  "sequencing_run_id": "240101_VH00123_100_AAG4WXGB5",
  "instrument_type": "nextseq",
  "run_parameters": {
    "flowcell_version": "2"
  },
  "timestamp_qc_check_started": "2024-01-10T15:45:28.074190",
  "timestamp_qc_check_completed": "2024-01-10T15:45:28.152267"
}
```

It will also write a more detailed file named `<RUN_ID>_qc_metrics.json`.

The metrics at the top-level of this file are available to use for making QC pass/fail decisions.

```
{
  "ErrorRateR1": 0.24,
  "PercentGtQ30R1": 91.76,
  "ErrorRateR2": 0.44,
  "PercentGtQ30R2": 87.43,
  "NonIndexedErrorRate": 0.34,
  "NonIndexedIntensityCycle1": 126.0,
  "NonIndexedPercentAligned": 37.75,
  "NonIndexedPercentGtQ30": 89.59,
  "NonIndexedProjectedTotalYield": 37.54,
  "NonIndexedYieldTotal": 37.54,
  "ErrorRate": 0.34,
  "IntensityCycle1": 130.0,
  "PercentAligned": 37.75,
  "PercentGtQ30": 89.62,
  "ProjectedTotalYield": 39.8,
  "YieldTotal": 39.8,
  "ClusterDensity": 4974000,
  "PercentPf": 77.4,
  "Reads": [
    {
      "ReadNumber": 1,
      "IsIndexed": false,
      "YieldTotal": 18.77,
      "ProjectedTotalYield": 18.77,
      "PercentAligned": 38.08,
      "ErrorRate": 0.24,
      "IntensityCycle1": 130.0,
      "PercentGtQ30": 91.76
    },
    {
      "ReadNumber": 2,
      "IsIndexed": true,
      "YieldTotal": 1.13,
      "ProjectedTotalYield": 1.13,
      "PercentAligned": 0.0,
      "ErrorRate": 0,
      "IntensityCycle1": 133.0,
      "PercentGtQ30": 91.73
    },
    {
      "ReadNumber": 3,
      "IsIndexed": true,
      "YieldTotal": 1.13,
      "ProjectedTotalYield": 1.13,
      "PercentAligned": 0.0,
      "ErrorRate": 0,
      "IntensityCycle1": 133.0,
      "PercentGtQ30": 88.41
    },
    {
      "ReadNumber": 4,
      "IsIndexed": false,
      "YieldTotal": 18.77,
      "ProjectedTotalYield": 18.77,
      "PercentAligned": 37.43,
      "ErrorRate": 0.44,
      "IntensityCycle1": 123.0,
      "PercentGtQ30": 87.43
    }
  ],
  "LanesByRead": [
    {
      "ReadNumber": 1,
      "LaneNumber": 1,
      "TileCount": 32,
      "Density": 4974000,
      "DensityDeviation": 0.0,
      "PercentPf": 77.4,
      "PercentPfDeviation": 1.31,
      "Reads": 161440000,
      "ReadsPf": 124940000,
      "PercentGtQ30": 91.76,
      "Yield": 18.77,
      "CyclesError": "150",
      "PercentAligned": 38.08,
      "PercentAlignedDeviation": 0.22,
      "ErrorRate": 0.24,
      "ErrorRateDeviation": 0.05,
      "ErrorRate35": 0.08,
      "ErrorRate35Deviation": 0.02,
      "ErrorRate75": 0.12,
      "ErrorRate75Deviation": 0.03,
      "ErrorRate100": 0.15,
      "ErrorRate100Deviation": 0.03,
      "IntensityCycle1": 130.0,
      "IntensityCycle1Deviation": 10.0,
      "PhasingSlope": 0.092,
      "PhasingOffset": 1.326,
      "PrePhasingSlope": 0.122,
      "PrePhasingOffset": 0.592,
      "ClusterDensity": 4974000,
      "Occupancy": 96.48
    },
    {
      "ReadNumber": 2,
      "LaneNumber": 1,
      "TileCount": 32,
      "Density": 4974000,
      "DensityDeviation": 0.0,
      "PercentPf": 77.4,
      "PercentPfDeviation": 1.31,
      "Reads": 161440000,
      "ReadsPf": 124940000,
      "PercentGtQ30": 91.73,
      "Yield": 1.13,
      "CyclesError": "0",
      "PercentAligned": 0,
      "PercentAlignedDeviation": 0,
      "ErrorRate": 0,
      "ErrorRateDeviation": 0,
      "ErrorRate35": 0,
      "ErrorRate35Deviation": 0,
      "ErrorRate75": 0,
      "ErrorRate75Deviation": 0,
      "ErrorRate100": 0,
      "ErrorRate100Deviation": 0,
      "IntensityCycle1": 133.0,
      "IntensityCycle1Deviation": 8.0,
      "PhasingSlope": 0,
      "PhasingOffset": 0,
      "PrePhasingSlope": 0,
      "PrePhasingOffset": 0,
      "ClusterDensity": 4974000,
      "Occupancy": 96.48
    },
    {
      "ReadNumber": 3,
      "LaneNumber": 1,
      "TileCount": 32,
      "Density": 4974000,
      "DensityDeviation": 0.0,
      "PercentPf": 77.4,
      "PercentPfDeviation": 1.31,
      "Reads": 161440000,
      "ReadsPf": 124940000,
      "PercentGtQ30": 88.41,
      "Yield": 1.13,
      "CyclesError": "0",
      "PercentAligned": 0,
      "PercentAlignedDeviation": 0,
      "ErrorRate": 0,
      "ErrorRateDeviation": 0,
      "ErrorRate35": 0,
      "ErrorRate35Deviation": 0,
      "ErrorRate75": 0,
      "ErrorRate75Deviation": 0,
      "ErrorRate100": 0,
      "ErrorRate100Deviation": 0,
      "IntensityCycle1": 133.0,
      "IntensityCycle1Deviation": 7.0,
      "PhasingSlope": 0,
      "PhasingOffset": 0,
      "PrePhasingSlope": 0,
      "PrePhasingOffset": 0,
      "ClusterDensity": 4974000,
      "Occupancy": 96.48
    },
    {
      "ReadNumber": 4,
      "LaneNumber": 1,
      "TileCount": 32,
      "Density": 4974000,
      "DensityDeviation": 0.0,
      "PercentPf": 77.4,
      "PercentPfDeviation": 1.31,
      "Reads": 161440000,
      "ReadsPf": 124940000,
      "PercentGtQ30": 87.43,
      "Yield": 18.77,
      "CyclesError": "150",
      "PercentAligned": 37.43,
      "PercentAlignedDeviation": 0.36,
      "ErrorRate": 0.44,
      "ErrorRateDeviation": 0.12,
      "ErrorRate35": 0.15,
      "ErrorRate35Deviation": 0.04,
      "ErrorRate75": 0.24,
      "ErrorRate75Deviation": 0.05,
      "ErrorRate100": 0.29,
      "ErrorRate100Deviation": 0.06,
      "IntensityCycle1": 123.0,
      "IntensityCycle1Deviation": 8.0,
      "PhasingSlope": 0.093,
      "PhasingOffset": 2.133,
      "PrePhasingSlope": 0.117,
      "PrePhasingOffset": 1.237,
      "ClusterDensity": 4974000,
      "Occupancy": 96.48
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
