"""Tests for downloading FJC IDB files."""

from __future__ import annotations

import io

import pytest

from fjc_idb import __main__ as cli
from fjc_idb import downloader, options

PAGE = '''
<a href="/sites/default/files/idb/codebooks/Appeals%20Codebook.pdf">
  Appeals Codebook.pdf</a>
<a href="/sites/default/files/idb/textfiles/ap08on_0.zip">
  Appellate Cases Cumulative File</a>
<a href="/sites/default/files/idb/datasets/ap08.sas7bdat">
  Appellate Cases Fiscal Year 2008</a>
<a href="/sites/default/files/idb/datasets/ap09_0.sas7bdat">
  Appellate Cases Fiscal Year 2009</a>
<a href="/sites/default/files/idb/datasets/apjun09.sas7bdat">
  Appellate Cases 12-Months Ending June 30, 2009</a>
<a href="/sites/default/files/idb/datasets/ap08to09.zip">
  Appellate Cases 5 Year File</a>
'''


@pytest.fixture
def requests(monkeypatch):
    """Replaces web requests with a fake FJC website and records them."""
    requested = []

    def fake_open(url):
        requested.append(url)
        if url == options._DATASET_PAGES['appellate']:
            return io.BytesIO(PAGE.encode())
        return io.BytesIO(f'contents of {url}'.encode())

    monkeypatch.setattr(downloader, '_open', fake_open)
    return requested


def test_list_files(requests) -> None:
    root = 'https://www.fjc.gov/sites/default/files/idb/datasets'
    assert downloader.list_files('appellate') == {
        2008: f'{root}/ap08.sas7bdat',
        2009: f'{root}/ap09_0.sas7bdat',
    }


def test_download(requests, tmp_path) -> None:
    files = downloader.download('appellate', 2008, 2010, tmp_path)
    folder = tmp_path / 'appellate'
    assert sorted(path.name for path in folder.iterdir()) == [
        'ap08.sas7bdat',
        'ap09_0.sas7bdat',
    ]
    assert (tmp_path / 'docs' / 'Appeals Codebook.pdf').exists()
    assert len(files) == 3
    assert (folder / 'ap08.sas7bdat').read_text().endswith('ap08.sas7bdat')
    # Existing files are skipped.
    requests.clear()
    assert downloader.download('appellate', 2008, 2009, tmp_path) == []
    assert requests == [options._DATASET_PAGES['appellate']]


def test_download_overwrite(requests, tmp_path) -> None:
    folder = tmp_path / 'appellate'
    folder.mkdir()
    (folder / 'ap09.sas7bdat').write_text('old file with an older name')
    files = downloader.download(
        'appellate', 2009, 2009, tmp_path, overwrite = True, codebook = False)
    assert files == [folder / 'ap09_0.sas7bdat']
    assert [path.name for path in folder.iterdir()] == ['ap09_0.sas7bdat']


def test_download_invalid_case_type(tmp_path) -> None:
    with pytest.raises(ValueError):
        downloader.download('bankruptcy', 2008, 2009, tmp_path)


def test_command_line_download(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        cli, 'download_files',
        lambda *args, **kwargs: calls.append(('download', args, kwargs)) or [])
    monkeypatch.setattr(
        cli.idb, 'run',
        lambda *args, **kwargs: calls.append(('run', args, kwargs)))
    cli.main(['appellate', '--start-year', '2008', '--download-only'])
    assert [call[0] for call in calls] == ['download']
    assert calls[0][2]['overwrite'] is False
    calls.clear()
    cli.main(['civil', '--start-year', '2008', '--download', '--overwrite'])
    assert [call[0] for call in calls] == ['download', 'run']
    assert calls[0][2]['overwrite'] is True
