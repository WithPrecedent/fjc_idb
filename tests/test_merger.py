"""Tests for merging appellate and district data."""

from __future__ import annotations

import pandas as pd

from fjc_idb import __main__ as cli
from fjc_idb import merger


def _appeals() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'appeal_type': ['4', '19', '19', '1', '4'],
            'district_of_origin': [
                'D. Me.', 'D. Me.', 'D. Me.', None, 'D. Vt.'],
            'district_docket': ['1000001', '1000001', '1100002', None, '1'],
            'criminal_defendant_number': [None, '2', None, None, None],
            'appeal_date': pd.to_datetime(
                ['2012-06-01', '2013-01-01', '2013-01-01', None, '2014-01-01']),
        }
    ).astype({
        'district_of_origin': 'string',
        'district_docket': 'string',
        'criminal_defendant_number': 'string',
    })


def _civil() -> pd.DataFrame:
    # Docket 1000001 was reopened after the appeal, so it has two records.
    return pd.DataFrame(
        {
            'circuit': ['First Circuit', 'First Circuit'],
            'district': ['D. Me.', 'D. Me.'],
            'district_courthouse': ['Portland, ME', 'Portland, ME'],
            'docket': ['1000001', '1000001'],
            'filing_date': pd.to_datetime(['2010-01-05', '2015-03-01']),
            'disposition': ['Judgment on jury verdict', 'Dismissed, other'],
            'pending': [0, 0],
        }
    ).astype({'district': 'string', 'docket': 'string'})


def _criminal() -> pd.DataFrame:
    # The criminal docket 1000001 has the same number as the civil one.
    return pd.DataFrame(
        {
            'circuit': ['First Circuit'] * 3,
            'district': ['D. Me.'] * 3,
            'district_courthouse': ['Bangor, ME'] * 3,
            'docket': ['1000001', '1000001', '1100002'],
            'defendant_number': [1, 2, 1],
            'filing_date': pd.to_datetime(
                ['2010-02-01', '2010-02-01', '2011-05-01']),
            'disposition_1': ['Convicted on guilty plea'] * 3,
            'pending': [0, 0, 0],
        }
    ).astype({'district': 'string', 'docket': 'string'})


def test_match_civil() -> None:
    matched = merger._match(
        _appeals(), _civil(), ['3', '4', '12'], ['docket'])
    # Only the civil appeal matches, with the record filed before the appeal.
    assert list(matched.index) == [0]
    assert matched.loc[0, 'disposition'] == 'Judgment on jury verdict'


def test_match_criminal() -> None:
    matched = merger._match(
        _appeals(), _criminal(), [str(code) for code in range(13, 23)],
        ['docket', 'defendant_number'])
    assert sorted(matched.index) == [1, 2]
    # Appeal 1 matches defendant 2, and appeal 2 (without a defendant number)
    # matches the only defendant on its docket.
    assert matched.loc[1, 'defendant_number'] == 2
    assert matched.loc[2, 'defendant_number'] == 1


def test_added_columns() -> None:
    appeals = _appeals()
    civil = merger._match(appeals, _civil(), ['3', '4', '12'], ['docket'])
    criminal = merger._match(
        appeals, _criminal(), [str(code) for code in range(13, 23)],
        ['docket', 'defendant_number'])
    merged = appeals.join(merger._get_added_columns(civil, criminal))
    assert merged['district_match'].tolist()[:3] == [
        'civil',
        'criminal',
        'criminal',
    ]
    assert pd.isna(merged['district_match'][3])
    assert pd.isna(merged['district_match'][4])
    # Shared columns are combined, and redundant columns are left out.
    assert merged['district_filing_date'][0] == pd.Timestamp('2010-01-05')
    assert merged['district_filing_date'][2] == pd.Timestamp('2011-05-01')
    assert merged['district_disposition'][0] == 'Judgment on jury verdict'
    assert merged['district_disposition_1'][1] == 'Convicted on guilty plea'
    for name in (
        'district_circuit',
        'district_district',
        'district_district_courthouse',
        'district_defendant_number',
    ):
        assert name not in merged


def test_command_line_merge(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        cli.idb, 'run', lambda *args, **kwargs: calls.append('run'))
    monkeypatch.setattr(
        cli, 'merge_district',
        lambda *args, **kwargs: calls.append(('merge', args, kwargs)))
    cli.main(['all', '--start-year', '2008', '--stop-year', '2026',
              '--merge-district'])
    assert calls[:3] == ['run', 'run', 'run']
    assert calls[3][0] == 'merge'
    assert calls[3][1] == (2008, 2026)
