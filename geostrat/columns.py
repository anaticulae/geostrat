# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""N-Column parser
===============
"""

import configo
import texmex
import utila


@utila.rename(navigator='ptn')
def parse(
    ptn: texmex.NavigatorMixin,
    column_count: int = 2,
    column_elements_min: int = 10,
    column_diff: float = 25.0,
    skip_overlapping: bool = False,
    data_adjust: bool = False,
) -> list:
    """Detect n-column_count columns and parse data.

    Hints: Use a high column_diff to join alternating text start together.

    Args:
        ptn(NavigatorMixin): current page
        column_count(int): number of columns
        column_elements_min(int): minimal count of data in every column
        column_diff(float): max x0 diff to fit in the same column
        skip_overlapping(bool): if True, the whole page must fit in
                                column-raster, if not None is returned
        data_adjust(bool): align data in horizonal lines
    Returns:
        list of columns with data
        None if extraction fails
    """
    if not ptn:
        # empty navigator
        return None
    assert column_count >= 1, str(column_count)
    assert (ptn.width / column_count) >= (2 * column_diff), (
        f'{(ptn.width / column_count)} >= {(2 * column_diff)}')
    marker = determine_marker(
        ptn,
        column_count=column_count,
        min_elements=column_elements_min,
        column_diff=column_diff,
    )
    if not marker:
        return None
    if len(marker) != column_count:
        utila.debug(f'invalid marker count; expected: {column_count} '
                    f'current: {len(marker)} page: {ptn.page}')
        utila.debug('skip column extraction')
        return None
    data = split_bymarker(
        ptn,
        marker,
        skip_overlapping=skip_overlapping,
        column_diff=column_diff,
    )
    if unbalanced_columns(data, ptn=ptn):
        utila.debug(f'unbalanced_columns, page: {ptn.page}')
        return None
    if skip_overlapping:
        if any(item is None for item in data):  # None is important here
            utila.debug('could not analyze, columns are mixed/ambigous')
            return None
    if data_adjust:
        data = adjust_data(data)
    return data


NAVIGATOR_NOT_IN_COLUMN_DATA = configo.HV_PERCENT_PLUS(default=92)


def unbalanced_columns(data, ptn) -> bool:
    if not all(data):
        return True
    column_content = utila.flat(data)
    valid = utila.rect_max([item.bounding for item in column_content])
    navigator_in_colum = [
        item for item in ptn if utila.rect_inside(valid, item.bounding)
    ]
    rate = utila.rate_rel(column_content, navigator_in_colum)
    if rate < NAVIGATOR_NOT_IN_COLUMN_DATA:
        utila.debug(f'column_content: {len(column_content)}, '
                    f'navigator_in_colum: {len(navigator_in_colum)} '
                    f'rate: {rate} page: {ptn.page}')
        return True
    return False


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
    """Filter items by x0 coordinate.

    Find items which are on a vertical line.
    """
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


def adjust_data(data, column=0) -> list:
    if not data:
        return []
    adjustment = [(item.bounding[1], item.bounding[3]) for item in data[column]]
    borders = [(current[0], after[0])
               for current, after in zip(adjustment[:-1], adjustment[1:])]
    if len(borders) <= 1:
        return []
    borders.append((borders[-1][1], utila.INF))
    result = []
    for border in borders:
        line = []
        for col in data:
            content = [
                item for item in col if utila.isinside(
                    value=(item.bounding[1] + item.bounding[3]) / 2,
                    left=border[0],
                    right=border[1],
                )
            ]
            line.append(tuple(content))
        result.append(tuple(line))
    return tuple(result)
