# Advanced User Guide

## Command line options

```text
fjc-idb CASE_TYPE [CASE_TYPE ...] --start-year YEAR [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `CASE_TYPE` | (required) | One or more of `appellate`, `civil`, and `criminal`, or `all`. |
| `--start-year` | (required) | The first statistical year to include. |
| `--stop-year` | the current year | The last statistical year to include. |
| `--data-folder` | `options._DATA_FOLDER` | The data folder, laid out as in the [Tutorial](tutorial.md#2-choose-a-data-folder). |
| `--rename-columns [true\|false]` | `options._RENAME_COLUMNS` (true) | Whether to use descriptive column names (`true`) or keep the IDB field names (`false`). |
| `--fix-city-spellings [true\|false]` | `options._FIX_CITY_SPELLINGS` (true) | Whether to correct the twelve city names misspelled in the FJC codebook (`true`) or keep them (`false`). |
| `--download` | off | Download files missing from the data folder before exporting. |
| `--download-only` | off | Download files missing from the data folder without exporting. |
| `--overwrite` | off | With `--download` or `--download-only`, replace files that already exist. |
| `--merge-district` | off | After exporting, merge the appellate data with the civil and criminal district data (see [Merging appellate and district data](#merging-appellate-and-district-data)). |

The export options are arguments of `fjc_idb.run` and the functions in
`fjc_idb.main`, and the download options are arguments of `fjc_idb.download`.

## Downloading

`fjc_idb.download` reads the FJC dataset page for a case type, finds the link
for each requested year, and saves the file in the data folder. Only the files
for single years are used, not the cumulative, five- and ten-year, or
twelve-months-ending-June files on the same pages, and bankruptcy data is not
included.

- **Folders.** Any folders of the data folder that do not exist yet are
  created first, for every case type and the `docs` folder. Use
  `fjc_idb.create_folders` to create them without downloading.
- **Existing files.** A year is skipped if the data folder already has a file
  for it. With `overwrite`, the new file is downloaded first and then any older
  file for the year is removed, so a failed download never loses data.
- **Partial downloads.** Files are written under a temporary `.part` name and
  renamed when complete.
- **Missing years.** Years the FJC has not published are skipped with a
  warning.
- **Codebooks.** The codebook linked from each dataset page is saved in the
  `docs` folder of the data folder (pass `codebook = False` to skip it).

The dataset pages are listed in `options._DATASET_PAGES`. If the FJC moves a
page, update its address there.

## Merging appellate and district data

`fjc_idb.merge_district` (or `--merge-district`) adds the district court's
record of each appealed case to the appellate data and saves the result in the
appellate folder as
`fjc_idb_appellate_with_district_data_{start_year}_{stop_year}.csv`. It needs
the appellate, civil, and criminal files for the same years.

```python
import fjc_idb

