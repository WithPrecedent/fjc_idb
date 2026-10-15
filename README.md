# fjc-idb

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/fjc-idb.svg?style=for-the-badge&color=cornflowerblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/fjc-idb/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/fjc_idb?style=for-the-badge&color=forestgreen&label=GitHub&logo=github)](https://github.com/WithPrecedent/fjc_idb/releases) |
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/fjc_idb/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/fjc_idb/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/fjc-idb?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/fjc-idb/) |
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=forestgreen&logo=github)](https://WithPrecedent.github.io/fjc_idb) |
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/uv-mediumpurple?style=for-the-badge&logo=uv&labelColor=gray)](https://docs.astral.sh/uv/) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-forestgreen?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-forestgreen?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot) |
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/fjc-idb?style=for-the-badge&color=cornflowerblue&label=Python&logo=python&logoColor=yellow)](https://pypi.org/project/fjc-idb/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-antiquewhite?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/)  [![Windows](https://img.shields.io/badge/Windows-blue?style=for-the-badge)](https://www.microsoft.com/en-us/windows?r=1) |
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/fjc-idb?style=for-the-badge&color=cornflowerblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/fjc-idb) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/fjc_idb?style=for-the-badge&color=forestgreen&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/fjc_idb/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/fjc_idb?style=for-the-badge&color=forestgreen&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/fjc_idb/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/fjc_idb?style=for-the-badge&color=forestgreen&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/fjc_idb/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/fjc_idb?style=for-the-badge&color=forestgreen&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/fjc_idb/forks) |
| | |

-----

## What is fjc-idb?

`fjc-idb` turns the Federal Judicial Center's [Integrated Database
(IDB)](https://www.fjc.gov/research/idb) into clean CSV files.

## Why use fjc-idb?

- **Readable columns.** IDB field names such as `PROCPROG` become descriptive
  names such as `procedural_progress`, and codes become labels from the FJC
  codebooks (`Ninth Circuit`, `Dismissed as settled`, `Los Angeles, CA`).
- **Correct missing data.** The IDB's missing-value codes (`-8` and the date
  1900-01-01) become real missing values, with the exceptions the codebooks
  describe (such as civil in forma pauperis status, where `-8` means "no").
- **No double counting.** Each yearly file repeats every case still pending
  when it was made. `fjc-idb` keeps pending cases only from the latest file, so
  combining years does not count a case more than once.
- **Useful added columns.** Indicators for appeal types and for groups of
  offenses and natures of suit, the days between key dates, counts of
  concurrences and dissents, a standard appellate docket number, and more.
- **Large files, little memory.** Years are processed one at a time, so even
  the criminal files (144 columns) need only a gigabyte or two of memory.
- **Codebooks for the output.** The documentation includes codebooks that
  describe every column of the CSV files and how it relates to the IDB.

The IDB is the most complete public source of case-level data on the federal
courts, but it is distributed as one SAS file per year with confusing field
names and a messy coding system. This repo addresses those shortcomings. But
it cannot cure the issue of missing data (particularly judge names). However,
the improvements made here should make it easier to merge the IDB data with
other sources (using the standard docket number format in `docket_number`).

`fjc-idb` has
been tested on the files from 2008 through 2026. It does not yet support the
bankruptcy files or the older files that use older codebooks.

## Getting started

### Requirements

- Python 3.11 or later
- An internet connection to download the IDB files from the
  [FJC IDB page](https://www.fjc.gov/research/idb), or the SAS (`.sas7bdat`)
  files themselves

### Installation

To install `fjc-idb`, use `pip`:

```sh
pip install fjc-idb
```

The package is installed as `fjc-idb` and imported in Python as `fjc_idb`:

```python
import fjc_idb
```

### Usage

Download the yearly files from the FJC website and export them in one step:

```sh
fjc-idb appellate --start-year 2008 --stop-year 2026 --data-folder path/to/fjc_idb --download
```

`--download` fetches only the files the data folder does not already have,
along with the FJC codebook for each case type. Use `--download-only` to fetch
files without exporting, and `--overwrite` to replace files already downloaded
(the FJC updates the file for the current year during the year). Once the files
are downloaded, leave out `--download` to export them again:

```sh
fjc-idb all --start-year 2015 --data-folder path/to/fjc_idb
```

Or from Python:

```python
import fjc_idb

fjc_idb.download('criminal', 2008, 2026, data_folder = 'path/to/fjc_idb')
fjc_idb.run('criminal', 2008, 2026, data_folder = 'path/to/fjc_idb')
```

The files are saved in this layout under their FJC names (such as
`ap08.sas7bdat` or `cv12_0.sas7bdat`). Files you download yourself work the
same way if you put them in the same folders:

```text
fjc_idb/
├── appellate/          ap08.sas7bdat, ap09.sas7bdat, ...
├── district/
│   ├── civil/          cv08_0.sas7bdat, cv09_0.sas7bdat, ...
│   └── criminal/       cr08.sas7bdat, cr09.sas7bdat, ...
└── docs/               the FJC codebooks
```

Each case type is saved next to its yearly files as
`fjc_idb_{case_type}_data_{start_year}_{stop_year}.csv`. Missing dates are
written as `NA`, and other missing values are left blank.

| Option | Default | Description |
| --- | --- | --- |
| case types | (required) | `appellate`, `civil`, `criminal`, or `all` |
| `--start-year` | (required) | The first statistical year to include |
| `--stop-year` | the current year | The last statistical year to include |
| `--data-folder` | set in `options.py` | The folder with the IDB files |
| `--rename-columns` | `true` | Use descriptive column names, or `false` to keep the IDB field names |
| `--fix-city-spellings` | `true` | Correct misspelled city names, or `false` to keep the FJC codebook spellings |
| `--download` | off | Download missing files from the FJC website before exporting |
| `--download-only` | off | Download missing files without exporting |
| `--overwrite` | off | Replace files that were already downloaded |
| `--merge-district` | off | Also merge the appellate data with the matching civil and criminal district records |

See the [documentation](https://WithPrecedent.github.io/fjc_idb) for a
tutorial, codebooks for each case type, and example analyses.

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/fjc_idb/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/fjc_idb/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/fjc_idb/code_of_conduct.md).

## Related Projects

The [Federal Judicial Center](https://www.fjc.gov) publishes the
[IDB](https://www.fjc.gov/research/idb), its codebooks, and an interactive tool
for exploring the data.

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/fjc_idb/blog/main/LICENSE).
