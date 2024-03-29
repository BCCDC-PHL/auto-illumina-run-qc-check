import argparse
import collections
import math
import sys
import re
import json


def parse_read_summary_line(read_summary_line):
    """
    Parse a line from a read summary csv file into a dict.

    :param read_summary_line: A line from a read summary csv file.
    :type read_summary_line: str
    :return: A dict containing the parsed read summary line.
             Keys: ['ReadNumber', 'IsIndexed', 'TotalCycles', 'YieldTotal', 'ProjectedTotalYield', 'PercentAligned', 'ErrorRate', 'IntensityCycle1', 'PercentGtQ30']
    :rtype: dict[str, object]
    """
    parsed_read_summary_line = {}

    read_summary_line = read_summary_line.strip().split(',')

    headers_input_order = [
        'Level',
        'YieldTotal',
        'ProjectedTotalYield',
        'PercentAligned',
        'ErrorRate',
        'IntensityCycle1',
        'PercentGtQ30',
        'Occupancy',
    ]

    level_to_read_number = {
        'Read 1': 1,
        'Read 2': 2,
        'Read 2 (I)': 2,
        'Read 3 (I)': 3,
        'Read 3': 3,
        'Read 4': 4,
        'Non-indexed': 'NonIndexed',
        'Total': 'Total',
    }

    float_fields = [
        'ErrorRate',
        'PercentAligned',
        'Occupancy',
    ]

    headers_output_order = [
        'ReadNumber',
        'IsIndexed',
        'TotalCycles',
        'YieldTotal',
        'ProjectedTotalYield',
        'PercentAligned',
        'ErrorRate',
        'IntensityCycle1',
        'PercentGtQ30',
    ]

    for idx, header in enumerate(headers_input_order):
        if header == 'Level':
            parsed_read_summary_line['ReadNumber'] = level_to_read_number[read_summary_line[idx]]
            if re.search("(I)", read_summary_line[idx]):
                parsed_read_summary_line['IsIndexed'] = True
            else:
                parsed_read_summary_line['IsIndexed'] = False
        elif header == 'IntensityC1':
            parsed_read_summary_line[header] = int(read_summary_line[idx])
        elif header == 'ErrorRate':
            if read_summary_line[idx] == 'nan':
                parsed_read_summary_line[header] = 0
            else:
                parsed_read_summary_line[header] = float(read_summary_line[idx])
        else:
            parsed_read_summary_line[header] = float(read_summary_line[idx])

        parsed_read_summary_line.pop('Occupancy', None)
        parsed_read_summary_line_ordered = collections.OrderedDict(sorted(parsed_read_summary_line.items(), key=lambda x: headers_output_order.index(x[0])))
        
    return parsed_read_summary_line_ordered


def parse_read_summary(summary_lines):
    """
    Parse a read summary csv file into a list of dicts.

    :param summary_lines: A list of lines from a read summary csv file.
    :type summary_lines: list[str]
    :return: A list of dicts containing the parsed read summary.
             Keys: ['ReadNumber', 'IsIndexed', 'TotalCycles', 'YieldTotal', 'ProjectedTotalYield', 'PercentAligned', 'ErrorRate', 'IntensityCycle1', 'PercentGtQ30']
    :rtype: list[dict[str, object]]
    """
    read_summary = []

    header_line_num = 0
    for line in summary_lines:
        header_line_num += 1
        if re.match("^Level", line):
            break
    for line in summary_lines[header_line_num:]:
            if re.match("^Total", line):
                read_summary_line = parse_read_summary_line(line)
                read_summary.append(read_summary_line)
                break
            else:
                read_summary_line = parse_read_summary_line(line)
                read_summary.append(read_summary_line)
    
    return read_summary


