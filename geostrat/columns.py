# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""N-Column parser
===============

# TODO: ADD OPTION TO ADJUST CONTENT HORIZONTALLY
"""

import texmex
import utila


def parse(
    navigator: texmex.NavigatorMixin,
    column_count: int = 2,
    column_elements_min: int = 10,
    column_diff: float = 25.0,
    skip_overlapping: bool = False,
) -> list:
    """Detect n-column_count columns and parse data.

    Hints: Use a hight column_diff to join alternating text start together.

    Args:
        navigator(NavigatorMixin): current page
        column_count(int): number of columns
        column_elements_min(int): minimal count of data in every column
        column_diff(float): max x0 diff to fit in the same column
        skip_overlapping(bool): if True, the whole page must fit in
                                column-raster, if not None is returned
    Returns:
        list of columns with data
        None if extraction fails
    """
    if not navigator:
        # empty navigator
        return None
    assert column_count >= 1, str(column_count)
    assert (navigator.width / column_count) >= (2 * column_diff), (
        f'{(navigator.width / column_count)} >= {(2 * column_diff)}')
    marker = determine_marker(
        navigator,
        column_count=column_count,
        min_elements=column_elements_min,
        column_diff=column_diff,
    )
    if not marker:
        return None

    if len(marker) != column_count:
        utila.debug(f'invalid marker count; expected: {column_count} '
                    f'current: {len(marker)} page: {navigator.page}')
        utila.debug('skip column extraction')
        return None

    data = split_bymarker(
        navigator,
        marker,
        skip_overlapping=skip_overlapping,
        column_diff=column_diff,
    )
    if skip_overlapping:
        if any(item is None for item in data):  # None is important here
            utila.debug('could not analyze, columns are mixed/ambigous')
            return None
    return data


def determine_marker(
    page,
    column_count: int,
    min_elements: int,
    column_diff: float,
) -> utila.Numbers:
    """Sort columns from left to right."""
    collected = [item.bounding[0] for item in page]  # x0 bounding

    clustered = utila.max_distance(
        collected,
        diff=column_diff,
        min_elements=min_elements,
    )

    if len(clustered) < column_count:
        return None

    result = [item[0] for item in clustered]
    result = sorted(result)
    return result


def split_bymarker(page, markers, skip_overlapping: bool, column_diff: float):
    assert markers
    markers = markers + [utila.INF]
    data = [
        column_data(
            page,
            marker,
            right,
            skip_overlapping=skip_overlapping,
            column_diff=column_diff,
        ) for marker, right in zip(markers[:-1], markers[1:])
    ]
    return data


def column_data(
    page,
    x0,
    x1,
    skip_overlapping: bool,
    column_diff: float = 25.0,
):
    """Filter items by x0 coordinate. Find items which are on a vertical
    line."""
    result = []
    for item in page:
        if not utila.near(item.bounding[0], x0, column_diff):
            continue
        if item.bounding[2] > x1:
            # right border outranges column
            if skip_overlapping:
                return None
            continue
        result.append(item)
    return result
