"""Tests for fjc_idb."""

from __future__ import annotations

import pandas as pd
import pytest

from fjc_idb import __main__ as cli
from fjc_idb import options
from fjc_idb.main import (
    _add_pro_se_party,
    _add_separate_opinions,
    _drop_stale_pending,
    _parse_jurisdiction,
    export_data,
    import_data,
    parse_data,
    parse_docket_number,
)


def _raw_appellate() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'CIRCUIT': [9.0, 0.0],
            'DOCKET': ['0801434', '1910001'],
            'DKTDATE': pd.to_datetime(['2008-05-02', '2019-01-15']),
            'APPELLAN': ['SMITH', '-8'],
            'AGENCY': ['-9', 'XYZ'],
            'FILEFEE': ['-8', 'FP'],
            'FEDCAP': ['Y', '-8'],
            'PUBSTAT': [2.0, 5.0],
            'TRANSCODE': ['E', 'J'],
            'TRMFEE': ['N', '-8'],
            'ENBANC': ['Y', '-8'],
            'STATUSCD': ['L', 'S'],
            'TORPROCSUB': [2.0, -8.0],
            'APPTYPE': [17.0, 4.0],
            'TRMTYPE': [15.0, -8.0],
            'REOPEN': ['-8', 'M'],
            'NOS': [530.0, -9.0],
            'OFFENSE': ['-9', '0100'],
            'DCIRC': [9.0, -8.0],
            'DDIST': ['73', '-8'],
            'DOFFICE': ['2', '-8'],
            'APPDATE': pd.to_datetime(['2008-05-01', '2019-03-01']),
            'HEARDATE': pd.to_datetime(['2008-05-08', '1900-01-01']),
            'JUDGDATE': pd.to_datetime(['2008-05-30', '1900-01-01']),
            'TAPEYEAR': [2008.0, 2099.0],
        }
    )


def test_parse_docket_number() -> None:
    assert parse_docket_number('0801434') == 'No. 08-1434'
    assert parse_docket_number('1910001') == 'No. 19-10001'
    with pytest.raises(ValueError):
        parse_docket_number('-8')


def test_parse_jurisdiction() -> None:
    data = pd.DataFrame(
        {
            'NOS': ['510', '530', '540', '100', '100', '100', '100'],
            'JURIS': [2, 3, 5, 1, 2, 4, -8],
        }
    )
    parsed = _parse_jurisdiction(data)
    assert parsed['JURIS'].tolist() == [
        'Federal Prisoner',
        'State Prisoner',
        'Local Prisoner',
        'U.S. Government Plaintiff',
        'U.S. Government Defendant',
        'Diversity of Citizenship',
        'N/A',
    ]
    data = pd.DataFrame({'NOS': [-9.0], 'JURIS': [-9.0]})
    assert _parse_jurisdiction(data)['JURIS'].tolist() == [
        'Non-Civil Case'
    ]


def test_add_pro_se_party() -> None:
    data = pd.DataFrame(
        {
            'PROSEFLE': ['1', '0', '0', '0', '-8', '-8'],
            'PROSETRM': ['0', '3', '0', '-8', '2', '-8'],
        }
    )
    parsed = _add_pro_se_party(data)
    assert parsed['pro_se_party'].tolist()[:5] == [1, 1, 0, 0, 1]
    assert pd.isna(parsed['pro_se_party'][5])
    assert list(parsed.columns) == ['PROSEFLE', 'PROSETRM', 'pro_se_party']


def test_add_separate_opinions() -> None:
    data = pd.DataFrame(
        {
            'JDG1INV': ['A', 'G', 'D', '-8'],
            'JDG2INV': ['P', 'E', 'F', '-8'],
            'JDG3INV': ['P', 'C', 'P', '-8'],
        }
    )
    parsed = _add_separate_opinions(data)
    assert parsed['concurrences'].tolist()[:3] == [0, 2, 1]
    assert parsed['dissents'].tolist()[:3] == [0, 2, 1]
    assert pd.isna(parsed['concurrences'][3])
    assert pd.isna(parsed['dissents'][3])
    assert list(parsed.columns)[3:] == ['concurrences', 'dissents']


