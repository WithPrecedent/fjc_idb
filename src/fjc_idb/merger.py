"""Merges the appellate data with the civil and criminal district data.

An appeal from a district court case is matched with the district court's
record of that case:

- Appeals from civil cases (see `rules.district_civil_appeal_types`) are
  matched with the civil files by district and docket number.
- Appeals from criminal cases (see `rules.district_criminal_appeal_types`) are
  matched with the criminal files by district, docket number, and defendant
  number. An appeal without a defendant number is matched only when the docket
  has a single defendant.

Reopened, remanded, and transferred cases can have several district records
with the same docket number. An appeal is matched with the latest record filed
on or before the notice of appeal or, if none was, with the latest record.

The district columns are added with the prefix 'district_', except those that
only repeat the match keys or the appellate data (see
`rules.redundant_civil_columns` and `rules.redundant_criminal_columns`). The
added 'district_match' column says whether each appeal was matched with a
'civil' or 'criminal' record.

"""

from __future__ import annotations

import datetime as dt
import logging
import pathlib
from typing import Any

import camina
import pandas as pd

from . import main, options, rules

logger = logging.getLogger(__name__)

_PREFIX = 'district_'


def merge_district(
    start_year: int,
    stop_year: int | None = None,
    data_folder: str | pathlib.Path = options._DATA_FOLDER,
    *,
    fix_city_spellings: bool = options._FIX_CITY_SPELLINGS,
    export: bool = True) -> pd.DataFrame:
    """Merges the appellate data with the civil and criminal district data.

    The appellate, civil, and criminal files for the same range of years are
    used, so an appeal can only be matched with a district case that was
    terminated in that range or was still pending. The civil and criminal files
    are read one year at a time, keeping only the records of appealed cases.

    The merged data is saved in the appellate folder as
    'fjc_idb_appellate_with_district_data_{start_year}_{stop_year}.csv'. Columns
    always have their descriptive names.

    Args:
        start_year: The first statistical year to include.
        stop_year: The last statistical year to include. Defaults to None, in
            which case the current year is used.
        data_folder: The path to the folder containing the FJC IDB dataset.
            Defaults to options._DATA_FOLDER.
        fix_city_spellings: Whether to correct misspelled city names from the
            FJC codebook. Defaults to options._FIX_CITY_SPELLINGS.
        export: Whether to save the merged data to a CSV file. Defaults to
            True.

    Returns:
        pd.DataFrame: The appellate data with the matched district columns.

    Examples:
        >>> import fjc_idb
        >>> fjc_idb.merge_district(2008, 2026)  # doctest: +SKIP

    """
    stop_year = stop_year or dt.datetime.now(tz = dt.UTC).year
    root: pathlib.Path = camina.pathlibify(data_folder)
    appellate_folder = main._get_data_path('appellate', root)
    appeals = main.parse_data(
        main.import_data('appellate', start_year, stop_year, appellate_folder),
        'appellate',
        fix_city_spellings = fix_city_spellings)
    civil = _match(
        appeals,
        _get_district_records(
            'civil', appeals, start_year, stop_year, root,
            fix_city_spellings = fix_city_spellings),
        rules.district_civil_appeal_types,
        ['docket'])
    criminal = _match(
        appeals,
        _get_district_records(
            'criminal', appeals, start_year, stop_year, root,
            fix_city_spellings = fix_city_spellings),
        rules.district_criminal_appeal_types,
        ['docket', 'defendant_number'])
    added = _get_added_columns(civil, criminal)
    merged = appeals.join(added)
    logger.info(
        'Matched %s of %s appeals with district records.',
        merged[f'{_PREFIX}match'].notna().sum(), len(merged))
    if export:
        replacements: dict[str, Any] = {
            spec.name: spec.missing_replacement
            for spec in main._get_columns('appellate').values()}
        replacements |= {
            name: 'NA' for name in added.columns
            if added[name].dtype.kind == 'M'}
        file_name = (
            f'fjc_idb_appellate_with_district_data_{start_year}_{stop_year}'
            '.csv')
        main.export_data(merged, appellate_folder, file_name, replacements)
    return merged


""" Private Functions """


def _get_added_columns(
    civil: pd.DataFrame,
    criminal: pd.DataFrame) -> pd.DataFrame:
    """Returns the district columns to add to the appellate data.

    Columns that the civil and criminal records share (such as 'filing_date')
    are combined into one column, since each appeal matches only one record.

    Args:
        civil: The matched civil records, indexed like the appellate data.
        criminal: The matched criminal records, indexed like the appellate
            data.

    Returns:
        pd.DataFrame: The district columns, with 'district_match' first.

    """
    civil = civil.drop(
        columns = [c for c in rules.redundant_civil_columns if c in civil])
    criminal = criminal.drop(columns = [
        c for c in rules.redundant_criminal_columns if c in criminal])
    added = pd.concat(
        [civil.assign(match = 'civil'), criminal.assign(match = 'criminal')])
    columns = ['match', *dict.fromkeys([*civil.columns, *criminal.columns])]
    added = added[columns]
    added.columns = [f'{_PREFIX}{name}' for name in columns]
    return added


