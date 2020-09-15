# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Alternate TextLine Group
========================

Group items due analyse alternating line-text-feed changes.

We assume that we analyse only text-content. Therefore we can ignore
text which differs to much from standard text size.

Currently we compute the most 2 text feed groups. But in general we can
extend this algorithm to more `lining points`.

To few data on a single page
----------------------------

In some cases there can be to few data on a page to determine the lining
points. This can happen if you have only one bibliography on the last
bib page. In this case, we can use the lining points of pages parsed
before.

Requirements
------------

- oneline_text
- oneline_textpositions

-> OnelinePageTextNavigator

Example:

.. code-block:: none

    RÖLL, Franz J. (1998): Mythen und Symbole in populären Medien. Der wahrnehmungs
             orientierte Ansatz in der Medienpädagogik. Frankfurt a. Main: GEP.

    RYSSEL, Dirk (2012): Dreiakter/Dreiaktstruktur. In: Lexikon der Filmbegriffe. Online
             verfügbar unter: http://filmlexikon.uni-kiel.de/index.php?
             action=lexikon&tag= det&id=2401 [Letzter Zugriff: 28.10.2014].

    SARBIN, Theodore R. (Hg.) (1986): Narrative Psychology. The Storied Nature
            of Human Conduct. New York: Praeger.

    SARBIN, Theodore R. (1986): Introduction and Overview. In: Sarbin 1986, ix-xviii.

    SCHENK, Michael (32007): Medienwirkungsforschung. Tübingen: Mohr Siebeck.

Title/Content Item
------------------

.. code-block:: none

    Moskowitz, H. & Fiorentino, D. (2000a). A review of    TITLE_ITEM
        regarding the effects of alcohol on driving-rel    CONTENT_ITEM
        Concentrations of 0.08 grams per deciliter and     CONTENT_ITEM

"""

import dataclasses

import texmex
import utila

import geostrat.utils

MIN_LINE_ELEMENT = 2  # TODO: HOLY VALUE
MAX_LINE_DIFF = 10

MAX_TEXT_DIFF = 2.5


@dataclasses.dataclass
class ParserConfig:
    min_word_count: int = 1
    min_content_length: int = 1
    main_split: bool = True


def parse_pages(pages, config: ParserConfig = None) -> list:
    """Analyse multiple pages to extract alternating text.

    If there is to few content for a page given, no local
    `lining_points` can be determined. To solve this issue we determine
    the global linings for all pages and parse the page with to few data
    with them. We prefer local over global linings. The global linings
    are only a backup.
    """
    config = ParserConfig() if not config else config
    linings = external_lining_points(pages)
    result = []
    for page in pages:
        try:
            # prefer own lining points
            parsed = parse_page(page, config=config)
        except NoSingleLiningPoints:
            parsed = parse_page(page, lining_points=linings, config=config)
        result.append(parsed)
    result = unite_hurenkind(result)
    return result


def unite_hurenkind(pages: list) -> list:
    """Unite group which does not start with title with title of the
    page before.

    Assume that title starts with left item. TODO: SUPPORT LEFT, RIGHT,
    MULTIPLE TITLE.
    """
    if not pages:
        return pages
    feeding = []
    for page in pages:
        if not page:
            continue
        for bib in page:
            for item in bib:
                feeding.append(item.bounding[0])
    _, right = min(feeding), max(feeding)
    result = [pages[0]]
    for page in pages[1:]:
        if not page:
            # empty page
            result.append(page)
            continue
        if utila.near(page[0][0].bounding[0], right, diff=MAX_LINE_DIFF):
            # move hurenkind to page before
            result[-1][-1].extend(page[0])
            # remove hurenkind from current page
            result.append(page[1:])
        else:
            result.append(page)
    return result


def parse_page(page, lining_points=None, config: ParserConfig = None) -> list:  # pylint:disable=R1260,R0912
    """Iterate through lines in document.

    A group is separated by an alternating text feed. We skip all
    elements which are not part of most common feed or not part of most
    common font size.

    A group is closed when:

        * the text feed is equal than first element in group
        * an illegal text feed occurs
        * an illegal font size

    Hint: Keep in mind when extending to more than one group, that one
    group can contain other groups.
    """
    if not page:
        return None
    starts = group_line_start(page) if lining_points is None else lining_points
    if not starts:
        raise NoSingleLiningPoints('could not find enough lining points')

    if not config:
        config = ParserConfig()
    textsize = texmex.textsize_frompage(page)
    result = []
    current = None
    for line in page:
        x0 = line.bounding[0]
        if not utila.near(textsize, line.style.textsize(), MAX_TEXT_DIFF):
            # illegal font size
            current = None
            continue
        if current is None:
            if not inside(starts, x0):
                # illegal line feed
                # seek to start position or next valid item
                continue
            result.append([line])
            current = x0
        else:
            if not inside(starts, x0):
                # illegal line feed
                current = None
                continue
            if utila.near(current, x0, diff=MAX_LINE_DIFF):
                # alternating position
                current = x0
                result.append([line])
            else:
                if config.main_split:
                    # mainsplit: ensure to start with `Title Item`, see above.
                    # Ensure to handle `Hurenkind` correctly.
                    if utila.near(min(starts), x0, diff=MAX_LINE_DIFF):
                        # page starts with hurenkind
                        result.append([line])
                        current = x0
                    else:
                        result[-1].append(line)
                else:
                    # member of group
                    result[-1].append(line)
    # remove items with to few content
    result = [item for item in result if valid_content(item, config)]
    return result


def external_lining_points(pages):
    starts = [group_line_start(page) for page in pages]
    # remove page without clear lining points
    starts = [item for item in starts if item is not None]

    starts = utila.flatten(starts)
    clustered = utila.max_distance(
        starts,
        diff=MAX_LINE_DIFF,
        min_elements=1,
    )
    starts = [item.center for item in clustered]
    if len(starts) < 2:
        raise NoMultipleLiningPoints
    lining_points = (starts[0], starts[1])
    return lining_points


def valid_content(item, config):
    item = geostrat.utils.connect_text(item)
    if len(item) < config.min_content_length:
        return False
    if len(item.split()) < config.min_word_count:
        return False
    return True


def inside(starts, value):
    return any((utila.near(item, value, MAX_LINE_DIFF) for item in starts))


def group_line_start(page):
    x0_pos = [item.bounding[0] for item in page]
    clusters = utila.max_distance(
        x0_pos,
        diff=MAX_LINE_DIFF,
        min_elements=MIN_LINE_ELEMENT,
    )
    if len(clusters) < 2:
        return None

    # from left to right
    items = [item.center for item in clusters[0:2]]
    first, second = min(items), max(items)
    return first, second


class AlternateGeometryException(ValueError):
    pass


class NoSingleLiningPoints(AlternateGeometryException):
    pass


class NoMultipleLiningPoints(AlternateGeometryException):
    pass
