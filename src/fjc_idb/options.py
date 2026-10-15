"""Default settings for importing, parsing, and exporting FJC IDB data.

These values are the defaults for `run`, `parse_data`, and the command line.
Change them here to change the defaults everywhere.

"""
from __future__ import annotations

import pathlib

# Whether to add agencies from the APPELLAN and APPELLEE columns when no
# AGENCY is present.
_ADD_AGENCIES_FROM_PARTIES: bool = True
# Whether to change the court names to strings or leave them as numbers.
_CHANGE_COURT_TO_STRING: bool = True
# Location of the root data folder
_DATA_FOLDER: pathlib.Path = (
    pathlib.Path(__file__).parents[4] / 'data' / 'courts' / 'fjc_idb')
_DATE_FORMAT: str = '%Y-%m-%d'
# FJC web pages that link to the yearly files for each case type.
_DATASET_PAGES: dict[str, str] = {
    'appellate': (
        'https://www.fjc.gov/research/idb/'
        'appellate-cases-filed-terminated-and-pending-fy-2008-present'),
    'civil': (
        'https://www.fjc.gov/research/idb/'
        'civil-cases-filed-terminated-and-pending-sy-1988-present'),
    'criminal': (
        'https://www.fjc.gov/research/idb/'
        'criminal-defendants-filed-terminated-and-pending-fy-1996-present')}
# Seconds to wait for the FJC website before giving up on a download.
_DOWNLOAD_TIMEOUT: int = 300
_ENCODING: str = 'latin-1'
# Whether to correct misspelled city names from the FJC codebook.
_FIX_CITY_SPELLINGS: bool = True
_MISSING_CODES: tuple[str | int, ...] = ('-8', -8)
_MISSING_DATE: str = '1900-01-01'
_PENDING_COLUMN: str = 'TAPEYEAR'
_PENDING_YEAR: int = 2099
_RENAME_COLUMNS: bool = True
_SOURCE_PREFIXES: dict[str, str] = {
    'appellate': 'ap',
    'civil': 'cv',
    'criminal': 'cr'}
