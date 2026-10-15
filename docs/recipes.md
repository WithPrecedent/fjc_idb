# Recipes

These examples use pandas to analyze the CSV files that `fjc_idb` creates.
They assume the files were exported for 2008 through 2026 into the default data
folder; change the paths to match your own files.

## Load a CSV file with the right types

`fjc_idb` writes missing dates as `NA` and leaves other missing values blank.
Because a few party names are literally "NA", read `NA` as missing only in date
columns. The column specifications in `fjc_idb.base` say which columns are
dates:

```python
import pandas as pd

from fjc_idb import base, options


def load_csv(path, case_type, columns = None):
    """Loads an fjc_idb CSV file with missing data and dates parsed."""
    specs = getattr(base, f'{case_type}_columns').values()
    dates = [spec.name for spec in specs if spec.data_type == 'date']
    header = pd.read_csv(path, nrows = 0).columns
    columns = columns or list(header)
    na_values = {
        column: ['', 'NA'] if column in dates else [''] for column in columns}
    return pd.read_csv(
        path,
        usecols = columns,
        keep_default_na = False,
        na_values = na_values,
        parse_dates = [column for column in columns if column in dates],
        low_memory = False)


folder = options._DATA_FOLDER
appeals = load_csv(
    folder / 'appellate' / 'fjc_idb_appellate_data_2008_2026.csv', 'appellate')
```

The civil and criminal files are large (2.2 GB and 1.3 GB for 2008–2026), so
pass `columns` to load only what you need.

## Appeals

### Affirmance rate by circuit

`disposition` holds the outcome of appeals decided on the merits, which are the
appeals with `when_terminated` 1 or 2 (code 1 in `disposition` is affirmed).

```python
merits = appeals[appeals['when_terminated'].isin([1, 2])]
affirmed = (merits['disposition'] == 1).groupby(merits['circuit']).mean()
affirmed.sort_values()
```

### Share of decisions published each year

```python
terminated = appeals[appeals['pending'] == 0]
terminated.groupby('data_file_year')['published'].mean()
```

### Time from notice of appeal to judgment

```python
appeals.groupby('circuit')['notice_to_judgment'].median().sort_values()
```

### Appeals with a dissent

```python
decided = appeals[appeals['dissents'].notna()]
(decided['dissents'] > 0).groupby(decided['circuit']).mean()
```

## Criminal defendants

### Conviction rate by offense group

`disposition_1` is the defendant's final disposition. The offense group columns
mark the groups of any of the defendant's five charges at filing.

```python
criminal = load_csv(
    folder / 'district' / 'criminal' / 'fjc_idb_criminal_data_2008_2026.csv',
    'criminal',
    ['pending', 'disposition_1', 'criminal_drugs', 'criminal_firearms',
     'criminal_immigration', 'criminal_fraud'])
closed = criminal[criminal['pending'] == 0]
convicted = closed['disposition_1'].str.startswith('Convicted', na = False)
groups = [
    'criminal_drugs', 'criminal_firearms', 'criminal_immigration',
    'criminal_fraud']
pd.Series({group: convicted[closed[group] == 1].mean() for group in groups})
```

### Count defendants filed each fiscal year

The AO counts a defendant as filed in the fiscal year of the proceeding date.
A fiscal year starts on October 1, so October through December belong to the
next year:

```python
filings = load_csv(
    folder / 'district' / 'criminal' / 'fjc_idb_criminal_data_2008_2026.csv',
    'criminal',
    ['proceeding_date', 'reopen_sequence'])
filings = filings[filings['reopen_sequence'] == 0]
date = filings['proceeding_date']
fiscal_year = date.dt.year + (date.dt.month >= 10)
filings.groupby(fiscal_year).size().loc[2008:]
```

The `count_*` columns (such as `count_filed`) describe the fiscal year of the
file each record came from. Because `fjc_idb` keeps each defendant only from
the latest file that includes it, summing those columns by year undercounts
defendants who were still pending at the end of an earlier year.

## Civil cases

### Settlement rate by nature of suit group

```python
civil = load_csv(
    folder / 'district' / 'civil' / 'fjc_idb_civil_data_2008_2026.csv',
    'civil',
    ['pending', 'disposition', 'civil_civil_rights', 'civil_habeas',
     'civil_ip', 'civil_social_security'])
closed = civil[civil['pending'] == 0]
settled = closed['disposition'] == 'Dismissed as settled'
groups = [
    'civil_civil_rights', 'civil_habeas', 'civil_ip', 'civil_social_security']
pd.Series({group: settled[closed[group] == 1].mean() for group in groups})
```

## Work with the data in Python instead of CSV files

To skip the CSV files, import and parse the data directly. The whole range is
held in memory, so use short ranges for civil and criminal data:

```python
from fjc_idb import main, options

folder = options._DATA_FOLDER / 'district' / 'criminal'
raw = main.import_data('criminal', 2025, 2026, folder)
criminal = main.parse_data(raw, 'criminal')
```
