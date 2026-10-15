"""Downloads FJC IDB files from the FJC website.

The FJC publishes each yearly file of the Integrated Database on a dataset page
for its case type (see `options._DATASET_PAGES`). The functions in this module
read those pages and save the yearly SAS files, and the codebook for each case
type, in the layout that `run` expects:

    data_folder/
    ├── appellate/          ap08.sas7bdat, ...
    ├── district/
    │   ├── civil/          cv08_0.sas7bdat, ...
    │   └── criminal/       cr08.sas7bdat, ...
    └── docs/               the codebooks

"""

from __future__ import annotations

import datetime as dt
import html.parser
import logging
import pathlib
import re
import shutil
import urllib.parse
import urllib.request
from typing import Any

import camina

from . import main, options

logger = logging.getLogger(__name__)

_USER_AGENT = 'fjc_idb (+https://github.com/WithPrecedent/fjc_idb)'
_YEAR_LABEL = re.compile(r'(?:Statistical|Fiscal) Year (\d{4})\s*$')


def download(
    case_type: str,
    start_year: int,
    stop_year: int | None = None,
    data_folder: str | pathlib.Path = options._DATA_FOLDER,
    *,
    overwrite: bool = False,
    codebook: bool = True) -> list[pathlib.Path]:
    """Downloads the yearly FJC IDB files for a range of years.

    Files are saved under their FJC names (such as 'ap12_0.sas7bdat') in the
    folder that `run` reads for `case_type`. A year that already has a file is
    skipped unless `overwrite` is True, in which case its file is replaced. The
    FJC updates the file for the current year during the year, so overwrite it
    to get the latest data. Years the FJC has not published are skipped with a
    warning.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').
        start_year: The first statistical year to download.
        stop_year: The last statistical year to download. Defaults to None, in
            which case the current year is used.
        data_folder: The path to the folder containing the FJC IDB dataset.
            Defaults to options._DATA_FOLDER.
        overwrite: Whether to replace files that already exist. Defaults to
            False.
        codebook: Whether to also download the codebook for `case_type` into
            the 'docs' folder of `data_folder`. Defaults to True.

    Returns:
        list[pathlib.Path]: The files that were downloaded.

    Raises:
        ValueError: If `case_type` is not a recognized source type.

    Examples:
        >>> import fjc_idb
        >>> fjc_idb.download('appellate', 2008, 2026)  # doctest: +SKIP

    """
    if case_type not in options._DATASET_PAGES:
        message = (
            f'Invalid source type: {case_type}. '
            f'Must be one of {list(options._DATASET_PAGES)}.')
        raise ValueError(message)
    stop_year = stop_year or dt.datetime.now(tz = dt.UTC).year
    root = camina.pathlibify(data_folder)
    folder = main._get_data_path(case_type, root)
    links = _get_links(options._DATASET_PAGES[case_type])
    files = _get_yearly_files(links)
    downloaded = []
    for year in range(start_year, stop_year + 1):
        if year not in files:
            logger.warning(
                'The FJC has not published a %s file for %s.', case_type, year)
            continue
        prefix = options._SOURCE_PREFIXES[case_type]
        existing = sorted(folder.glob(f'{prefix}{year % 100:02d}*.sas7bdat'))
        if existing and not overwrite:
            logger.info('Skipped %s, which already exists.', existing[0].name)
            continue
        path = _save(files[year], folder)
        # Remove an older file for the year saved under a different name.
        for file in existing:
            if file != path:
                file.unlink()
        downloaded.append(path)
    if codebook:
        codebooks = [url for url in links if '/idb/codebooks/' in url]
        for url in codebooks:
            path = root / 'docs' / _file_name(url)
            if overwrite or not path.exists():
                downloaded.append(_save(url, path.parent))
    return downloaded


def list_files(case_type: str) -> dict[int, str]:
    """Returns the yearly FJC IDB files the FJC publishes for a case type.

    Only the files for single years are included, not the cumulative,
    multi-year, or twelve-months-ending-June files on the same page.

    Args:
        case_type: The source type ('appellate', 'civil', or 'criminal').

    Returns:
        dict[int, str]: The address of each yearly file, keyed by its year.

    """
    return _get_yearly_files(_get_links(options._DATASET_PAGES[case_type]))


""" Private Functions """


class _LinkParser(html.parser.HTMLParser):
    """Collects the address and text of every link in a web page."""

    def __init__(self) -> None:
        super().__init__()
        self.links: dict[str, str] = {}
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'a':
            self._href = dict(attrs).get('href')
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == 'a' and self._href is not None:
            self.links[self._href] = ' '.join(''.join(self._text).split())
            self._href = None


def _file_name(url: str) -> str:
    """Returns the file name at the end of a web address.

    Args:
        url: The web address.

    Returns:
        str: The decoded file name.

    """
    return urllib.parse.unquote(pathlib.PurePosixPath(
        urllib.parse.urlparse(url).path).name)


def _get_links(page: str) -> dict[str, str]:
    """Returns the links on a web page.

    Args:
        page: The address of the web page.

    Returns:
        dict[str, str]: The text of each link, keyed by its full address.

    """
    with _open(page) as response:
        content = response.read().decode('utf-8', errors = 'replace')
    parser = _LinkParser()
    parser.feed(content)
    return {
        urllib.parse.urljoin(page, href): text
        for href, text in parser.links.items()}


def _get_yearly_files(links: dict[str, str]) -> dict[int, str]:
    """Returns the yearly SAS files among the links on a dataset page.

    Args:
        links: The text of each link, keyed by its address.

    Returns:
        dict[int, str]: The address of each yearly file, keyed by its year.

    """
    files = {}
    for url, text in links.items():
        match = _YEAR_LABEL.search(text)
        if match and url.lower().endswith('.sas7bdat'):
            files[int(match.group(1))] = url
    return files


def _open(url: str) -> Any:
    """Opens a web address with the FJC IDB user agent.

    Args:
        url: The web address.

    Returns:
        Any: The response to the request.

    Raises:
        ValueError: If `url` is not an https address.

    """
    if urllib.parse.urlparse(url).scheme != 'https':
        message = f'Only https addresses can be downloaded, not {url}.'
        raise ValueError(message)
    request = urllib.request.Request(  # noqa: S310
        url, headers = {'User-Agent': _USER_AGENT})
    return urllib.request.urlopen(  # noqa: S310
        request, timeout = options._DOWNLOAD_TIMEOUT)


def _save(url: str, folder: pathlib.Path) -> pathlib.Path:
    """Downloads a file into a folder.

    The file is written under a temporary name and renamed when complete, so an
    interrupted download does not leave a partial file behind.

    Args:
        url: The address of the file.
        folder: The folder to save the file in.

    Returns:
        pathlib.Path: The path of the saved file.

    """
    folder.mkdir(parents = True, exist_ok = True)
    path = folder / _file_name(url)
    partial = path.with_name(f'{path.name}.part')
    logger.info('Downloading %s.', path.name)
    try:
        with _open(url) as response, partial.open('wb') as file:
            shutil.copyfileobj(response, file)
        partial.replace(path)
    finally:
        partial.unlink(missing_ok = True)
    return path
