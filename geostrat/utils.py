# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib

import utila


def connect_text(items) -> str:
    """\
    >>> connect_text([''])
    ''
    """
    # TODO: REPLACE WITH MORE GENERAL APPRAOCH FROM A NICER PACKAGE
    with contextlib.suppress(AttributeError, TypeError):
        items = [item.text for item in items]
    items = [item.replace(utila.NEWLINE, ' ').strip() for item in items]
    # replace trennung
    items = [
        item[0:-1] if item and isminus(item[-1]) else item for item in items
    ]
    raw = ''.join(items)
    raw = raw.replace(utila.NEWLINE, ' ')
    return raw


def isminus(item):
    """\
    >>> isminus('-')
    True
    """
    return item in ('-', chr(173))