merged = fjc_idb.merge_district(2008, 2026, data_folder = 'path/to/fjc_idb')
```

**How appeals are matched.**

- An appeal is matched with the civil or criminal data according to its
  appeal type (`rules.district_civil_appeal_types` and
  `rules.district_criminal_appeal_types`). This matters because a district
  can give a civil case and a criminal case the same docket number.
- Civil appeals are matched by district and docket number. Criminal appeals
  are matched by district, docket number, and defendant number; an appeal
  without a defendant number is matched only if the docket has a single
  defendant.
- A reopened, remanded, or transferred case can have several district records
  with the same docket number. The appeal is matched with the latest record
  filed on or before the notice of appeal or, if none was, with the latest
  record.
- Administrative appeals, original proceedings, and appeals from bankruptcy
  courts and bankruptcy appellate panels have no district record and are not
  matched.

**Columns.** The district columns are added with the prefix `district_`, such
as `district_filing_date`, `district_disposition`, or `district_prison_total_months`.
Columns that civil and criminal records share (such as the filing and
termination dates) are combined into one column. Columns that only repeat the
match keys or the appellate data are left out; they are listed in
`rules.redundant_civil_columns` and `rules.redundant_criminal_columns`. The
added `district_match` column is `civil` or `criminal` for a matched appeal and
blank otherwise.

**Coverage.** A district case is in the district files only if it was
terminated in the range of years or was still pending, so appeals filed long
after the start year match far more often than early ones. For 2008 through
2026, 93% of civil appeals and 80% of criminal appeals were matched (98% and
88% of those filed in 2010 or later). The merged data always uses the
descriptive column names.

The merge reads the civil and criminal files one year at a time and keeps only
the records of appealed cases. For 2008 through 2026 it takes about as long as
exporting all three case types.

## Changing the defaults

The defaults live in `src/fjc_idb/options.py` and apply to the Python functions
and the command line alike.

| Option | Default | Description |
| --- | --- | --- |
| `_DATA_FOLDER` | `data/courts/fjc_idb`, four folders above `options.py` | The data folder. |
| `_RENAME_COLUMNS` | `True` | Whether to rename columns. |
| `_FIX_CITY_SPELLINGS` | `True` | Whether to correct misspelled city names. |
| `_DATE_FORMAT` | `%Y-%m-%d` | How dates are written to the CSV files. |
| `_DATASET_PAGES` | the FJC dataset pages | The web page that links to the yearly files for each case type. |
| `_DOWNLOAD_TIMEOUT` | `300` | Seconds to wait for the FJC website before a download fails. |
| `_ENCODING` | `latin-1` | The text encoding of the SAS files. |
| `_MISSING_CODES` | `('-8', -8)` | Codes treated as missing when combining district and office codes and when building indicator columns. |
| `_MISSING_DATE` | `1900-01-01` | The date the IDB uses for missing dates. |
| `_PENDING_COLUMN`, `_PENDING_YEAR` | `TAPEYEAR`, `2099` | The column and value that mark pending records. |

## How the pipeline works

`fjc_idb.run` processes one yearly file at a time:

1. **Import.** The yearly SAS file is read. Pending records are dropped from
   every file except the latest one, because a pending case is repeated in
   each file until it ends.
2. **Prepare.** Columns that depend on the raw codes are added (such as
   indicator columns and `docket_number`), and district and office codes are
   combined with their circuit and district so that they match the codebook.
3. **Parse.** Each column is cleaned according to its `Column` specification:
   missing-value codes become missing data, codes are replaced by labels, and
   the column is converted to its data type. City spellings are corrected and
   the days between key dates are added.
4. **Rename.** Columns get their descriptive names.
5. **Export.** The rows are appended to the CSV file, with missing data written
   as each column's `missing_replacement`.

Because only one year is in memory at a time, even the criminal files (144
columns, about 1.7 million defendants for 2008–2026) need only one to two
gigabytes. `import_data` and `parse_data` work on a whole range at once and are
useful for short ranges or interactive work.

## Customizing columns

Each case type has a dictionary of `Column` instances in `fjc_idb.base`
(`appellate_columns`, `civil_columns`, and `criminal_columns`), keyed by the
column's new name. A `Column` describes how to parse one IDB field:

```python
Column(
    'JUDGMENT',                 # the IDB field name
    'judgment_for',             # the new column name
    str,                        # str, int, or 'date'
    missing_value = ['-8', '0'],  # code(s) meaning missing, or None
    missing_replacement = '',   # what to write for missing data
    decoder = rules.judgments)  # labels that replace the codes
```

To change how a column is parsed, edit its entry. For example, to keep the
codebook's `-8` in `class_action` instead of leaving it blank:

```python
'class_action': Column('CLASSACT', 'class_action', int, missing_value = None),
```

## Customizing rules

The `fjc_idb.rules` package holds the code lists and labels, divided into
modules by case type:

| Module | Contents |
| --- | --- |
| `rules.courts` | Circuits, districts, courthouses, city spelling fixes, the date gaps added to every file, and the rules for merging appellate and district data |
| `rules.appellate` | Appeal types, agencies, writs, publication, and other appellate labels |
| `rules.offenses` | Groups of criminal offense codes, shared by the appellate and criminal files |
| `rules.civil` | Groups of nature of suit codes, jurisdiction labels, and civil district labels |
| `rules.criminal` | Criminal district labels |

Every rule is also available directly from `fjc_idb.rules`, such as
`rules.circuits`.

### Adding an indicator column

Indicator columns come from dictionaries that map a column name to a list of
codes. To add an offense group, define the list in `rules/offenses.py` and add
it to `criminal_offense_columns`:

```python
criminal_bank_robbery: list[str] = ['1100']

criminal_offense_columns: dict[str, list[str]] = {
    ...
    'criminal_bank_robbery': criminal_bank_robbery}
```

The new column then appears in both the appellate and criminal files. Nature of
suit groups work the same way through `civil_nature_of_suit_columns` in
`rules/civil.py`.

### Adding a date gap

`rules.date_gaps` maps a new column name to a pair of IDB date fields. A gap is
added to every file that has both fields:

```python
date_gaps: dict[str, tuple[str, str]] = {
    ...
    'filing_to_sentencing': ('FILEDATE', 'SENTDATE')}
```

## Notes on the data

- **Statistical years.** Since 1993, the statistical year has matched the
  federal fiscal year (October 1 through September 30).
- **Updated records.** Each record is the latest version the FJC received, so
  values that changed during a case (such as pro se status or the charges) can
  be overwritten. The FJC's research guide recommends saving each quarterly
  update to keep the full history.
- **Data quality.** Fields used in the AO's published tables have quality
  checks; others, such as pro se status, in forma pauperis status, and class
  action allegations, do not.
- **Judges.** Judge codes are blank in the public files under Judicial
  Conference policy.