def parse_read_line(read_line, read_number):
    """
    Parse a line from a read summary csv file into a dict.

    :param read_line: A line from a read summary csv file.
    :type read_line: str
    :param read_number: The read number.
    :type read_number: int
    :return: A dict containing the parsed read line.
             Keys: ['ReadNumber', 'LaneNumber', 'Surface', 'TileCount', 'Density', 'DensityDeviation', 'PercentPf', 'PercentPfDeviation', 'Reads', 'ReadsPf', 'PercentGtQ30', 'Yield', 'CyclesError', 'PercentAligned', 'PercentAlignedDeviation', 'ErrorRate', 'ErrorRateDeviation', 'ErrorRate35', 'ErrorRate35Deviation', 'ErrorRate75', 'ErrorRate75Deviation', 'ErrorRate100', 'ErrorRate100Deviation', 'IntensityCycle1', 'IntensityCycle1Deviation', 'PhasingSlope', 'PhasingOffset', 'PrePhasingSlope', 'PrePhasingOffset', 'ClusterDensity', 'Occupancy']
    :rtype: dict[str, object]
    """
    parsed_read_line = {}

    headers_input_order = [
        'LaneNumber',
        'Surface',
        'TileCount',
        'Density',
        'PercentPf',
        'LegacyPhasingPrephasingRate',
        'Phasing',
        'Prephasing',
        'Reads',
        'ReadsPf',
        'PercentGtQ30',
        'Yield',
        'CyclesError',
        'PercentAligned',
        'ErrorRate',
        'ErrorRate35',
        'ErrorRate75',
        'ErrorRate100',
        'Occupancy',
        'IntensityCycle1',
    ]

    headers_output_order = [
        'ReadNumber',
        'LaneNumber',
        'Surface',
        'TileCount',
        'Density',
        'DensityDeviation',
        'PercentPf',
        'PercentPfDeviation',
        'Reads',
        'ReadsPf',
        'PercentGtQ30',
        'Yield',
        'CyclesError',
        'PercentAligned',
        'PercentAlignedDeviation',
        'ErrorRate',
        'ErrorRateDeviation',
        'ErrorRate35',
        'ErrorRate35Deviation',
        'ErrorRate75',
        'ErrorRate75Deviation',
        'ErrorRate100',
        'ErrorRate100Deviation',
        'IntensityCycle1',
        'IntensityCycle1Deviation',
        'PhasingSlope',
        'PhasingOffset',
        'PrePhasingSlope',
        'PrePhasingOffset',
        'ClusterDensity',
        'Occupancy',
    ]

    average_stdev_fields = [
        'PercentAligned',
        'PercentPf',
        'Density',
        'ErrorRate',
        'ErrorRate35',
        'ErrorRate75',
        'ErrorRate100',
        'IntensityCycle1',
        'Occupancy',
    ]

    slash_fields = { 
        'Phasing': {
            'numerator_field': 'PhasingSlope',
            'denominator_field': 'PhasingOffset'
        },
        'Prephasing': {
            'numerator_field': 'PrePhasingSlope',
            'denominator_field': 'PrePhasingOffset'
        },
    }

    float_fields = [
        'PercentGtQ30',
        'Reads',
        'ReadsPf',
        'Yield',
    ]

    int_fields = [
        'ReadNumber',
        'LaneNumber',
        'TileCount',
    ]

    read_line_list = [record.strip() for record in read_line.strip().split(',')]
    parsed_read_line = dict(zip(headers_input_order, read_line_list))
    parsed_read_line['ReadNumber'] = read_number

    for field in average_stdev_fields:
        string_value = parsed_read_line[field]
        [average, stdev] = [float(value) for value in string_value.split(' +/- ')]
        deviation_field = field + 'Deviation'
        parsed_read_line[field] = average
        parsed_read_line[deviation_field] = stdev

    for field, num_denom in slash_fields.items():
        string_value = parsed_read_line[field]
        numerator_field = num_denom['numerator_field']
        denominator_field = num_denom['denominator_field']
        [numerator, denominator] = [float(value) for value in string_value.split(' / ')]
        parsed_read_line[numerator_field] = numerator
        parsed_read_line[denominator_field] = denominator
        parsed_read_line.pop(field, None)

    for field in float_fields:
        parsed_read_line[field] = float(parsed_read_line[field])

    for field in int_fields:
        parsed_read_line[field] = int(parsed_read_line[field])

    parsed_read_line['Density'] = int(float(parsed_read_line['Density'] * 1000))
    parsed_read_line['ClusterDensity'] = parsed_read_line['Density']
    parsed_read_line['Reads'] = int(float(parsed_read_line['Reads'] * 1000000))
    parsed_read_line['ReadsPf'] = int(float(parsed_read_line['ReadsPf'] * 1000000))

    parsed_read_line.pop('OccupancyDeviation', None)
    parsed_read_line.pop('LegacyPhasingPrephasingRate', None)

    for k, v in parsed_read_line.items():
        if type(v) is float and math.isnan(v):
            parsed_read_line[k] = 0

    parsed_read_line_ordered = collections.OrderedDict(sorted(parsed_read_line.items(), key=lambda x: headers_output_order.index(x[0])))

    return parsed_read_line_ordered


