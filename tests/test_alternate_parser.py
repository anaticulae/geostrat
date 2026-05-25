# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hoverpower
import pytest
import serializeraw
import utilo
import utilotest

import geostrat


@pytest.mark.parametrize('page, expected', [
    (97, 14),
    (98, 14),
    (99, 15),
    (100, 3),
])
@utilotest.longrun
@utilotest.requires(hoverpower.MASTER116_PDF)
def test_parse_master116_page(page, expected):
    navigators = serializeraw.ptn_frompath(
        hoverpower.link(hoverpower.MASTER116_PDF),
        prefix='oneline',
        pages=page,
    )
    parsed = geostrat.al_parse_page(navigators[0])
    assert len(parsed) == expected, str(parsed)


@utilotest.longrun
@utilotest.requires(hoverpower.MASTER089_PDF)
def test_parse_master89_external_liningpoints():
    """Page 80 has to few content items to determine the lining points.

    Therefore the external lining points of page 79 are used to
    determine the bibliograpy on page 80.
    """
    pages = (79, 80)
    expected = (14, 1)
    parsed = load_and_parse(pages, hoverpower.MASTER089_PDF)
    for page_result, page_expected in zip(parsed, expected):
        assert len(page_result) == page_expected, str(page_result)


def test_parse_master89_external_liningpoints_single():
    pages = 79
    parsed = load_and_parse(pages, hoverpower.MASTER089_PDF)[0]
    assert len(parsed) == 14, str(parsed)


def test_parse_bachelor56_page49_whitespace_error():
    pages = (49)
    parsed = load_and_parse(pages, hoverpower.BACHELOR056_PDF)[0]
    assert len(parsed) == 8, str(parsed)


def test_parse_bachelor56_page51_hurenkind_error():
    pages = (51)
    parsed = load_and_parse(pages, hoverpower.BACHELOR056_PDF)[0]
    assert len(parsed) == 8, str(parsed)


def test_parse_bachelor56_page5051_hurenkind_unite():
    pages = (50, 51)
    parsed = load_and_parse(pages, hoverpower.BACHELOR056_PDF)
    flat = utilo.flat(parsed)
    assert len(flat) == 15, str(parsed)


def load_and_parse(pages, resources: str):
    utilotest.fixture_requires(resources)
    resources = hoverpower.link(resources)
    navigators = serializeraw.ptn_frompath(
        resources,
        prefix='oneline',
        pages=pages,
    )
    config = geostrat.ParserConfig(
        content_length_min=10,
        word_count_min=4,
    )
    parsed = geostrat.al_parse_pages(navigators, config=config)
    return parsed
