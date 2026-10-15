"""Imports, parses, and exports data from the FJC Integrated Database.

The FJC distributes the Integrated Database (IDB) as yearly SAS files. The
functions in this module turn those files into one clean table per case type:

- `import_data` reads the yearly files for a range of years and drops the
  outdated pending cases repeated in earlier files.
- `parse_data` converts missing-value codes to missing data, replaces codes
  with readable labels, converts each column to its data type, adds derived
  columns, and renames the columns.
- `export_data` writes a parsed table to a CSV file.
- `run` does all three for a range of years, one yearly file at a time.

The case types are 'appellate' (courts of appeals), 'civil' (district court
civil cases), and 'criminal' (district court criminal defendants).

"""

from __future__ import annotations

import datetime as dt
import pathlib
from typing import Any

import camina
import pandas as pd

from . import base, options, rules

# Docket numbers have a two-digit year and a serial number of four or more
# digits, with a 0 inserted before four-digit serial numbers.
_DOCKET_MINIMUM_LENGTH = 6
_SERIAL_DIGITS = 4

def run(
    case_type: str,
    start_year: int,
    stop_year: int | None = None,
    data_folder: str | pathlib.Path = options._DATA_FOLDER,
    *,
    rename_columns: bool = options._RENAME_COLUMNS,
    fix_city_spellings: bool = options._FIX_CITY_SPELLINGS) -> None:
    """Imports, parses, and exports FJC IDB data for a range of years.

    The CSV file is named 'fjc_idb_{case_type}_data_{start_year}_{stop_year}'
    and saved next to the yearly files for `case_type`. Each yearly file is
    parsed and appended to the CSV file in turn, so only one year of data is
    held in memory at a time.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').
        start_year: The first statistical year to include.
        stop_year: The last statistical year to include. Defaults to None, in
            which case the current year is used.
        data_folder: The path to the folder containing the FJC IDB dataset.
            Defaults to options._DATA_FOLDER.
        rename_columns: Whether to rename columns based on the column mapping
            for `case_type`. Defaults to options._RENAME_COLUMNS.
        fix_city_spellings: Whether to correct misspelled city names from the
            FJC codebook. Defaults to options._FIX_CITY_SPELLINGS.

    Raises:
        ValueError: If `case_type` is not a recognized source type.

    Examples:
        >>> import fjc_idb
        >>> fjc_idb.run('appellate', 2008, 2026)  # doctest: +SKIP

    """
    if case_type not in options._SOURCE_PREFIXES:
        message = (
            f'Invalid source type: {case_type}. '
            f'Must be one of {list(options._SOURCE_PREFIXES)}.')
        raise ValueError(message)
    stop_year = stop_year or dt.datetime.now(tz = dt.UTC).year
    data_folder = _get_data_path(case_type, data_folder)
    files = _get_files(case_type, start_year, stop_year, data_folder)
    missing_replacements = {
        spec.name if rename_columns else spec.import_name:
            spec.missing_replacement
        for spec in _get_columns(case_type).values()}
    file_name = f'fjc_idb_{case_type}_data_{start_year}_{stop_year}.csv'
    for index, file in enumerate(files):
        data = _import_file(file, keep_pending = index == len(files) - 1)
        data = parse_data(
            data, case_type, rename_columns = rename_columns,
            fix_city_spellings = fix_city_spellings)
        export_data(
            data, data_folder, file_name, missing_replacements,
            append = index > 0)

def export_data(
    data: pd.DataFrame,
    data_folder: pathlib.Path,
    file_name: str,
    missing_replacements: dict[str, Any] | None = None,
    *,
    append: bool = False) -> None:
    """Exports the FJC IDB dataset to a CSV file.

    Dates are written as YYYY-MM-DD. Missing data is written as the value in
    `missing_replacements` for its column, or left blank.

    Args:
        data: The FJC IDB dataset to export.
        data_folder: The path to the folder where the CSV file will be saved.
        file_name: The name of the CSV file.
        missing_replacements: Values to write in place of missing data, keyed
            by column name. Defaults to None, which leaves missing data blank.
        append: Whether to add the rows to the end of an existing CSV file
            instead of replacing it. Defaults to False.

    """
    data = data.copy(deep=False)
    for name, value in (missing_replacements or {}).items():
        if name in data and data[name].isna().any():
            column = data[name]
            if column.dtype.kind == 'M':
                column = column.dt.strftime(options._DATE_FORMAT)
            data[name] = column.astype(object).where(column.notna(), value)
    output_path = data_folder / file_name
    data.to_csv(
        output_path, index = False, date_format = options._DATE_FORMAT,
        mode = 'a' if append else 'w', header = not append)

