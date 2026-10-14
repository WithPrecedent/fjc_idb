"""Imports, parses, and exports data from the FJC Integrated Database."""

from __future__ import annotations

import datetime
import pathlib
from typing import Any

import camina
import pandas as pd

from . import base, options


def run(
    case_type: str,
    start_year: int,
    stop_year: int | None = None,
    data_folder: str | pathlib.Path = options._DATA_FOLDER,
    rename_columns: bool = options._RENAME_COLUMNS,
) -> None:
    """Imports, parses, and exports FJC IDB data for a range of years.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').
        start_year: The first statistical year to include.
        stop_year: The last statistical year to include. Defaults to None, in 
            which case the current year is used.
        data_folder: The path to the folder containing the FJC IDB dataset. 
            Defaults to options._DATA_FOLDER.
        rename_columns: Whether to rename columns based on the column mapping 
            for `case_type`. Defaults to options._RENAME_COLUMNS.

    Raises:
        ValueError: If `case_type` is not a recognized source type.

    """
    if case_type not in options._SOURCE_PREFIXES:
        message = f'Invalid source type: {case_type}. Must be one of {list(options._SOURCE_PREFIXES)}.'
        raise ValueError(message)
    stop_year = stop_year or datetime.datetime.now().year
    data_folder = _get_data_path(case_type, data_folder)
    data = import_data(case_type, start_year, stop_year, data_folder)
    data = parse_data(data, case_type, rename_columns)
    missing_values = {
        feature.name
        if rename_columns
        else feature.import_name: feature.missing_value
        for feature in _get_features(case_type).values()}
    file_name = f'fjc_idb_{case_type}_data_{start_year}_{stop_year}.csv'
    export_data(data, data_folder, file_name, missing_values)


def export_data(
    data: pd.DataFrame,
    data_folder: pathlib.Path,
    file_name: str,
    missing_values: dict[str, Any] | None = None,
) -> None:
    """Exports the FJC IDB dataset to a CSV file.

    Args:
        data: The FJC IDB dataset to export.
        data_folder: The path to the folder where the CSV file will be saved.
        file_name: The name of the CSV file.
        missing_values: Values to write in place of missing data, keyed by
            column name. Defaults to None, which leaves missing data blank.

    """
    data = data.copy(deep=False)
    for name, value in (missing_values or {}).items():
        if name in data and data[name].isna().any():
            column = data[name]
            if column.dtype.kind == "M":
                column = column.dt.strftime(options._DATE_FORMAT)
            data[name] = column.astype(object).where(column.notna(), value)
    output_path = data_folder / file_name
    data.to_csv(output_path, index=False, date_format=options._DATE_FORMAT)


def import_data(
    case_type: str,
    start_year: int,
    stop_year: int | None = None,
    data_folder: pathlib.Path = options._DATA_FOLDER,
) -> pd.DataFrame:
    """Imports the FJC IDB dataset from the specified folder.

    Each yearly file holds the cases terminated in that statistical year. Recent
    files also hold a snapshot of the cases still pending when the file was
    made, so only the pending cases in the latest file are kept.

    Args:
        case_type (str): The source type ('appellate', 'civil', or 'criminal').
        start_year (int): The first statistical year to include.
        stop_year (int | None, optional): The last statistical year to include.
            Defaults to None, in which case the current year is used.
        data_folder (pathlib.Path): The path to the folder containing the yearly
            files for `case_type`.

    Returns:
        pd.DataFrame: The imported rows from all matching yearly files.

    Raises:
        FileNotFoundError: If no yearly files are found in `data_folder`.

    """
    prefix = options._SOURCE_PREFIXES[case_type]
    stop_year = stop_year or datetime.datetime.now().year
    dataframes = []
    for year in range(start_year, stop_year + 1):
        year_suffix = f'{year % 100:02d}'
        files = sorted(data_folder.glob(f'{prefix}{year_suffix}*.sas7bdat'))
        dataframes.extend(
            pd.read_sas(file, encoding=options._ENCODING) for file in files
        )
    if not dataframes:
        message = f'No {case_type} files for {start_year}-{stop_year} found in {data_folder}.'
        raise FileNotFoundError(message)
    dataframes = _drop_stale_pending(dataframes)
    return pd.concat(dataframes, ignore_index=True)


def parse_data(
    data: pd.DataFrame,
    case_type: str,
    rename_columns: bool = options._RENAME_COLUMNS,
) -> pd.DataFrame:
    """Parses the FJC IDB dataset.

    Missing-value codes are converted to missing data, coded columns with a
    decoder are replaced by their labels, and every column is converted to the
    data type of its feature.

    Args:
        data (pd.DataFrame): The imported FJC IDB dataset.
        case_type (str): The source type ('appellate', 'civil', or 'criminal').
        rename_columns (bool): Whether to rename columns based on the column
            mapping for `case_type`.

    Returns:
        pd.DataFrame: The parsed FJC IDB dataset.

    """
    features = _get_features(case_type)
    data = data.copy(deep=False)
    if case_type == "appellate":
        data = _prepare_appellate(data)
    for feature in features.values():
        if feature.import_name in data:
            data[feature.import_name] = _parse_feature(
                data[feature.import_name], feature
            )
    if rename_columns:
        data = _column_rename(data, case_type)
    return data


