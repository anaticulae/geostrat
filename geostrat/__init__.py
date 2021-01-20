#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

from geostrat.alternate import AlternateGeometryException
from geostrat.alternate import NoMultipleLiningPoints
from geostrat.alternate import NoSingleLiningPoints
from geostrat.alternate import ParserConfig
from geostrat.alternate import parse_page as al_parse_page
from geostrat.alternate import parse_pages as al_parse_pages
from geostrat.columns import parse
from geostrat.double_column import all_columns
from geostrat.double_column import columns as dc_columns
from geostrat.double_column import parse_page as dc_parse_page
from geostrat.double_column import split_bymarker
from geostrat.utils import connect_text

__version__ = '1.1.9'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGE = 'geostrat'