def import_data(
    case_type: str,
    start_year: int,
    stop_year: int | None = None,
    data_folder: pathlib.Path = options._DATA_FOLDER) -> pd.DataFrame:
    """Imports the FJC IDB dataset from the specified folder.

    Each yearly file holds the cases (or, for criminal data, the defendants)
    terminated in that statistical year, and many files also hold a snapshot of
    those still pending when the file was made. Because pending records are
    repeated in every later file until they end, only the pending records in
    the latest file are kept.

    The whole range is held in memory. For a long range of civil or criminal
    data, `run` processes one year at a time instead.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').
        start_year: The first statistical year to include.
        stop_year: The last statistical year to include.
            Defaults to None, in which case the current year is used.
        data_folder: The path to the folder containing the yearly
            files for `case_type`.

    Returns:
        pd.DataFrame: The imported rows from all matching yearly files.

    """
    files = _get_files(case_type, start_year, stop_year, data_folder)
    dataframes = [
        _import_file(file, keep_pending = index == len(files) - 1)
        for index, file in enumerate(files)]
    return pd.concat(dataframes, ignore_index=True)

def parse_data(
    data: pd.DataFrame,
    case_type: str,
    rename_columns: bool = options._RENAME_COLUMNS,
    fix_city_spellings: bool = options._FIX_CITY_SPELLINGS) -> pd.DataFrame:
    """Parses the FJC IDB dataset.

    Missing-value codes are converted to missing data, coded columns with a
    decoder are replaced by their labels, every column is converted to its
    data type, and the days between key dates are added. Each case type also
    gets derived columns, such as indicators for groups of offenses or natures
    of suit; the codebooks in the User Guide list them.

    Args:
        data: The imported FJC IDB dataset.
        case_type: The source type ('appellate', 'civil', or 'criminal').
        rename_columns: Whether to rename columns based on the column mapping
            for `case_type`.
        fix_city_spellings: Whether to correct misspelled city names from the
            FJC codebook.

    Returns:
        pd.DataFrame: The parsed FJC IDB dataset.

    """
    specs = _get_columns(case_type)
    data = data.copy(deep=False)
    preparers = {
        'appellate': _prepare_appellate,
        'civil': _prepare_civil,
        'criminal': _prepare_criminal}
    data = preparers[case_type](data)
    if 'JURIS' in data:
        data = _parse_jurisdiction(data)
    for spec in specs.values():
        if spec.import_name in data:
            data[spec.import_name] = _parse_column(data[spec.import_name], spec)
    if fix_city_spellings:
        corrections = {
            rules.offices[code]: name
            for code, name in rules.office_spelling_fixes.items()}
        for spec in specs.values():
            if spec.decoder is rules.offices and spec.import_name in data:
                data[spec.import_name] = data[spec.import_name].replace(
                    corrections)
    data = _add_date_gaps(data)
    if rename_columns:
        data = _column_rename(data, case_type)
    return data

def parse_docket_number(docket_number: str) -> str:
    """Converts an IDB court of appeals docket number to its standard form.

    The IDB stores appellate docket numbers as a two-digit year followed by a
    serial number, with a 0 inserted before four-digit serial numbers (for
    example, '1701234' for 17-1234). The inserted 0 is removed.

    Args:
        docket_number: The docket number as it appears in the IDB.

    Returns:
        str: The docket number in the form 'No. YY-NNNN'.

    Raises:
        ValueError: If `docket_number` has fewer than six characters.

    Examples:
        >>> parse_docket_number('1701234')
        'No. 17-1234'
        >>> parse_docket_number('1910001')
        'No. 19-10001'

    """
    if len(docket_number) < _DOCKET_MINIMUM_LENGTH:
        raise ValueError(f'Invalid docket number: {docket_number}')
    year = docket_number[:2]
    docket_num = docket_number[2:]
    if len(docket_num) > _SERIAL_DIGITS and docket_num[0] == '0':
        docket_num = docket_num[1:]
    return f'No. {year}-{docket_num}'

""" Private Functions """

