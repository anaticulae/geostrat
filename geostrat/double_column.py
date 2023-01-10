# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
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

ADJUST_COLUMNS_TOLERENACE = configo.HV_FLOAT_PLUS(default=5.0)

COLUMNS_DIFF_MAX = configo.HV_FLOAT_PLUS(default=2.0)

COLUMNS_ELEMENTS_MIN = configo.HV_INT_PLUS(default=5)

LINE_GAP_MIN = configo.HV_FLOAT_PLUS(default=10.0)

LINES_DIFF_MAX = configo.HV_FLOAT_PLUS(default=2.0)

LINES_ELEMENTS_MIN = configo.HV_INT_PLUS(default=5)


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
    if not short_column or not description_column:
        utila.debug('no short or long column; skip strategy')
        return None
    overlapping = overlapping_column(short_column, description_column)
    if overlapping:
        # TODO: EXTEND ERROR MESSAGE
        utila.debug(overlapping)
        utila.debug('could not analyze, columns are mixed/ambigous')
        return None
    adjusted = adjust_columns(
        short_column,
        description_column,
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


def leftbounding(left, lasty1) -> list:
    result = []
    for first, second in zip(left[:-1], left[1:]):
        result.append((first.bounding[1], second.bounding[1]))
    # TODO: USE MAX DISTANCE?
    # TODO: IS LAST_Y1 THE BEST?
    # add last box defined by mean box height of items before
    # meandiff = statistics.mean([second - first for first, second in result])
    # result.append((result[-1][1], result[-1][1] + meandiff))
    result.append((result[-1][1], lasty1))
    return result


def adjust_columns(short_column, description_column, short_marker):
    """Adjust multi line columns. Group right side items to
    corresponding left side shortcut."""
    inside_all = all_columns([short_column, description_column])
    left = [
        item for item in inside_all
        if utila.near(item.bounding[0], short_marker)
    ]
    if len(left) <= 1:
        # require at least two elements to determine height of area
        return None
    right = []
    lasty1 = description_column[-1].bounding[3]  # y1 of last item
    leftgoal = leftbounding(left, lasty1)
    for start, end in leftgoal:
        # start, end = first.bounding[1], second.bounding[1]
        # give some tolerance
        start = start - ADJUST_COLUMNS_TOLERENACE
        right.append([
            item for item in description_column
            if start <= item.bounding[1] <= item.bounding[3] <= end
        ])
    if not left or not right:
        # could not adjust multiline colum
        return None
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
        diff=COLUMNS_DIFF_MAX,
        min_elements=COLUMNS_ELEMENTS_MIN,
    )
    if len(clustered) < 2:
        return None
    result = [item[0] for item in clustered]
    result = sorted(result)
    return result


def lines(page) -> utila.Numbers:
    line_distance = texmex.linedistances(page, noneatend=False)
    clustered = utila.max_distance(
        line_distance,
        diff=LINES_DIFF_MAX,
        min_elements=LINES_ELEMENTS_MIN,
    )
    result = [item[0] for item in clustered if item[0] >= LINE_GAP_MIN]
    # huggest element first
    result = sorted(result, reverse=True)
    return result