def parse_lanes_by_read(summary_lines):
    """
    Parse a read summary csv file into a list of dicts.

    :param summary_lines: A list of lines from a read summary csv file.
    :type summary_lines: list[str]
    :return: A list of dicts containing the parsed read summary.
             Keys: ['ReadNumber', 'LaneNumber', 'Surface', 'TileCount', 'Density', 'DensityDeviation', 'PercentPf', 'PercentPfDeviation', 'Reads', 'ReadsPf', 'PercentGtQ30', 'Yield', 'CyclesError', 'PercentAligned', 'PercentAlignedDeviation', 'ErrorRate', 'ErrorRateDeviation', 'ErrorRate35', 'ErrorRate35Deviation', 'ErrorRate75', 'ErrorRate75Deviation', 'ErrorRate100', 'ErrorRate100Deviation', 'IntensityCycle1', 'IntensityCycle1Deviation', 'PhasingSlope', 'PhasingOffset', 'PrePhasingSlope', 'PrePhasingOffset', 'ClusterDensity', 'Occupancy']
    :rtype: list[dict[str, object]]
    """
    lanes_by_read = []
    read_number = None

    for line in summary_lines:
        if re.match("^Read 1$", line):
            read_number = 1
        elif re.match("^Read 2$", line):
            read_number = 2
        elif re.match("^Read 2 \(I\)$", line):
            read_number = 2
        elif re.match("^Read 3 \(I\)$", line):
            read_number = 3
        elif re.match("^Read 4$", line):
            read_number = 4
        elif re.match("^Extracted", line) or re.match("^Called", line) or re.match("^Scored", line):
            read_number = None
        else:
            pass

        if read_number and not re.match("^Lane", line) and not re.match("^Read", line):
            parsed_read_line = parse_read_line(line, read_number)
            parsed_read_line['ReadNumber'] = read_number
        else:
            parsed_read_line = {}

        if parsed_read_line and parsed_read_line['Surface'] == '-':
            parsed_read_line.pop('Surface', None)
            lanes_by_read.append(parsed_read_line)

    return lanes_by_read


def parse_run_stats(summary_lines):
    """
    Parse a run stats csv file into a dict.

    :param summary_lines: A list of lines from a run stats csv file.
    :type summary_lines: list[str]
    :return: A dict containing the parsed run stats. Keys: ['PercentGtQ30', 'ProjectedTotalYield', 'YieldTotal', 'ErrorRate', 'PercentAligned', 'Occupancy', 'Reads']
    :rtype: dict[str, object]
    """
    run_stats = collections.OrderedDict()

    read_summary_headers = []
    read_summary_lines = []

    replaced_fields = {
        '%>=Q30': 'PercentGtQ30',
        'Projected Yield': 'ProjectedTotalYield',
        'Yield': 'YieldTotal',
        'Error Rate': 'ErrorRate',
        'Aligned': 'PercentAligned',
        '% Occupied': 'Occupancy',
        'Level': 'ReadNumber',
        'Intensity C1': 'IntensityCycle1',
    }

    level_to_read_number = {
        'Read 1': 1,
        'Read 2': 2,
        'Read 2 (I)': 2,
        'Read 3 (I)': 3,
        'Read 3': 3,
        'Read 4': 4,
        'Total': 'Total',
        'Non-Indexed': 'Non-Indexed',
    }

    headers_output_order = [
        'ReadNumber',
        'IsIndexed',
        'TotalCycles',
        'YieldTotal',
        'ProjectedTotalYield',
        'PercentAligned',
        'ErrorRate',
        'IntensityCycle1',
        'PercentGtQ30',
    ]

    for line in summary_lines:
        if re.match("^Level", line):
            read_summary_headers = re.split("\s*,", line.rstrip())

            for idx, header in enumerate(read_summary_headers):
                if header in replaced_fields:
                    read_summary_headers[idx] = replaced_fields[header]
            break
    for line in summary_lines:
        if re.match("^Total", line) or re.match("^Non-indexed", line):
            # read_summary_lines.append(re.split(",", line.rstrip()))
            break
        else:
            if re.match("^Read", line):
                read_summary_lines.append(re.split(",", line.rstrip()))

    read_summary = []
    for line in read_summary_lines:
        read_summary_line_dict = {}
        for idx, header in enumerate(read_summary_headers):
            if header == 'ReadNumber':
                read_summary_line_dict[header] = level_to_read_number[line[idx]]
                if re.search("(I)", line[idx]):
                    read_summary_line_dict['IsIndexed'] = True
                else:
                    read_summary_line_dict['IsIndexed'] = False
            elif header == 'IntensityC1':
                read_summary_line_dict[header] = int(line[idx])
            elif header == 'ErrorRate':
                if line[idx] == 'nan':
                    read_summary_line_dict[header] = 0
                else:
                    read_summary_line_dict[header] = float(line[idx])
            else:
                read_summary_line_dict[header] = float(line[idx])

        read_summary_line_dict.pop('Occupancy', None)
        read_summary_line_dict_ordered = collections.OrderedDict(sorted(read_summary_line_dict.items(), key=lambda x: headers_output_order.index(x[0])))

        read_summary.append(read_summary_line_dict_ordered)
                 
    return run_stats


