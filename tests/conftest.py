# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import gennex
import hoverpower
import resinf
import utilotest

import geostrat

pytest_plugins = ['pytester', 'xdist']  # pylint: disable=invalid-name

hoverpower.setup(geostrat.ROOT)
PACKAGE = geostrat.PACKAGE

RESOURCES = [
    (hoverpower.MASTER116_PDF, '95:105'),
    (hoverpower.MASTER089_PDF, '79:82'),
    (hoverpower.BACHELOR056_PDF, '45:55'),
    (hoverpower.BACHELOR063_PDF, '59:61'),
    (hoverpower.PAPER18_PDF, '0,7,14'),
    (hoverpower.BACHELOR037_PDF, '2,33,34,35,36'),
    (hoverpower.BOOK200_PDF, '4,24,25,26,27,82'),
    resinf.todo(
        hoverpower.BACHELOR067_PDF,
        pages='63',
        rawmaker='--char_margin=1.1',
    ),
]

WORKER = utilotest.worker_count(6, onci=len(RESOURCES))


def pytest_sessionstart(session):  # pylint:disable=W0613
    hoverpower.run()


def extract(resources):
    destination = hoverpower.generated()
    gennex.extract(
        resources,
        dest=destination,
        worker=WORKER,
        # groupme='--content',
        # headnote=True,
        # footnote=True,
        pagenumber=True,
        # cleanup=True,
    )
