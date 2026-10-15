"""Command line interface for downloading and exporting FJC IDB data.

Examples:
    python -m fjc_idb appellate --start-year 2008 --stop-year 2026
    fjc-idb civil criminal --start-year 2020 --rename-columns false
    fjc-idb all --start-year 2008 --download

"""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Sequence

from . import main as idb
from . import options
from .downloader import download as download_files


def main(arguments: Sequence[str] | None = None) -> None:
    """Downloads and exports FJC IDB data for the case types and years given
    on the command line.

    Args:
        arguments: The command line arguments. Defaults to None, in which case
            the arguments passed to the program are used.

    """
    parsed = _get_parser().parse_args(arguments)
    logging.basicConfig(level = logging.INFO, format = '%(message)s')
    case_types = (
        list(options._SOURCE_PREFIXES) if 'all' in parsed.case_types
        else list(dict.fromkeys(parsed.case_types)))
    for case_type in case_types:
        if parsed.download or parsed.download_only:
            started = time.time()
            files = download_files(
                case_type,
                parsed.start_year,
                parsed.stop_year,
                data_folder = parsed.data_folder,
                overwrite = parsed.overwrite)
            print(
                f'Downloaded {len(files)} {case_type} files in '
                f'{time.time() - started:.0f}s.')
        if parsed.download_only:
            continue
        started = time.time()
        idb.run(
            case_type,
            parsed.start_year,
            parsed.stop_year,
            data_folder = parsed.data_folder,
            rename_columns = parsed.rename_columns,
            fix_city_spellings = parsed.fix_city_spellings)
        print(f'Exported {case_type} data in {time.time() - started:.0f}s.')


def _get_parser() -> argparse.ArgumentParser:
    """Returns the parser for the command line arguments.

    Returns:
        argparse.ArgumentParser: The command line parser.

    """
    parser = argparse.ArgumentParser(
        prog = 'fjc-idb',
        description = (
            'Download FJC Integrated Database files and export them to CSV '
            'files in the data folder for each case type.'))
    parser.add_argument(
        'case_types',
        nargs = '+',
        choices = [*options._SOURCE_PREFIXES, 'all'],
        help = 'the case types to export, or "all" for every case type')
    parser.add_argument(
        '--start-year',
        type = int,
        required = True,
        help = 'the first statistical year to include')
    parser.add_argument(
        '--stop-year',
        type = int,
        default = None,
        help = 'the last statistical year to include (default: current year)')
    parser.add_argument(
        '--data-folder',
        default = options._DATA_FOLDER,
        help = 'the folder containing the FJC IDB data (default: %(default)s)')
    parser.add_argument(
        '--rename-columns',
        type = _to_bool,
        nargs = '?',
        const = True,
        default = options._RENAME_COLUMNS,
        metavar = 'true|false',
        help = (
            'rename columns to descriptive names, or keep the IDB field names '
            'with "false" (default: %(default)s)'))
    parser.add_argument(
        '--fix-city-spellings',
        type = _to_bool,
        nargs = '?',
        const = True,
        default = options._FIX_CITY_SPELLINGS,
        metavar = 'true|false',
        help = (
            'correct misspelled city names from the FJC codebook, or keep '
            'them with "false" (default: %(default)s)'))
    parser.add_argument(
        '--download',
        action = 'store_true',
        help = 'download missing files from the FJC website before exporting')
    parser.add_argument(
        '--download-only',
        action = 'store_true',
        help = 'download missing files from the FJC website without exporting')
    parser.add_argument(
        '--overwrite',
        action = 'store_true',
        help = (
            'replace files that were already downloaded, such as the file for '
            'the current year, which the FJC updates during the year'))
    return parser


def _to_bool(value: str) -> bool:
    """Converts a command line value to True or False.

    Args:
        value: The value given on the command line.

    Returns:
        bool: True for 'true', 'yes', 'on', or '1', and False for 'false',
            'no', 'off', or '0' (in any case).

    Raises:
        argparse.ArgumentTypeError: If `value` is not one of those words.

    """
    choices = {
        'true': True, 'yes': True, 'on': True, '1': True,
        'false': False, 'no': False, 'off': False, '0': False}
    try:
        return choices[value.lower()]
    except KeyError as error:
        message = f'expected true or false, not {value!r}'
        raise argparse.ArgumentTypeError(message) from error


if __name__ == '__main__':
    main()