def test_parse_data() -> None:
    data = parse_data(_raw_appellate(), 'appellate', rename_columns=True)
    assert data['circuit'].tolist() == ['Ninth Circuit', 'D.C. Circuit']
    assert data['docket_num_idb'].tolist() == ['0801434', '1910001']
    assert data['docket_number'].tolist() == ['No. 08-1434', 'No. 19-10001']
    assert data['district_of_origin'][0] == 'Central District of California'
    assert data['district_courthouse'][0] == 'Los Angeles, CA'
    assert pd.isna(data['district_courthouse'][1])
    assert data['agency'].tolist() == ['None', 'XYZ']
    assert data['nature_of_suit'].tolist() == [530, -9]
    assert data['criminal_offense'].tolist() == [-9, 100]
    assert data['criminal_homicide'].tolist() == [0, 1]
    assert data['criminal_murder'].tolist() == [0, 1]
    assert data['criminal_drugs'].tolist() == [0, 0]
    assert data['civil_habeas'].tolist() == [1, 0]
    assert data['civil_habeas_death_penalty'].tolist() == [0, 0]
    assert data['data_file_year'].tolist() == [2008, 2099]
    assert data['district_of_origin'].isna().sum() == 1
    assert pd.isna(data['appellant'][1])
    assert pd.isna(data['in_forma_pauperis'][0])
    assert data['in_forma_pauperis'][1] == 1
    assert data['criminal_capital_case'].tolist() == [1, 0]
    assert data['new_filing'].tolist() == [1, 0]
    assert data['enbanc'].tolist() == ['1', 'Missing/Pending']
    assert data['pending'].tolist() == [0, 1]
    assert data['published'].tolist() == [1, 0]
    assert data['writ_termination'][0] == 'Mandamus (fee paid)'
    assert pd.isna(data['writ_termination'][1])
    assert data['in_forma_pauperis_termination'].tolist() == [
        '0',
        'Missing/Pending',
    ]
    assert data['criminal_guidelines_sentence'].tolist() == [1, 0]
    assert data['criminal_guidelines_conviction'].tolist() == [1, 0]
    assert data['civil_non_us_party'].tolist() == [0, 1]
    assert data['criminal_guidelines_general'].tolist() == [0, 0]
    assert data['criminal_guidelines_sentence_at_termination'].tolist() == [
        1,
        0,
    ]
    assert data['criminal_guidelines_conviction_at_termination'].tolist() == [
        0,
        0,
    ]
    assert data['appeal_type_missing_at_termination'].tolist() == [0, 1]
    assert pd.isna(data['reopened_or_remanded'][0])
    assert data['reopened_or_remanded'][1] == 'Remanded from the Supreme Court'
    assert pd.isna(data['judgment_date'][1])
    assert data['hearing_to_judgment'][0] == 22
    assert data['notice_to_judgment'][0] == 29
    assert data['notice_to_hearing'][0] == 7
    for column in (
        'hearing_to_judgment',
        'notice_to_judgment',
        'notice_to_hearing',
    ):
        assert pd.isna(data[column][1])
    assert (
        parse_data(_raw_appellate(), 'appellate', False).columns[0] == 'CIRCUIT'
    )


def test_fix_city_spellings() -> None:
    raw = pd.DataFrame(
        {
            'DOCKET': ['0801434'],
            'APPTYPE': [4.0],
            'DCIRC': [11.0],
            'DDIST': ['3C'],
            'DOFFICE': ['3'],
        }
    )
    fixed = parse_data(raw, 'appellate')
    assert fixed['district_courthouse'][0] == 'Coral Gables, FL'
    original = parse_data(raw, 'appellate', fix_city_spellings=False)
    assert original['district_courthouse'][0] == 'Coral Cables, FL'


def test_parse_civil() -> None:
    raw = pd.DataFrame(
        {
            'CIRCUIT': [11.0, 9.0],
            'DISTRICT': ['3C', '73'],
            'OFFICE': ['3', '-8'],
            'DOCKET': ['2500001', '2600002'],
            'ORIGIN': [2.0, 1.0],
            'FILEDATE': pd.to_datetime(['2025-01-01', '2026-01-01']),
            'JURIS': [3.0, 2.0],
            'NOS': [440.0, 530.0],
            'TERMDATE': pd.to_datetime(['2025-03-02', '1900-01-01']),
            'DISP': [13.0, -8.0],
            'JUDGMENT': [1.0, 0.0],
            'PROSE': [0.0, 1.0],
            'IFP': ['-8', 'FP'],
            'STATUSCD': ['L', 'S'],
            'TAPEYEAR': [2025.0, 2099.0],
        }
    )
    data = parse_data(raw, 'civil')
    assert data['circuit'].tolist() == ['Eleventh Circuit', 'Ninth Circuit']
    assert data['district'][0] == 'Southern District of Florida'
    assert data['district_courthouse'][0] == 'Coral Gables, FL'
    assert pd.isna(data['district_courthouse'][1])
    assert data['origin'][0] == 'Removed from state court'
    assert data['jurisdiction'].tolist() == [
        'Federal Question',
        'Federal Prisoner',
    ]
    assert data['disposition'][0] == 'Dismissed as settled'
    assert data['judgment_for'][0] == 'Plaintiff'
    assert pd.isna(data['judgment_for'][1])
    assert data['in_forma_pauperis'].tolist() == [0, 1]
    assert data['pro_se_party'].tolist() == [0, 1]
    assert data['civil_civil_rights'].tolist() == [1, 0]
    assert data['civil_habeas'].tolist() == [0, 1]
    assert data['pending'].tolist() == [0, 1]
    assert data['filing_to_termination'][0] == 60
    assert pd.isna(data['filing_to_termination'][1])


