# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import power
import serializeraw

import geostrat


def paper18_page(page: int):
    navigators = serializeraw.create_pagetextnavigators_frompath(
        power.link(power.PAPER18_PDF),
        pages=(page,),
    )
    return navigators[0]


def test_paper18_page14_complete():
    page14 = paper18_page(14)
    parsed = geostrat.parse(page14, column_count=8)
    assert len(parsed) == 8
    assert parsed[0][0]  # first item in first column
    assert parsed[-1][-1]  # last item in last column


def test_paper18_page14_do_not_ignore_errors():
    page14 = paper18_page(14)
    parsed = geostrat.parse(
        page14,
        column_count=8,
        skip_overlapping=True,
    )
    assert not parsed


def test_paper18_page7():
    page7 = paper18_page(7)
    parsed = geostrat.parse(page7, column_count=3)
    assert len(parsed) == 3


def test_paper18_page0_no_column():
    page0 = paper18_page(0)
    parsed = geostrat.parse(page0, column_count=3)
    assert not parsed