def _column_rename(data: pd.DataFrame, case_type: str) -> pd.DataFrame:
    """Renames columns in the FJC IDB dataset based on the column mapping.

    Args:
        data: The imported FJC IDB dataset.
        case_type: The source type ('appellate', 'civil', or 'criminal').

    Returns:
        pd.DataFrame: The FJC IDB dataset with renamed columns.

    """
    renamer = _get_columns(case_type)
    return data.rename(
        columns = {spec.import_name: spec.name for spec in renamer.values()})

def _add_appeal_type_columns(
    data: pd.DataFrame,
    source: str = 'APPTYPE',
    suffix: str = '') -> pd.DataFrame:
    """Adds a column for each appeal type with 1 for yes and 0 for no.

    The new columns are named by `rules.appeal_types_to_columns` plus `suffix`
    and placed after `source`. Appeal types listed in
    `rules.appeal_types_in_other_columns` are marked in the columns of each of
    the listed appeal types.

    Args:
        data: The imported appellate dataset.
        source: The column with the appeal type codes. Defaults to 'APPTYPE'.
        suffix: The text added to the end of each new column name. Defaults to
            ''.

    Returns:
        pd.DataFrame: The appellate dataset with the appeal type columns.

    """
    if source not in data:
        return data
    appeal_types = _to_codes(data[source])
    position = _position_after(data, source)
    others = rules.appeal_types_in_other_columns
    for code, name in rules.appeal_types_to_columns.items():
        included = [code] + [
            other for other, codes in others.items() if code in codes]
        indicator = appeal_types.isin(included).astype('Int64')
        data.insert(position, f'{name}{suffix}', indicator)
        position += 1
    return data

def _add_code_columns(
    data: pd.DataFrame,
    sources: str | list[str],
    columns: dict[str, list[str]],
    suffix: str = '') -> pd.DataFrame:
    """Adds a column for each list of codes with 1 for yes and 0 for no.

    A new column is 1 if any of `sources` has a code in its list. The new
    columns are placed after the last of `sources` and are missing where every
    one of `sources` has a missing-value code.

    Args:
        data: The imported dataset.
        sources: The column or columns with the codes.
        columns: The codes marked in each new column, keyed by column name.
        suffix: The text added to the end of each new column name. Defaults to
            ''.

    Returns:
        pd.DataFrame: The dataset with the new columns.

    """
    sources = [sources] if isinstance(sources, str) else sources
    if not all(source in data for source in sources):
        return data
    codes = pd.concat([_to_codes(data[source]) for source in sources], axis = 1)
    missing = (codes.isna() | codes.isin(options._MISSING_CODES)).all(axis = 1)
    position = _position_after(data, sources[-1])
    for name, included in columns.items():
        indicator = codes.isin(included).any(axis = 1).astype('Int64')
        data.insert(position, f'{name}{suffix}', indicator.mask(missing))
        position += 1
    return data


def _add_date_gaps(data: pd.DataFrame) -> pd.DataFrame:
    """Adds columns with the number of days between pairs of dates.

    The new columns are named by `rules.date_gaps` and placed after the last
    date column. A gap is missing if either of its dates is missing.

    Args:
        data: The FJC IDB dataset with parsed dates.

    Returns:
        pd.DataFrame: The FJC IDB dataset with the date gap columns.

    """
    gaps = {
        name: dates for name, dates in rules.date_gaps.items()
        if all(date in data for date in dates)}
    if not gaps:
        return data
    dates = {date for pair in gaps.values() for date in pair}
    position = max(_position_after(data, date) for date in dates)
    for name, (start, end) in gaps.items():
        days = (data[end] - data[start]).dt.days.astype('Int64')
        data.insert(position, name, days)
        position += 1
    return data

def _add_separate_opinions(data: pd.DataFrame) -> pd.DataFrame:
    """Adds columns counting the concurrences and dissents on the panel.

    The new 'concurrences' and 'dissents' columns are placed after JDG3INV.
    They count the judges whose JDG1INV, JDG2INV, or JDG3INV code is in
    `rules.concurrence_codes` or `rules.dissent_codes`. Both are missing if
    all three codes are missing.

    Args:
        data: The imported appellate dataset.

    Returns:
        pd.DataFrame: The appellate dataset with the new columns.

    """
    sources = ['JDG1INV', 'JDG2INV', 'JDG3INV']
    if not all(source in data for source in sources):
        return data
    codes = pd.concat([_to_codes(data[source]) for source in sources], axis = 1)
    missing = (codes.isna() | codes.isin(options._MISSING_CODES)).all(axis = 1)
    position = _position_after(data, 'JDG3INV')
    for name, included in (
            ('concurrences', rules.concurrence_codes),
            ('dissents', rules.dissent_codes)):
        count = codes.isin(included).sum(axis = 1).astype('Int64').mask(missing)
        data.insert(position, name, count)
        position += 1
    return data