def test_parse_criminal() -> None:
    raw = pd.DataFrame(
        {
            'CIRCUIT': ['09', '11'],
            'DISTRICT': ['73', '3C'],
            'OFFICE': ['2', '3'],
            'STATUSCD': ['J', 'E'],
            'FILEDATE': pd.to_datetime(['2025-01-01', '2026-01-01']),
            'FCOUNSEL': [6.0, -8.0],
            **{
                f'D2FOFFCD{number}': codes
                for number, codes in zip(
                    range(1, 6),
                    [['6801', '8720'], ['0100', '-8'], ['-8', '-8'],
                     ['-8', '-8'], ['-8', '-8']],
                )
            },
            'TERMDATE': pd.to_datetime(['2025-07-01', '1900-01-01']),
            'TERMOFF': ['2', '-8'],
            **{
                f'D2TOFFCD{number}': codes
                for number, codes in zip(
                    range(1, 6),
                    [['6801', '-8'], ['-8', '-8'], ['-8', '-8'],
                     ['-8', '-8'], ['-8', '-8']],
                )
            },
            'DISP1': [4.0, -8.0],
            'PRISTIM1': [60.0, -8.0],
            'TAPEYEAR': [2025.0, 2099.0],
        }
    )
    data = parse_data(raw, 'criminal')
    assert data['circuit'].tolist() == ['Ninth Circuit', 'Eleventh Circuit']
    assert data['district_courthouse'].tolist() == [
        'Los Angeles, CA',
        'Coral Gables, FL',
    ]
    assert data['termination_courthouse'][0] == 'Los Angeles, CA'
    assert pd.isna(data['termination_courthouse'][1])
    assert data['pending'].tolist() == [0, 1]
    assert data['filing_counsel'][0] == 'Public or community defender'
    assert data['criminal_drugs'].tolist() == [1, 0]
    assert data['criminal_homicide'].tolist() == [1, 0]
    assert data['criminal_immigration'].tolist() == [0, 1]
    assert data['criminal_drugs_at_termination'][0] == 1
    assert data['criminal_homicide_at_termination'][0] == 0
    assert pd.isna(data['criminal_drugs_at_termination'][1])
    assert data['disposition_1'][0] == 'Convicted on guilty plea'
    assert data['prison_months_1'][0] == 60
    assert data['filing_to_termination'][0] == 181


def test_drop_stale_pending() -> None:
    raw = _raw_appellate()
    earlier, latest = _drop_stale_pending([raw, raw])
    assert earlier['TAPEYEAR'].tolist() == [2008.0]
    assert len(latest) == 2


def test_export_data(tmp_path) -> None:
    data = parse_data(_raw_appellate(), 'appellate')
    export_data(
        data, tmp_path, 'test.csv', {'judgment_date': 'NA', 'appellant': ''}
    )
    exported = pd.read_csv(
        tmp_path / 'test.csv', dtype=str, keep_default_na=False
    )
    assert exported['judgment_date'].tolist() == ['2008-05-30', 'NA']
    assert exported['docket_date'].tolist() == ['2008-05-02', '2019-01-15']
    assert exported['appellant'].tolist() == ['SMITH', '']
    assert exported['district_of_origin'].tolist() == [
        'Central District of California',
        '',
    ]


def test_command_line(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        cli.idb, 'run', lambda *args, **kwargs: calls.append((args, kwargs)))
    cli.main(
        ['civil', 'civil', '--start-year', '2010', '--rename-columns', 'false'])
    assert calls == [
        (
            ('civil', 2010, None),
            {
                'data_folder': options._DATA_FOLDER,
                'rename_columns': False,
                'fix_city_spellings': options._FIX_CITY_SPELLINGS,
            },
        )
    ]
    calls.clear()
    cli.main(['all', '--start-year', '2008', '--stop-year', '2009'])
    assert [args for args, _ in calls] == [
        ('appellate', 2008, 2009),
        ('civil', 2008, 2009),
        ('criminal', 2008, 2009),
    ]
    calls.clear()
    cli.main([
        'appellate', '--start-year', '2008', '--rename-columns',
        '--fix-city-spellings', 'No'])
    assert calls[0][1]['rename_columns'] is True
    assert calls[0][1]['fix_city_spellings'] is False
    with pytest.raises(SystemExit):
        cli.main(['appellate', '--start-year', '2008', '--rename-columns', 'x'])
    with pytest.raises(SystemExit):
        cli.main(['bankruptcy', '--start-year', '2008'])
    with pytest.raises(SystemExit):
        cli.main(['appellate'])


def test_import_data() -> None:
    data_folder = options._DATA_FOLDER / 'appellate'
    if not any(data_folder.glob('ap08*.sas7bdat')):
        pytest.skip('FJC IDB appellate data is not available.')
    data = import_data('appellate', 2008, 2008, data_folder)
    assert not data.empty
    assert set(data['TAPEYEAR']) == {2008}
    assert isinstance(data['DOCKET'][0], str)
    with pytest.raises(FileNotFoundError):
        import_data('appellate', 1901, 1901, data_folder)


if __name__ == '__main__':
    test_import_data()
