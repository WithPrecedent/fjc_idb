# Criminal District Codebook

This codebook describes the criminal CSV file that `fjc-idb` creates from the
FJC Integrated Database (IDB) files for criminal defendants in the U.S.
district courts. It follows the FJC's *Criminal Integrated Database (IDB): 1996
to Present* codebook (August 2016), adapted to the column names, labels, and
added columns that `fjc-idb` produces. The original codebook is available from
the [FJC IDB page](https://www.fjc.gov/research/idb).

```python exec="true" session="criminal"
from fjc_idb import rules


def table(codes, code_header = 'Code', label_header = 'Label'):
    lines = [f'| {code_header} | {label_header} |', '| --- | --- |']
    lines += [f'| `{code}` | {label} |' for code, label in codes.items()]
    print('\n'.join(lines))
```

## About the data

- **One row per defendant.** Unlike the civil and appellate files, each row is
  a defendant, not a case. A case with several defendants has several rows,
  identified by `defendant_number` or `defendant_key`.
- **Years.** The IDB has one file for each fiscal year, which runs from
  October 1 through September 30. Each file is a snapshot with one record for
  every defendant filed or terminated during the year, or still pending at its
  end. A record holds both the filing and, once the defendant is terminated,
  the closing data. The record is the most recent one the court sent, so
  earlier information (such as the charges in a superseded indictment) can be
  overwritten.
- **Pending defendants.** A pending defendant is repeated in every file until
  terminated, so `fjc-idb` keeps pending defendants only from the latest file
  in the range. In those rows, `pending` is 1 and `data_file_year` is 2099.
  A defendant terminated in one year and terminated again in a later year
  (for example, after a retrial) has a row for each termination.
- **Code changes.** The FJC updated the data back to 1996 to use the codes in
  place since fiscal year 2012. Some fields were created in 2012 and are
  missing or calculated for earlier years, as noted below.
- **Column order.** The CSV keeps the order of the original file, with each
  added column placed after the columns it comes from. The tables below group
  the columns by subject instead.

## Conventions

| Topic | How `fjc-idb` handles it |
| --- | --- |
| Column names | Each original IDB field is renamed to a descriptive name. Pass `rename_columns=False` (or `--rename-columns false`) to keep the IDB names, such as `FOFFCD1`. |
| Missing data | The IDB code `-8` and the date 1900-01-01 mean missing data. They are written as `NA` in date columns and left blank in all other columns. |
| Labels | Columns marked with a label table have their codes replaced by labels. Codes with no label are kept as they are. |
| Indicators | Added indicator columns are `1` for yes and `0` for no. |
| Added columns | Columns marked *added* are created by `fjc-idb` and are not in the IDB. |
| Numbered columns | The IDB records up to five offenses for each defendant at filing and at termination, ranked by severity. Columns ending in `_1` through `_5` describe offense 1 (the most severe) through offense 5. |

## Defendant and case identification

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `fiscal_year` | FISCALYR | integer | Fiscal year of the file the row comes from. |
| `circuit` | CIRCUIT | text | Circuit where the case was located. See [Circuits](#circuits). The IDB stores this field as text (`09`); it is matched to the same labels as the other files. |
| `district` | DISTRICT | text | District where the case was located. The IDB's two-character code is combined with the circuit to match the codebook's district list. See [Districts](#districts). |
| `district_courthouse` | OFFICE | text | Office where the case was located, as "City, ST". See [Courthouses](#courthouses). |
| `docket` | DOCKET | text | District docket number: a two-digit calendar year and a five-digit sequence number. |
| `defendant_number` | DEFNO | integer | System-assigned number of the defendant in the case, which the court cannot change. |
| `court_defendant_number` | CTDEF | integer | Court-assigned number of the defendant, which the court can renumber. Missing before fiscal year 2012. |
| `defendant_name` | NAME | text | Defendant's name. Blank in the public files. |
| `reopen_sequence` | REOPSEQ | integer | `0` for an original proceeding, `1` for the first reopening, and so on. Reopenings terminated before fiscal year 2012 are all `1`. |
| `case_type` | TYPEREG | text | Type of the current case. See [Case types](#case-types). |
| `case_type_transfer` | TYPETRN | text | Type of the originating case, if the case was transferred. |
| `case_type_magistrate` | TYPEMAG | text | Type of the magistrate judge case, if the case was merged from one. |
| `defendant_key` | DEFLGKY | text | Unique key for the defendant: district, office, docket number, case type, defendant number, and reopen sequence. |
| `case_key` | CASLGKY | text | Unique key for the case: district, office, docket number, case type, and reopen sequence. |
| `magistrate_docket` | MAGDOCK | text | Docket number of a magistrate judge case later merged into the criminal case. |
| `magistrate_defendant_number` | MAGDEF | integer | Defendant number in that magistrate judge case. |
| `county` | COUNTY | text | Five-digit FIPS code of the county where the offense was committed (two digits for the state and three for the county). `88888` means outside the home state and `99999` outside the United States. |

## Status and record

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `pending` | STATUSCD | integer | `1` for a pending defendant (IDB code `E`) and `0` for a terminated defendant (`J`). |
| `data_file_year` | TAPEYEAR | integer | Fiscal year in which the defendant was terminated, or 2099 for pending defendants. |
| `fugitive_status` | FUGSTAT | text | See [Fugitive status](#fugitive-status). |
| `fugitive_start_date` | FGSTRTDATE | date | Date the defendant became a fugitive. Missing before fiscal year 2012. |
| `fugitive_end_date` | FGENDDATE | date | Date a fugitive defendant was taken into custody. Missing before fiscal year 2012. |
| `source` | SOURCE | text | Where the record came from: `CMECF` (sent by the court through CM/ECF), `DSNAPSHOT` or `FUGITIVE` (snapshots from the AO's legacy system), or `MASTER` (the legacy live database). |
| `version` | VER | integer | `0` for the first version of the record and increasing by one with each update. Missing before fiscal year 2012. |
| `load_date` | LOADDATE | date | Date the record was loaded into the AO's database. |
| `last_update_date` | UPDATE | date | Date of the last action on the record. Discontinued in March 2012. |

## Filing

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `filing_date` | FILEDATE | date | Date the case was first docketed in the district court. |
| `proceeding_date` | PROCDATE | date | Date proceedings began on the charges (or the date of a felony waiver of indictment). The AO uses this date to count filings. |
| `proceeding` | PROCCD | text | Nature of the proceeding. See [Proceedings](#proceedings). |
| `first_appearance_date` | APPDATE | date | Date the defendant first appeared before a judicial officer in the district where a charge was pending. |
| `first_appearance` | APPCD | text | Event by which the defendant first appeared. See [First appearances](#first-appearances). |
| `filing_judge` | FJUDGE | text | Code of the judge assigned at filing. Blank in the public files. |
| `filing_counsel` | FCOUNSEL | text | Type of counsel at filing. See [Counsel](#counsel). |
| `transfer_district` | TRANDIST | text | District of an intra-district transfer. |
| `transfer_office` | TRANOFF | text | Office from which an intra-district transfer took place. |
| `transfer_docket` | TRANDOCK | text | Original docket number in an intra-district transfer. |
| `transfer_defendant_number` | TRANDEF | text | Original defendant number in an intra-district transfer. |

### Offenses at filing

For each offense from 1 to 5:

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `filing_title_section_N` | FTITLEN | text | Title and section of the U.S. Code charged, such as `21:846=CD.F`. |
| `filing_offense_level_N` | FOFFLVLN | text | Level of the offense. See [Offense levels](#offense-levels). |
| `filing_offense_ao_N` | FOFFCDN | text | Four-digit AO offense code, maintained until fiscal year 2005. |
| `filing_offense_d2_N` | D2FOFFCDN | text | Four-digit D2 offense code, which replaced the AO codes in fiscal year 2005 and was added to earlier records. |
| `filing_severity_N` | FSEVN | text | Severity code used to rank the offenses. See [Severity codes](#severity-codes). |

### Offense groups

| Column | IDB fields | Type | Description |
| --- | --- | --- | --- |
| *offense indicators* | D2FOFFCD1–5 | integer | *Added.* One column for each group of offense codes, which is 1 if any of the defendant's five filing offenses is in the group. Blank if all five are missing. See [Offense groups](#offense-group-codes). |
| *offense indicators at termination* | D2TOFFCD1–5 | integer | *Added.* The same columns built from the five termination offenses, each with `_at_termination` added to its name. Blank for defendants who have not been terminated. |

The groups use the D2 codes because they are the current classification and
cover every year in the data.

## Termination

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `disposition_date` | DISPDATE | date | Date judicial proceedings concluded. |
| `sentencing_date` | SENTDATE | date | Date the final sentence was entered on the docket. |
| `termination_date` | TERMDATE | date | Date the case was closed: the disposition date if all counts were dismissed or ended in acquittal, or the sentencing date if the defendant was found guilty on any count. The AO uses this date to count terminations. |
| `filing_to_termination` | FILEDATE, TERMDATE | integer | *Added.* Days from `filing_date` to `termination_date`. Blank if either date is missing. |
| `days_to_proceeding` | INT1 | integer | Days from the earlier of the filing date and first appearance date to the proceeding date. |
| `days_proceeding_to_disposition` | INT2 | integer | Days from the proceeding date to the disposition date. |
| `days_disposition_to_sentencing` | INT3 | integer | Days from the disposition date to the sentencing date. |
| `termination_courthouse` | TERMOFF | text | Office where the case was terminated, as "City, ST". See [Courthouses](#courthouses). |
| `termination_judge` | TJUDGE | text | Code of the judge who terminated the case. Blank in the public files. |
| `termination_counsel` | TCOUNSEL | text | Type of counsel at termination. See [Counsel](#counsel). |

### Offenses and sentences at termination

For each offense from 1 to 5, ranked by the severity of the disposition and
penalty. The AO reports `disposition_1` as the defendant's final disposition.

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `termination_title_section_N` | TTITLEN | text | Title and section of the U.S. Code. |
| `termination_offense_level_N` | TOFFLVLN | text | Level of the offense. See [Offense levels](#offense-levels). |
| `termination_offense_ao_N` | TOFFCDN | text | Four-digit AO offense code. |
| `termination_offense_d2_N` | D2TOFFCDN | text | Four-digit D2 offense code. |
| `termination_severity_N` | TSEVN | text | Severity code. See [Severity codes](#severity-codes). |
| `disposition_N` | DISPN | text | Disposition of the offense. See [Dispositions](#dispositions). |
| `prison_months_N` | PRISTIMN | integer | Months of prison imposed, or a special code. See [Sentence codes](#sentence-codes). |
| `prison_code_N` | PRISCDN | text | Whether the prison sentence is concurrent or consecutive. See [Sentence codes](#sentence-codes). |
| `probation_months_N` | PROBMONN | integer | Months of probation imposed, or `-1` for less than one month. |
| `probation_code_N` | PROBCDN | text | Whether the probation sentence is concurrent or consecutive. See [Sentence codes](#sentence-codes). |
| `supervised_release_months_N` | SUPVRELN | integer | Months of supervised release imposed. |
| `fine_N` | FINEAMTN | integer | Fine imposed in dollars, not including restitution or special assessments. |

### Sentence totals

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `prison_total_months` | PRISTOT | integer | Total prison time for all convictions, accounting for concurrent and consecutive sentences, or a special code. See [Sentence codes](#sentence-codes). |
| `probation_total_months` | PROBTOT | integer | Total probation time for all convictions, or `-1` for less than one month. |
| `fine_total` | FINETOT | integer | Total fine for all convictions, in dollars. |

## Counts

These columns are `1` if the defendant counts toward the AO's published
statistics for the fiscal year and `0` if not. They were created in fiscal year
2012 and calculated for fiscal years 2005 through 2011.

| Column | IDB field | Counts defendants |
| --- | --- | --- |
| `count_filed_including_transfers` | CTFILTRN | filed, including transfers between districts |
| `count_filed` | CTFIL | filed, excluding transfers between districts |
| `count_filed_without_reopens` | CTFILWOR | filed as original proceedings |
| `count_filed_reopens` | CTFILR | filed by reopening, remand, appeal, or retrial |
| `count_terminated_including_transfers` | CTTRTRN | terminated, including transfers between districts |
| `count_terminated` | CTTR | terminated, excluding transfers between districts |
| `count_terminated_without_reopens` | CTTRWOR | terminated in original proceedings |
| `count_terminated_reopens` | CTTRR | terminated after reopening, remand, appeal, or retrial |
| `count_pending` | CTPN | pending at the end of the year, including long-term fugitives |
| `count_pending_without_fugitives` | CTPNWOF | pending at the end of the year, excluding long-term fugitives |

## Code lists

### Circuits

```python exec="true" session="criminal"
table({code: label for code, label in rules.circuits.items() if code != '-8'})
```

### Districts

The IDB stores a two-character district code. `fjc-idb` adds the two-digit
circuit in front of it (circuit 9 and district `73` become `0973`), which is
how the appellate codebook lists districts.

??? note "District codes"

    ```python exec="true" session="criminal"
    table(rules.districts)
    ```

### Courthouses

Office codes repeat across districts, so each office is identified by its
combined district code followed by the office code (`09732` is Los Angeles).
The names come from Appendix D of the appellate codebook, which uses the same
office codes, and are followed by the state's two-letter abbreviation. By
default, twelve names misspelled in that codebook are corrected; pass
`fix_city_spellings=False` (or `--fix-city-spellings false`) to keep the codebook
spellings. The appellate codebook lists [every courthouse code](appellate.md#courthouses).

### Case types

```python exec="true" session="criminal"
table(rules.case_types)
```

### Fugitive status

```python exec="true" session="criminal"
table(rules.fugitive_statuses)
```

### Proceedings

```python exec="true" session="criminal"
table(rules.proceedings)
```

Before fiscal year 2012, the AO treated code `13` as a transfer between
districts.

### First appearances

Codes `A` through `D` apply to cases that began before a magistrate judge, and
`1` through `3` to cases that began as criminal cases.

```python exec="true" session="criminal"
table(rules.first_appearances)
```

### Counsel

```python exec="true" session="criminal"
table(rules.counsel)
```

Code `4` (self) expired in 1990.

### Offense levels

Petty offenses assigned to magistrate judges are not reported to the AO.

```python exec="true" session="criminal"
table(rules.offense_levels)
```

### Offense group codes

Each group is an indicator column. The same groups are used in the appellate
codebook, where the offense codes are listed with their descriptions.

```python exec="true" session="criminal"
table(
    {name: ', '.join(f'`{code}`' for code in codes)
     for name, codes in rules.criminal_offense_columns.items()},
    'Column', 'D2 codes')
```

### Severity codes

A severity code has three characters. The first gives the maximum prison
sentence, the second the type of crime, and the third the maximum fine. For
example, `235` means four to five years of prison, a crime against a person,
and a fine of $5,001 to $10,000. Codes range from `A00` (lowest) to `939`
(highest).

| Code | Maximum prison sentence | Type of crime | Maximum fine |
| --- | --- | --- | --- |
| `A` | None | — | — |
| `B` | 6 months or less | — | — |
| `C` | 7 months to 1 year | — | — |
| `0` | 1 year and 1 day to 2 years | None | None |
| `1` | 2 years and 1 day to 3 years | Moral turpitude | $1–$100 |
| `2` | 4 to 5 years | Property | $101–$500 |
| `3` | 6 to 10 years | Personal | $501–$1,000 |
| `4` | 11 to 15 years | — | $1,001–$5,000 |
| `5` | 16 to 20 years | — | $5,001–$10,000 |
| `6` | 21 to 25 years | — | $10,001–$20,000 |
| `7` | Over 25 years | — | $20,001–$50,000 |
| `8` | Life | — | $50,001–$99,999 |
| `9` | Death | — | $100,000 or more |

### Dispositions

```python exec="true" session="criminal"
table(rules.criminal_dispositions)
```

Code `1` also covers dismissals of counts alleging only criminal forfeiture and
cases remanded or with an appeal affirmed or denied. Dismissals without
prejudice use code `15`.

### Sentence codes

Prison months (`prison_months_N` and `prison_total_months`) are a number of
months or one of these codes, which `fjc-idb` keeps as numbers:

| Code | Meaning |
| --- | --- |
| `-1` | Imprisonment of less than one month |
| `-2` | Guilty, no sentence imposed |
| `-3` | Sealed sentence |
| `-4` | Life imprisonment |
| `-5` | Death |

Prison and probation codes (`prison_code_N` and `probation_code_N`) are a
letter followed by a three-digit number of counts:

| Letter | Meaning |
| --- | --- |
| `C` | Concurrent |
| `S` | Consecutive |
| `M` | Single count, or multiple counts of a single offense |