""" Private Functions """


def _column_rename(data: pd.DataFrame, case_type: str) -> pd.DataFrame:
    """Renames columns in the FJC IDB dataset based on the column mapping.

    Args:
        data (pd.DataFrame): The imported FJC IDB dataset.
        case_type (str): The source type ('appellate', 'civil', or 'criminal').

    Returns:
        pd.DataFrame: The FJC IDB dataset with renamed columns.

    """
    renamer = _get_features(case_type)
    return data.rename(
        columns={
            feature.import_name: feature.name for feature in renamer.values()
        }
    )


def _drop_stale_pending(dataframes: list[pd.DataFrame]) -> list[pd.DataFrame]:
    """Drops pending cases from every yearly file except the latest one.

    Args:
        dataframes (list[pd.DataFrame]): Yearly files in chronological order.

    Returns:
        list[pd.DataFrame]: The yearly files without outdated pending cases.

    """
    column = options._PENDING_COLUMN
    earlier = [
        dataframe[dataframe[column] != options._PENDING_YEAR]
        if column in dataframe
        else dataframe
        for dataframe in dataframes[:-1]
    ]
    return [*earlier, dataframes[-1]]


def _get_data_path(
    case_type: str, data_folder: pathlib.Path | str
) -> pathlib.Path:
    """Returns the path to the data file for the specified source type.

    Args:
        case_type (str): The source type ('appellate', 'civil', or 'criminal').
        data_folder (str | pathlib.Path): The path to the folder containing the FJC IDB dataset.

    Returns:
        pathlib.Path: The path to the data file for the specified source type.

    """
    data_folder = camina.pathlibify(data_folder)
    if case_type in ['civil', 'criminal']:
        data_folder = data_folder / "district" / case_type
    else:
        data_folder = data_folder / case_type
    return data_folder


def _get_features(case_type: str) -> dict[str, base.Feature]:
    """Returns the column mapping for the specified source type.

    Args:
        case_type (str): The source type ('appellate', 'civil', or 'criminal').

    Returns:
        dict[str, base.Feature]: The features of the specified source type.

    Raises:
        NotImplementedError: If there is no column mapping for `case_type`.

    """
    try:
        return getattr(base, f'{case_type}_columns')
    except AttributeError as error:
        message = f'No column mapping exists for {case_type} cases.'
        raise NotImplementedError(message) from error


def _parse_feature(column: pd.Series, feature: base.Feature) -> pd.Series:
    """Cleans, decodes, and converts a column based on its feature.

    Args:
        column (pd.Series): The imported column.
        feature (base.Feature): The feature describing the column.

    Returns:
        pd.Series: The parsed column.

    """
    if feature.data_type == 'date':
        column = pd.to_datetime(column)
        return column.mask(column == pd.Timestamp(options._MISSING_DATE))
    codes = _to_codes(column)
    codes = codes.mask(codes.isin(options._MISSING_CODES))
    if feature.decoder:
        codes = codes.map(feature.decoder).fillna(codes).astype('string')
    if feature.data_type in (int, 'int'):
        return pd.to_numeric(codes).astype('Int64')
    return codes


def _prepare_appellate(data: pd.DataFrame) -> pd.DataFrame:
    """Makes the changes that are specific to appellate data.

    A standard hyphenated docket number is added and the district of origin is
    prefixed with its circuit, which is how district codes are listed in the
    FJC codebook.

    Args:
        data (pd.DataFrame): The imported appellate dataset.

    Returns:
        pd.DataFrame: The appellate dataset ready for parsing.

    """
    dockets = data["DOCKET"].map(base.parse_docket_number)
    data.insert(data.columns.get_loc('DOCKET') + 1, 'docket_number', dockets)
    districts = _to_codes(data["DDIST"])
    circuits = _to_codes(data["DCIRC"]).str.zfill(2)
    data["DDIST"] = districts.where(
        districts.isin(options._MISSING_CODES), circuits + districts
    )
    return data


def _to_codes(column: pd.Series) -> pd.Series:
    """Converts a column to the text codes used in the FJC codebooks.

    Args:
        column (pd.Series): The imported column.

    Returns:
        pd.Series: The column as strings, with whole numbers for numeric codes.

    """
    if pd.api.types.is_numeric_dtype(column):
        return column.astype('Int64').astype('string')
    codes = column.astype('string').str.strip()
    return codes.mask(codes == '')
