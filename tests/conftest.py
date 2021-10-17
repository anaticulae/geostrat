# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import genex
import power

import geostrat

pytest_plugins = ['pytester', 'xdist']  # pylint: disable=invalid-name

power.setup(geostrat.ROOT)
PACKAGE = geostrat.PACKAGE

RESOURCES = [
    (power.MASTER116_PDF, '95:105'),
    (power.MASTER089_PDF, '79:82'),
    (power.BACHELOR056_PDF, '45:55'),
    (power.BACHELOR063_PDF, '59:61'),
    (power.PAPER18_PDF, '0,7,14'),
    (power.BACHELOR037_PDF, '2,33,34,35,36'),
]

WORKER = 6


def pytest_sessionstart(session):  # pylint:disable=W0613
    power.run()


def extract(resources):
    destination = power.generated()
    genex.extract(
        resources,
        destination=destination,
        worker=WORKER,
        groupme='--footer --content --pagenumbers',
        pages=':',
    )
