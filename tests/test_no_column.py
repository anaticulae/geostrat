# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import power
import pytest
import serializeraw
import utilatest

import geostrat


@pytest.mark.parametrize('data_adjust', [True, False])
@utilatest.requires(power.BOOK200_PDF)
def test_no_book200(data_adjust):
    source = power.link(power.BOOK200_PDF)
    ptns = serializeraw.ptn_frompath(source)
    for navigator in ptns:
        parsed = geostrat.parse(
            navigator,
            data_adjust=data_adjust,
        )
        assert not parsed, str(navigator.page)