def parse_interop_summary(summary_lines):
    """
    Parse an interop summary csv file into a dict.

    :param summary_lines: A list of lines from an interop summary csv file.
    :type summary_lines: list[str]
    :return: A dict containing the parsed interop summary. Keys: ['ClusterDensity', 'ErrorRate', 'IntensityCycle1', 'PercentAligned', 'PercentGtQ30', 'ProjectedTotalYield', 'YieldTotal', 'Reads', 'LanesByRead']
    :rtype: dict[str, object]
    """
    sequencingstats = {}
    read_summary = parse_read_summary(summary_lines)
    reads = [r for r in read_summary if isinstance(r['ReadNumber'], int)]

    for r in [r for r in read_summary if r['ReadNumber'] == 1]:
        keys = [
            'ErrorRate',
            'PercentGtQ30',
        ]
        for k in keys:
            sequencingstats[k + 'R1'] = r[k]

    for r in [r for r in read_summary if r['ReadNumber'] == 4]:
        keys = [
            'ErrorRate',
            'PercentGtQ30',
        ]
        for k in keys:
            sequencingstats[k + 'R2'] = r[k]
    
    for r in [r for r in read_summary if r['ReadNumber'] == 'NonIndexed']:
        keys = [
            'ErrorRate',
            'IntensityCycle1',
            'PercentAligned',
            'PercentGtQ30',
            'ProjectedTotalYield',
            'YieldTotal',
        ]
        for k in keys:
            sequencingstats['NonIndexed' + k] = r[k]

    for r in [r for r in read_summary if r['ReadNumber'] == 'Total']:
        keys = [
            'ErrorRate',
            'IntensityCycle1',
            'PercentAligned',
            'PercentGtQ30',
            'ProjectedTotalYield',
            'YieldTotal',
        ]
        for k in keys:
            sequencingstats[k] = r[k]
        
    lanes_by_read = parse_lanes_by_read(summary_lines)

    # The ClusterDensity and PercentPf fields are only present in the lanes_by_read list.
    # Lift them up to the top level of the dict, to make it easier to access them as run-level metrics.
    if len(lanes_by_read) > 0:
        if 'ClusterDensity' in lanes_by_read[0]:
            sequencingstats['ClusterDensity'] = lanes_by_read[0]['ClusterDensity']
        if 'PercentPf' in lanes_by_read[0]:
            sequencingstats['PercentPf'] = lanes_by_read[0]['PercentPf']

    sequencingstats['Reads'] = reads
    sequencingstats['LanesByRead'] = lanes_by_read

    return sequencingstats


def parse_run_parameters_xml(run_parameters_xml_path, instrument_type):
    """
    Parse a run parameters xml file into a dict.

    :param run_parameters_xml_path: The path to the run parameters xml file.
    :type run_parameters_xml_path: str
    :param instrument_type: The instrument type. One of ['miseq', 'nextseq'].
    :type instrument_type: str
    :return: A dict containing the parsed run parameters. Keys: ['flowcell_version']
    :rtype: dict[str, object]
    """
    run_parameters = {}
    with open(run_parameters_xml_path, 'r') as f:
        for line in f:
            line = line.strip()
            if instrument_type == 'miseq':
                if re.search("^<ReagentKitVersion>", line):
                    version = re.search("<ReagentKitVersion>(.*)</ReagentKitVersion>", line).group(1)
                    version_num = version.lstrip('Version')
                    run_parameters['flowcell_version'] = version_num
            elif instrument_type == 'nextseq':
                if re.search("^<FlowCellVersion>", line):
                    version_num = re.search("<FlowCellVersion>(.*)</FlowCellVersion>", line).group(1)
                    run_parameters['flowcell_version'] = version_num

    return run_parameters
