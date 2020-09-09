# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Parse double, triple, quadrupel column layouts.

Example:

.. code-block:: none

    [Ohm91]             OHMEDA MEDIZINTECHNIK: 2300 Finapress Blutdruckmonitor;
                        Bedienungsanleitung,Puchheim (1991)

    [Pau10]             PAULAT, Klaus Prof. Dr.: Regelungstechnik;
                        Vorlesungsskript SS2010, Hochschule Ulm (2010)
"""

import configo
import texmex
import utila


def parse_page(page) -> list:
    line_gaps = lines(page)
    if not line_gaps:
        utila.debug('no line gaps; skip strategy')
        return None

    marker = columns(page)
    if not marker:
        return None

    (short_column, description_column), short_mark = split_bymarker(
        page,
        marker,
    )

    overlapping = overlapping_column(short_column, description_column)
    if overlapping:
        # TODO: EXTEND ERROR MESSAGE
        utila.debug(overlapping)
        utila.debug('could not analyze, columns are mixed/ambigous')
        return None
    adjusted = adjust_columns(
        short_column,
        description_column,
        line_gaps,
        short_mark,
    )
    if adjusted is None:
        return None
    left, right = adjusted
    result = []
    for short, description in zip(left, right):
        description = [item.text.strip() for item in description]
        description = ' '.join(description)
        result.append((short.text, description))
    return result


def split_bymarker(page, marker):
    if not marker:
        return None
    short_marker = marker[0]
    description_marker = marker[1]
    short_column = column_data(page, short_marker)
    description_column = column_data(page, description_marker)
    return [short_column, description_column], short_marker


def overlapping_column(short, description):
    # TODO: INTRODUCE HASH BOUNDING METHOD
    shorts = set(str(item.bounding) for item in short)
    descriptions = set(str(item.bounding) for item in description)

    mixig = shorts & descriptions
    return mixig


def adjust_columns(short_column, description_column, line_gaps, short_marker):
    """Adjust multi line columns. Group right side items to
    corresponding left side shortcut."""
    inside_all = all_columns([short_column, description_column])
    left = [
        item for item in inside_all
        if utila.near(item.bounding[0], short_marker)
    ]
    right = []
    for first, second in zip(left[:-1], left[1:]):
        start, end = first.bounding[1], second.bounding[1]
        start = start - 5.0  # TODO: HOLY VALUE, give some tolerance
        right.append([
            item for item in description_column
            if start <= item.bounding[1] <= item.bounding[3] <= end
        ])
    if not left or not right:
        # could not adjust multiline colum
        return None

    # TODO: DIRTY, move to separate method
    # group last item
    start = left[-1].bounding[1]
    if len(line_gaps) >= 2:
        # biggest item is distance between multiline shortcut lines
        # second biggest item is normal line distance
        max_gap = line_gaps[1]
    else:
        # only single lines, no multiline shortcut lines
        max_gap = line_gaps[0]
    last = []
    for item in description_column:
        if item.bounding[1] < start:
            continue
        if (item.bounding[1] - start) > max_gap:
            # gap after content is to big
            break
        last.append(item)
        start = item.bounding[3]
    right.append(last)
    assert len(left) == len(right), 'could not parse both columns correctly'
    return left, right


def all_columns(items, vertical_diff: float = 6.0):
    """Select items which have a correspondet in every column with the
    same y1-baseline.

    Using y1 to use `baseline` of text cause lower z and upper Z have
    same base but the top coordinate can vary very much."""
    # TODO: ADD CHECK TO AVOID AMBIGOUS RESULTS AS A RESULT OF TOO MUCH
    # VERTICAL DIFF
    buckets = [set() for _ in items]
    for index, cdata in enumerate(items):
        for item in cdata:
            # bottom line position: y1
            buckets[index].add(item.bounding[3])
    result = []
    all_items = utila.flatten(items)
    for item in all_items:
        # search for items which are placed in both columns. There are the
        # bases for grouping text in vertical direction. See example above:
        # [Ohm91]        OHMEDA MEDIZINTECHNIK: 2300 Finapress Blutdruckmonitor;
        # [Pau10]        PAULAT, Klaus Prof. Dr.: Regelungstechnik;
        inside = [
            # any match in a column
            any(
                utila.near(
                    # bottom line position: y1
                    item.bounding[3],
                    ypos,
                    diff=vertical_diff,
                ) for ypos in bucket) for bucket in buckets
        ]
        if not all(inside):
            # check occurence in all columns
            continue
        if len([it for it in inside if it]) < 2:
            # not enough items in a line, avoid single column detection
            continue
        result.append(item)
    return result


# TODO: THIS HIGH DIFF IS REQUIRED FOR BACHELOR37 EXAMPLE, BECAUSE HIDDEN
# WHITESPACES MAKES ANALYSIS COMPLICATED -> TODO: IMPROVE PARSER
def column_data(page, x0, diff: float = 60.0):
    """Filter items by x0 coordinate. Find items which are on a vertical
    line."""
    result = []
    for item in page:
        if not utila.near(item.bounding[0], x0, diff):
            continue
        result.append(item)
    return result


def columns(page) -> utila.Numbers:
    """Sort columns from left to right."""
    collected = []
    for item in page:
        x0 = item.bounding[0]
        collected.append(x0)

    clustered = utila.max_distance(
        collected,
        diff=2.0,  # TODO: HOLY VALUE
        min_elements=5  # TODO: HOLY VALUE
    )
    if len(clustered) < 2:
        return None

    result = [item[0] for item in clustered]
    result = sorted(result)
    return result


MIN_LINE_GAP = configo.HV_FLOAT_PLUS(10.0)


def lines(page) -> utila.Numbers:
    line_distance = texmex.linedistances(page, noneatend=False)
    clustered = utila.max_distance(
        line_distance,
        diff=2.0,  # TODO: HOLY VALUE
        min_elements=5  # TODO: HOLY VALUE
    )
    result = [item[0] for item in clustered if item[0] >= MIN_LINE_GAP]
    # huggest element first
    result = sorted(result, reverse=True)
    return result
