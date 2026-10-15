# Tutorial

This tutorial walks through downloading the FJC Integrated Database (IDB)
files and turning them into clean CSV files.

## 1. Install fjc_idb

`fjc_idb` requires Python 3.11 or later.

```sh
pip install fjc_idb
```

To work from a copy of the repository instead, install it with
[uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

## 2. Choose a data folder

`fjc_idb` keeps the IDB files, the FJC codebooks, and the CSV files it creates
in one data folder with this layout:

```text
fjc_idb/                  <- the data folder
├── appellate/
│   ├── ap08.sas7bdat
│   └── ...
├── district/
│   ├── civil/
│   │   ├── cv08_0.sas7bdat
│   │   └── ...
│   └── criminal/
│       ├── cr08.sas7bdat
│       └── ...
└── docs/                 <- the FJC codebooks
```

Pass the location of this folder with `--data-folder` (or `data_folder` in
Python), or set it once as the default in `options.py` (see the
[Advanced User Guide](advanced.md)). The folder and its subfolders do not need
to exist yet: downloading creates any that are missing, and
`fjc_idb.create_folders('path/to/fjc_idb')` creates them without downloading
anything.

## 3. Download the IDB files

`fjc_idb` downloads the yearly SAS files from the
[FJC IDB page](https://www.fjc.gov/research/idb) and saves them in the data
folder under their FJC names. It covers the three datasets that `fjc_idb`
parses; bankruptcy data is not included.

| Case type | FJC dataset | Years available |
| --- | --- | --- |
| `appellate` | Appellate cases filed, terminated, and pending, FY 2008 to present | 2008 on |
| `civil` | Civil cases filed, terminated, and pending, SY 1988 to present | 1988 on |
| `criminal` | Criminal defendants filed, terminated, and pending, FY 1996 to present | 1996 on |

From the command line:

```sh
fjc-idb appellate --start-year 2008 --stop-year 2026 --data-folder path/to/fjc_idb --download-only
```

Or from Python:

```python
import fjc_idb

fjc_idb.download('appellate', 2008, 2026, data_folder = 'path/to/fjc_idb')
```

Files that are already in the data folder are skipped, so running the command
again only fetches what is missing. The codebook for each case type is saved
in `docs/`. The file for the current year is updated by the FJC during the
year; add `--overwrite` (or `overwrite = True`) to replace it with the latest
version. To see which years the FJC publishes, use `fjc_idb.list_files`:

```python
fjc_idb.list_files('criminal')   # {1996: 'https://www.fjc.gov/...', ...}
```

The files are large: about 14 MB per year for appellate data, 60 to 180 MB
per year for civil data, and 160 to 200 MB per year for criminal data.

!!! note "Downloading the files yourself"

    You can also download the files from the FJC website by hand. Keep their
    names as they are (the FJC sometimes adds a suffix, as in
    `ap12_0.sas7bdat`) and put them in the folders shown above.

## 4. Export the data

From the command line, give the case types and the first year to include:

```sh
fjc-idb appellate --start-year 2008 --stop-year 2026 --data-folder path/to/fjc_idb
```

`python -m fjc_idb` works the same way. Use `all` for every case type, and add
`--download` to fetch any missing files first:

```sh
fjc-idb all --start-year 2008 --data-folder path/to/fjc_idb --download
```

Or, from Python:

```python
import fjc_idb

fjc_idb.run('appellate', 2008, 2026, data_folder = 'path/to/fjc_idb')
```

Each case type is saved next to its yearly files, for example
`appellate/fjc_idb_appellate_data_2008_2026.csv`. When no stop year is given,
the current year is used. For 2008 through 2026, the appellate file takes about
a minute, the civil file about five minutes, and the criminal file about seven.

## 5. Understand the output

Each CSV file has one row per appeal, civil case, or criminal defendant, with:

- descriptive column names in place of the IDB's short field names,
- readable labels in place of many codes (for example, `Ninth Circuit` instead
  of `9`),
- missing data written as `NA` in date columns and left blank elsewhere,
- added columns, such as indicators for groups of offenses and the number of
  days between key dates, and
- pending cases taken only from the latest file in the range.

The codebooks in this User Guide describe every column:

- [Appellate Codebook](codebooks/appellate.md)
- [Criminal District Codebook](codebooks/criminal.md)
- [Civil District Codebook](codebooks/civil.md)

## 6. Analyze the data

See [Recipes](recipes.md) for loading the CSV files with pandas and for example
analyses.