def _add_published(data: pd.DataFrame) -> pd.DataFrame:
    """Adds a column showing whether the opinion or order was published.

    The new 'published' column is placed after PUBSTAT. It is 1 for codes in
    `rules.published_codes`, 0 for codes in `rules.unpublished_codes`, and
    missing otherwise.

    Args:
        data: The imported appellate dataset.

    Returns:
        pd.DataFrame: The appellate dataset with the 'published' column.

    """
    if 'PUBSTAT' not in data:
        return data
    codes = _to_codes(data['PUBSTAT'])
    published = pd.Series(pd.NA, index = data.index, dtype = 'Int64')
    published = published.mask(
        codes.isin([str(code) for code in rules.unpublished_codes]), 0)
    published = published.mask(
        codes.isin([str(code) for code in rules.published_codes]), 1)
    data.insert(_position_after(data, 'PUBSTAT'), 'published', published)
    return data


def _add_pro_se_party(
    data: pd.DataFrame,
    sources: tuple[str, ...] = ('PROSEFLE', 'PROSETRM')) -> pd.DataFrame:
    """Adds a column showing whether any party was pro se.

    The new 'pro_se_party' column is placed after the last of `sources`. It is
    1 if any of `sources` shows a pro se party, 0 if none of them does, and
    missing if all of them are missing.

    Args:
        data: The imported dataset.
        sources: The columns with pro se codes. Defaults to the appellate
            columns for pro se parties at filing and at termination.

    Returns:
        pd.DataFrame: The dataset with the 'pro_se_party' column.

    """
    if not all(source in data for source in sources):
        return data
    codes = pd.concat([_to_codes(data[source]) for source in sources], axis = 1)
    known = ['0', *rules.pro_se_codes]
    pro_se_party = pd.Series(pd.NA, index = data.index, dtype = 'Int64')
    pro_se_party = pro_se_party.mask(codes.isin(known).any(axis = 1), 0)
    pro_se_party = pro_se_party.mask(
        codes.isin(rules.pro_se_codes).any(axis = 1), 1)
    data.insert(
        _position_after(data, sources[-1]), 'pro_se_party', pro_se_party)
    return data

def _combine_court_codes(
    data: pd.DataFrame,
    circuit: str,
    district: str,
    offices: list[str]) -> pd.DataFrame:
    """Prefixes district and office codes as they are listed in the codebooks.

    The district code is prefixed with its two-digit circuit, and each office
    code is prefixed with that combined district code.

    Args:
        data: The imported dataset.
        circuit: The column with the circuit code.
        district: The column with the district code.
        offices: The columns with office codes in `district`.

    Returns:
        pd.DataFrame: The dataset with the combined codes.

    """
    districts = _to_codes(data[district])
    circuits = _to_codes(data[circuit]).str.zfill(2)
    data[district] = districts.where(
        districts.isin(options._MISSING_CODES), circuits + districts)
    for office in offices:
        # An office cannot be identified without its district.
        codes = _to_codes(data[office]).mask(
            districts.isin(options._MISSING_CODES), '-8')
        data[office] = codes.where(
            codes.isin(options._MISSING_CODES), data[district] + codes)
    return data


