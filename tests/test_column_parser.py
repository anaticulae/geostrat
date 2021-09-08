# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import power
import serializeraw

import geostrat
import geostrat.double_column


def test_parse_column_bachelor63_page59():
    """Latex double column. Left side with [Hem10] pattern"""
    pages = (59)
    navigators = serializeraw.create_pagetextnavigators_frompath(
        power.link(power.BACHELOR063_PDF),
        # fill_empty=False,
        pages=pages,
    )
    parsed = geostrat.dc_parse_page(navigators[0])
    assert len(parsed) == 12, str(parsed)


def test_parse_column_bachelor63_page59_all_columns():
    """Latex double column. Left side with [Hem10] pattern"""
    pages = (59,)
    navigators = serializeraw.create_pagetextnavigators_frompath(
        power.link(power.BACHELOR063_PDF),
        # fill_empty=False,
        pages=pages,
    )
    page = navigators[0]
    marker = geostrat.dc_columns(page)
    (short, description), _ = geostrat.split_bymarker(page, marker)
    inside_all = geostrat.all_columns(
        [short, description],
        vertical_diff=5.0,
    )
    text = [item.text.strip() for item in inside_all]
    # reducing vertical diff leads to droping out of detection
    assert '[Ohm91]' in text, text


def test_extract_columns_bachelor37page33():
    source = power.link(power.BACHELOR037_PDF)
    ptn = serializeraw.create_pagetextnavigators_frompath(source, pages=(33,))
    ptn = ptn[0]
    parsed = geostrat.parse(ptn)
    # parse two columns
    assert len(parsed) == 2


def test_extract_columns_bachelor37page2():
    source = power.link(power.BACHELOR037_PDF)
    ptn = serializeraw.create_pagetextnavigators_frompath(source, pages=(2,))[0]
    parsed = geostrat.parse(ptn)
    # parse two columns
    assert len(parsed) == 2
    assert len(parsed[0]) == 11
    assert len(parsed[1]) == 20, str(parsed[1])


def test_extract_columns_bachelor37complete():
    source = power.link(power.BACHELOR037_PDF)
    ptns = serializeraw.create_pagetextnavigators_frompath(source)
    doubled = [page.page for page in ptns if geostrat.parse(page)]
    # it is possible that more than required pages can be inside
    inside = [item in doubled for item in [33, 34, 35, 36]]
    assert all(inside), str(inside)


def test_geometry_all_columns_bachelor37page2():
    source = power.link(power.BACHELOR037_PDF)
    ptn = serializeraw.create_pagetextnavigators_frompath(source, pages=(2,))[0]
    columns = [
        geostrat.double_column.column_data(ptn, x0=item)
        for item in geostrat.dc_columns(ptn)
    ]
    all_columns = geostrat.all_columns(columns)
    assert len(all_columns) == 20, str(all_columns)
