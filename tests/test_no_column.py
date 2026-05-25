# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import hoverpower
import pytest
import serializeraw
import utilotest

import geostrat


@pytest.mark.parametrize('data_adjust', [True, False])
@utilotest.requires(hoverpower.BOOK200_PDF)
def test_no_book200(data_adjust):
    source = hoverpower.link(hoverpower.BOOK200_PDF)
    ptns = serializeraw.ptn_frompath(source)
    for navigator in ptns:
        parsed = geostrat.parse(
            navigator,
            data_adjust=data_adjust,
        )
        assert not parsed, str(navigator.page)