def _get_district_records(
    case_type: str,
    appeals: pd.DataFrame,
    start_year: int,
    stop_year: int,
    root: pathlib.Path,
    *,
    fix_city_spellings: bool) -> pd.DataFrame:
    """Returns the district records with the docket of an appeal.

    The yearly files are parsed one at a time, keeping only the records whose
    district and docket number match an appeal.

    Args:
        case_type: 'civil' or 'criminal'.
        appeals: The parsed appellate data.
        start_year: The first statistical year to include.
        stop_year: The last statistical year to include.
        root: The path to the folder containing the FJC IDB dataset.
        fix_city_spellings: Whether to correct misspelled city names.

    Returns:
        pd.DataFrame: The matching district records, in the order of the
            yearly files.

    """
    keys = pd.MultiIndex.from_frame(
        appeals[['district_of_origin', 'district_docket']].dropna())
    folder = main._get_data_path(case_type, root)
    files = main._get_files(case_type, start_year, stop_year, folder)
    records = []
    for index, file in enumerate(files):
        data = main._import_file(file, keep_pending = index == len(files) - 1)
        data = main.parse_data(
            data, case_type, fix_city_spellings = fix_city_spellings)
        found = pd.MultiIndex.from_frame(
            data[['district', 'docket']].astype('string')).isin(keys)
        records.append(data[found])
    return pd.concat(records, ignore_index = True)


def _match(
    appeals: pd.DataFrame,
    records: pd.DataFrame,
    appeal_types: list[str],
    keys: list[str]) -> pd.DataFrame:
    """Matches appeals with one district record each.

    Args:
        appeals: The parsed appellate data.
        records: The district records that might match an appeal.
        appeal_types: The appeal types matched with `records`.
        keys: The columns of `records` matched with the appellate district
            docket number and, for criminal records, defendant number. The
            district is always matched.

    Returns:
        pd.DataFrame: The matched records, indexed like the appellate data.

    """
    names = {
        'docket': 'district_docket',
        'defendant_number': 'criminal_defendant_number'}
    candidates = appeals.loc[
        appeals['appeal_type'].isin(appeal_types)
        & appeals['district_docket'].notna(),
        ['district_of_origin', *(names[key] for key in keys), 'appeal_date']]
    records = records.assign(_order = range(len(records)))
    # pandas joins treat missing keys as equal, so they are left out here.
    complete = candidates[[names[key] for key in keys]].notna().all(axis = 1)
    matched = _join(candidates[complete], records, keys, names)
    if 'defendant_number' in keys:
        # Appeals without a defendant number match a docket with one defendant.
        without = candidates[candidates['criminal_defendant_number'].isna()]
        found = _join(without, records, ['docket'], names)
        defendants = found.groupby('_appeal')['defendant_number'].nunique()
        single = defendants[defendants == 1].index
        matched = pd.concat([matched, found[found['_appeal'].isin(single)]])
    # Prefer the latest record filed on or before the notice of appeal.
    eligible = (
        matched['appeal_date'].isna()
        | (matched['filing_date'] <= matched['appeal_date']))
    matched = (
        matched.assign(_eligible = eligible)
        .sort_values(['_appeal', '_eligible', 'filing_date', '_order'])
        .drop_duplicates('_appeal', keep = 'last'))
    appellate_columns = [
        'appeal_date', 'district_of_origin', *(names[key] for key in keys)]
    return (
        matched.set_index('_appeal')
        .drop(columns = ['_eligible', '_order', *appellate_columns])
        .rename_axis(index = None))


def _join(
    candidates: pd.DataFrame,
    records: pd.DataFrame,
    keys: list[str],
    names: dict[str, str]) -> pd.DataFrame:
    """Joins appeals with every district record that has their keys.

    Args:
        candidates: The appeals to match.
        records: The district records.
        keys: The columns of `records` to match, besides the district.
        names: The appellate column matched with each column in `keys`.

    Returns:
        pd.DataFrame: One row for each appeal and matching record, with the
            appeal's index in '_appeal'.

    """
    # Keys are compared as text, so a defendant number matches whether it is
    # stored as text or as a number.
    pairs = [
        ('district_of_origin', 'district'),
        *((names[key], key) for key in keys)]
    joins = [f'_key_{district}' for _, district in pairs]
    left = candidates.reset_index(names = '_appeal')
    right = records.copy(deep = False)
    for join, (appellate, district) in zip(joins, pairs, strict = True):
        left[join] = left[appellate].astype('string')
        right[join] = right[district].astype('string')
    return left.merge(right, on = joins).drop(columns = joins)
