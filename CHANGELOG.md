# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.0.4

### Changed

- Updated to the `snickerdoodle` 0.4.0 template.
- Made `ruff` ignore boolean default positional arguments (`FBT002`).
- Relaxed `pydoclint` checks of type hints, class attributes, and raised exceptions.
- Excluded `uv.lock` from the large file check.
- Fixed typos in the contributing guide and noted that the project does not use a code formatter.
- Fixed the LICENSE link in the README.

## 0.0.3

### Added

- `merge_district` (and the `--merge-district` option) merges the appellate
  data with the civil and criminal district records of the appealed cases and
  saves the result as
  `fjc_idb_appellate_with_district_data_{start_year}_{stop_year}.csv`. Appeals
  are matched by district, docket number, and, for criminal cases, defendant
  number, and the district columns are added with the prefix `district_`.
- `create_folders` creates the folders of the data folder, and downloading now
  creates any that are missing.

### Changed

- The documentation refers to the package by its PyPI name, `fjc-idb`, when
  installing it and in prose; it is still imported as `fjc_idb`.

## 0.0.2

### Added

- Parsing for three types of FJC Integrated Database (IDB) files: courts of
  appeals, civil cases in the district courts, and criminal defendants in the
  district courts. The parsing follows the current FJC codebooks and has been
  tested on the files from 2008 through 2026.
- `run` exports a range of years to a CSV file, one yearly file at a time to
  keep memory use low. `import_data`, `parse_data`, and `export_data` work on
  the data in memory.
- `download` and `list_files` get the yearly SAS files and codebooks from the
  FJC website.
- The `fjc-idb` command (also `python -m fjc_idb`) with `--start-year`,
  `--stop-year`, `--data-folder`, `--rename-columns`, `--fix-city-spellings`,
  `--download`, `--download-only`, and `--overwrite`.
- Descriptive column names, labels in place of codes (circuits, districts,
  courthouses, agencies, dispositions, and more), and correct handling of the
  IDB's missing-value codes.
- Pending cases are kept only from the latest yearly file, so combining years
  does not count a case more than once.
- Added columns: indicators for appeal types and for groups of criminal
  offenses and natures of suit, the days between key dates, counts of
  concurrences and dissents, whether a decision was published, whether any
  party was pro se, and a standard appellate docket number.
- Documentation: a tutorial, an advanced user guide, recipes, an API
  reference, and codebooks for the appellate, criminal, and civil CSV files.

### Fixed

- Continuous integration: removed Python 3.10 from the test matrix (pandas 3
  requires Python 3.11 or later), fixed ruff and mypy errors, removed the
  ruff-format pre-commit hook, and replaced the outdated release action.

## 0.0.1

    Initial Commit