def _drop_pending(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Drops the pending cases from a yearly file.

    Args:
        dataframe: A yearly file.

    Returns:
        pd.DataFrame: The yearly file without pending cases.

    """
    column = options._PENDING_COLUMN
    if column not in dataframe:
        return dataframe
    return dataframe[dataframe[column] != options._PENDING_YEAR]


def _drop_stale_pending(dataframes: list[pd.DataFrame]) -> list[pd.DataFrame]:
    """Drops pending cases from every yearly file except the latest one.

    Args:
        dataframes: Yearly files in chronological order.

    Returns:
        list[pd.DataFrame]: The yearly files without outdated pending cases.

    """
    earlier = [_drop_pending(dataframe) for dataframe in dataframes[:-1]]
    return [*earlier, dataframes[-1]]

def _get_data_path(
    case_type: str,
    data_folder: pathlib.Path | str) -> pathlib.Path:
    """Returns the path to the data file for the specified source type.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').
        data_folder: The path to the folder containing the FJC IDB dataset.

    Returns:
        pathlib.Path: The path to the data file for the specified source type.

    """
    folder: pathlib.Path = camina.pathlibify(data_folder)
    if case_type in ['civil', 'criminal']:
        return folder / 'district' / case_type
    return folder / case_type

def _get_files(
    case_type: str,
    start_year: int,
    stop_year: int | None,
    data_folder: pathlib.Path) -> list[pathlib.Path]:
    """Returns the yearly files for a range of years in chronological order.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').
        start_year: The first statistical year to include.
        stop_year: The last statistical year to include, or None for the
            current year.
        data_folder: The path to the folder containing the yearly files for
            `case_type`.

    Returns:
        list[pathlib.Path]: The matching yearly files.

    Raises:
        FileNotFoundError: If no yearly files are found in `data_folder`.

    """
    prefix = options._SOURCE_PREFIXES[case_type]
    stop_year = stop_year or dt.datetime.now(tz = dt.UTC).year
    files = []
    for year in range(start_year, stop_year + 1):
        year_suffix = f'{year % 100:02d}'
        files.extend(
            sorted(data_folder.glob(f'{prefix}{year_suffix}*.sas7bdat')))
    if not files:
        message = (
            f'No {case_type} files for {start_year}-{stop_year} '
            f'found in {data_folder}.')
        raise FileNotFoundError(message)
    return files


def _import_file(file: pathlib.Path, keep_pending: bool) -> pd.DataFrame:
    """Imports one yearly file.

    Args:
        file: The path to the yearly file.
        keep_pending: Whether to keep the pending cases, which should only be
            kept from the latest file.

    Returns:
        pd.DataFrame: The imported rows.

    """
    data = pd.read_sas(file, encoding = options._ENCODING)
    return data if keep_pending else _drop_pending(data)


def _get_columns(case_type: str) -> dict[str, base.Column]:
    """Returns the column mapping for the specified source type.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').

    Returns:
        dict[str, base.Column]: The columns of the specified source type.

    Raises:
        NotImplementedError: If there is no column mapping for `case_type`.

    """
    try:
        columns: dict[str, base.Column] = getattr(base, f'{case_type}_columns')
    except AttributeError as error:
        message = f'No column mapping exists for {case_type} cases.'
        raise NotImplementedError(message) from error
    return columns

def _parse_column(column: pd.Series, spec: base.Column) -> pd.Series:
    """Cleans, decodes, and converts a column based on its specification.

    Args:
        column: The imported column.
        spec: The specification describing the column.

    Returns:
        pd.Series: The parsed column.

    """
    missing_values = spec.missing_value
    if missing_values is None:
        missing_values = []
    elif not isinstance(missing_values, (list, tuple)):
        missing_values = [missing_values]
    if spec.data_type == 'date':
        column = pd.to_datetime(column)
        missing_dates = [pd.Timestamp(value) for value in missing_values]
        return column.mask(column.isin(missing_dates))
    codes = _to_codes(column)
    codes = codes.mask(codes.isin([str(value) for value in missing_values]))
    if spec.decoder:
        codes = codes.map(spec.decoder).fillna(codes).astype('string')
    if spec.data_type in (int, 'int'):
        return pd.to_numeric(codes).astype('Int64')
    return codes

def _parse_jurisdiction(data: pd.DataFrame) -> pd.DataFrame:
    """Translate FJC jurisdiction codes into readable labels.

    For prisoner petitions (identified by their nature of suit), the
    jurisdiction code has a prison-specific meaning. Otherwise, the code follows
    the standard civil jurisdiction taxonomy. This runs before the raw codes
    are parsed so that the missing (-8) and non-civil (-9) codes can be labeled.

    Args:
        data: The imported dataset with JURIS and NOS columns.

    Returns:
        pd.DataFrame: The dataset with JURIS replaced by readable labels.

    """
    jurisdiction = _to_codes(data['JURIS'])
    nature_of_suit = _to_codes(data['NOS'])
    is_prisoner_case = nature_of_suit.isin(rules.prisoner_codes)
    for code, label in rules.prisoner_jurisdiction.items():
        jurisdiction = jurisdiction.mask(
            is_prisoner_case & (jurisdiction == code),
            label,
        )
    for code, label in rules.civil_jurisdiction.items():
        jurisdiction = jurisdiction.mask(
            ~is_prisoner_case & (jurisdiction == code),
            label,
        )
    jurisdiction = jurisdiction.mask(jurisdiction == '-8', 'N/A')
    jurisdiction = jurisdiction.mask(jurisdiction == '-9', 'Non-Civil Case')
    data['JURIS'] = jurisdiction
    return data

def _position_after(data: pd.DataFrame, column: str) -> int:
    """Returns the position just after a column.

    Args:
        data: The dataset.
        column: The name of the column.

    Returns:
        int: The position just after `column`.

    Raises:
        TypeError: If `column` appears more than once in `data`.

    """
    location = data.columns.get_loc(column)
    if not isinstance(location, int):
        message = f'The column {column} appears more than once.'
        raise TypeError(message)
    return location + 1


def _prepare_appellate(data: pd.DataFrame) -> pd.DataFrame:
    """Makes the changes that are specific to appellate data.

    Indicator columns for each appeal type at filing and at termination, for
    groups of criminal offenses and natures of suit, for whether any party was
    pro se, for whether the decision was published, and for the number of
    concurrences and dissents are added, a standard
    hyphenated docket number is added, the district of origin is prefixed
    with its circuit, which is how district codes are listed in the FJC
    codebook, and the district office is prefixed with that district code,
    which is how office codes are listed in the codebook.

    Args:
        data: The imported appellate dataset.

    Returns:
        pd.DataFrame: The appellate dataset ready for parsing.

    """
    data = _add_appeal_type_columns(data)
    data = _add_appeal_type_columns(data, 'TRMTYPE', '_at_termination')
    data = _add_pro_se_party(data)
    data = _add_published(data)
    data = _add_separate_opinions(data)
    data = _add_code_columns(data, 'OFFENSE', rules.criminal_offense_columns)
    data = _add_code_columns(data, 'NOS', rules.civil_nature_of_suit_columns)
    dockets = data['DOCKET'].map(parse_docket_number)
    data.insert(_position_after(data, 'DOCKET'), 'docket_number', dockets)
    return _combine_court_codes(data, 'DCIRC', 'DDIST', ['DOFFICE'])


def _prepare_civil(data: pd.DataFrame) -> pd.DataFrame:
    """Makes the changes that are specific to civil district data.

    Indicator columns for groups of natures of suit and a column for whether
    any party was pro se are added, and the district and office codes are
    combined as they are listed in the FJC codebook.

    Args:
        data: The imported civil dataset.

    Returns:
        pd.DataFrame: The civil dataset ready for parsing.

    """
    data = _add_pro_se_party(data, ('PROSE',))
    data = _add_code_columns(data, 'NOS', rules.civil_nature_of_suit_columns)
    return _combine_court_codes(data, 'CIRCUIT', 'DISTRICT', ['OFFICE'])


def _prepare_criminal(data: pd.DataFrame) -> pd.DataFrame:
    """Makes the changes that are specific to criminal district data.

    Indicator columns for groups of offenses are added from the five D2
    offense codes at filing and at termination, the circuit code is converted
    to the numeric form used by the other files, and the district and office
    codes are combined as they are listed in the FJC codebook.

    Args:
        data: The imported criminal dataset.

    Returns:
        pd.DataFrame: The criminal dataset ready for parsing.

    """
    filing = [f'D2FOFFCD{number}' for number in range(1, 6)]
    termination = [f'D2TOFFCD{number}' for number in range(1, 6)]
    data = _add_code_columns(data, filing, rules.criminal_offense_columns)
    data = _add_code_columns(
        data, termination, rules.criminal_offense_columns, '_at_termination')
    data['CIRCUIT'] = pd.to_numeric(data['CIRCUIT'], errors = 'coerce')
    return _combine_court_codes(
        data, 'CIRCUIT', 'DISTRICT', ['OFFICE', 'TERMOFF'])

def _to_codes(column: pd.Series) -> pd.Series:
    """Converts a column to the text codes used in the FJC codebooks.

    Args:
        column: The imported column.

    Returns:
        pd.Series: The column as strings, with whole numbers for numeric codes.

    """
    if pd.api.types.is_numeric_dtype(column):
        return column.astype('Int64').astype('string')
    codes = column.astype('string').str.strip()
    return codes.mask(codes == '')
