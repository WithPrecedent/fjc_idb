# Appellate Codebook

This codebook describes the appellate CSV file that `fjc_idb` creates from the
FJC Integrated Database (IDB) files for the U.S. courts of appeals. It follows
the FJC's *Appeals Documentation, FY 2008 – Present* (revised February 10,
2021), adapted to the column names, labels, and added columns that `fjc_idb`
produces. The original codebook is available from the
[FJC IDB page](https://www.fjc.gov/research/idb).

```python exec="true" session="appellate"
from fjc_idb import base, rules


def table(codes, code_header = 'Code', label_header = 'Label'):
    lines = [f'| {code_header} | {label_header} |', '| --- | --- |']
    lines += [f'| `{code}` | {label} |' for code, label in codes.items()]
    print('\n'.join(lines))
```

## About the data

- **One row per appeal.** Each row is an appeal docketed in a court of appeals.
  Docket numbers are unique only within a circuit, and an appeal that is
  reopened or remanded can appear again with a new row.
- **Years.** The IDB has one file for each statistical year, which runs from
  October 1 through September 30 (statistical year 2026 began on October 1,
  2025). Each file holds the appeals terminated that year. The most recent
  files also hold a snapshot of appeals still pending when the file was made.
- **Pending appeals.** A pending appeal is repeated in each file until it ends,
  so `fjc_idb` keeps pending appeals only from the latest file in the range. In
  those rows, `pending` is 1 and `data_file_year` is 2099.
- **Column order.** The CSV keeps the order of the original file, with each
  added column placed next to the column it comes from. The tables below
  group the columns by subject instead.

## Conventions

| Topic | How `fjc_idb` handles it |
| --- | --- |
| Column names | Each original IDB field is renamed to a descriptive name. Pass `rename_columns=False` (or `--rename-columns false`) to keep the IDB names, such as `CIRCUIT`. |
| Missing data | The IDB code `-8` and the date 1900-01-01 mean missing data. They are written as `NA` in date columns and left blank in all other columns, unless a column below says otherwise. |
| Not applicable | The IDB code `-9` means a field does not apply (for example, a nature of suit for a criminal appeal). It is kept as `-9` unless a column below says otherwise. |
| Labels | Columns marked with a label table have their codes replaced by labels. Codes with no label are kept as they are. |
| Indicators | Added indicator columns are `1` for yes and `0` for no. |
| Added columns | Columns marked *added* are created by `fjc_idb` and are not in the IDB. |

## Case identification

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `circuit` | CIRCUIT | text | Circuit in which the appeal was filed. See [Circuits](#circuits). |
| `docket_num_idb` | DOCKET | text | Docket number as stored in the IDB: a two-digit year and a serial number, with a 0 inserted before four-digit serial numbers (`1701234` for 17-1234). Five-digit serial numbers have no inserted 0 (`1910001`). |
| `docket_number` | DOCKET | text | *Added.* The docket number in standard form, such as `No. 17-1234`. |
| `reopened_or_remanded` | REOPEN | text | Whether the appeal was reopened or remanded. See [Reopened or remanded](#reopened-or-remanded). Blank for appeals that were never reopened or remanded; the IDB codes these as missing. |
| `docket_date` | DKTDATE | date | Date the appeal was docketed in the court of appeals. |
| `data_file_year` | TAPEYEAR | integer | Statistical year of the file the row comes from: the year the appeal was terminated, or 2099 for pending appeals. |
| `pending` | STATUSCD | integer | `1` for a pending appeal (IDB code `S`) and `0` for a terminated appeal (`L`). |
| `new_filing` | TRANSCODE | integer | Type of the last transaction on the record: `1` for a new filing (`E`) and `0` for a change to an existing record, including its termination (`J`). The undocumented code `R`, which appears on a few pending appeals, is left blank. |
| `last_date` | TRANSDATE | date | Date of the last action on the record (system generated). |

## Parties

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `us_appellant` | USAPT | integer | `1` if the United States initiated the appeal and `0` if not. |
| `appellant` | APPELLAN | text | Name of the party who initiated the appeal (truncated to 20 characters). |
| `us_appellee` | USAPE | integer | `1` if the appeal was filed against the United States and `0` if not. |
| `appellee` | APPELLEE | text | Name of the party against whom the appeal was taken (truncated to 20 characters). |
| `pro_se_at_filing` | PROSEFLE | integer | Pro se parties at filing. See [Pro se parties](#pro-se-parties). |
| `pro_se_at_termination` | PROSETRM | text | Pro se parties at termination. See [Pro se parties](#pro-se-parties). |
| `pro_se_party` | PROSEFLE, PROSETRM | integer | *Added.* `1` if either column shows a pro se party (codes 1, 2, or 3), `0` if neither does, and blank if both are missing. |
| `in_forma_pauperis` | FILEFEE | integer | `1` if a party was granted permission to proceed in forma pauperis at filing (`FP`). The IDB stores `-8` for all other appeals, which is left blank. |
| `in_forma_pauperis_termination` | TRMFEE | text | In forma pauperis status at termination: `1` if granted (`FP`), `0` if not (`N`), and `Missing/Pending` for `-8`, which appears only on pending appeals. |

## Type of appeal

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `appeal_type` | APPTYPE | text | Type of appeal at filing. See [Appeal types](#appeal-types). |
| *appeal type indicators* | APPTYPE | integer | *Added.* One column for each appeal type, named in [Appeal types](#appeal-types). |
| `appeal_type_termination` | TRMTYPE | text | Type of appeal as reported by the clerk at termination, using the same codes as `appeal_type`. It differs from `appeal_type` in about 0.07% of terminated appeals, almost all in 2008–2010 and among the sentencing guideline codes. It is `-8` for pending appeals. |
| *appeal type indicators at termination* | TRMTYPE | integer | *Added.* The same indicator columns built from `appeal_type_termination`, each with `_at_termination` added to its name. For pending appeals, only `appeal_type_missing_at_termination` is 1. |
| `writ` | ORGPROC | integer | Nature of an original proceeding (coded only when `appeal_type` is 6). See [Writs](#writs) for the codes. |
| `writ_termination` | TORPROCSUB | text | Nature of an original proceeding as reported at termination. See [Writs](#writs). |
| `agency` | AGENCY | text | Federal agency involved in an administrative appeal (coded only when `appeal_type` is 1 or 2). See [Agencies](#agencies). Non-agency appeals (IDB code `-9`) are labeled `None`. |

## Lower court

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `circuit_of_origin` | DCIRC | text | Circuit of the district or bankruptcy court where the case was first filed. See [Circuits](#circuits). |
| `district_of_origin` | DDIST | text | District or bankruptcy court where the case was first filed. The IDB's two-character code is combined with the circuit to match the codebook's district list. See [Districts](#districts). |
| `district_courthouse` | DOFFICE | text | Office of the district or bankruptcy court where the case was first filed, as "City, ST". See [Courthouses](#courthouses). |
| `district_docket` | DDOCKET | text | Docket number in the district or bankruptcy court. |
| `district_docket_date` | DDKTDATE | date | Date the case was docketed in the district or bankruptcy court. |
| `appeal_date` | APPDATE | date | Date the notice of appeal was filed in the lower court. For interlocutory appeals under 28 U.S.C. § 1292(b), the date the application was granted. |
| `district_judge` | DJUDGE | text | Code of the judge whose decision was appealed. Blank in the public files. |
| `jurisdiction` | JURIS | text | Basis of federal jurisdiction in civil appeals. See [Jurisdiction](#jurisdiction). |
| `nature_of_suit` | NOS | integer | Nature of the action in civil appeals. See [Nature of suit](#nature-of-suit). `-9` for non-civil appeals. |
| *nature of suit indicators* | NOS | integer | *Added.* One column for each group of nature of suit codes. See [Nature of suit groups](#nature-of-suit-groups). |
| `criminal_offense` | OFFENSE | integer | Offense charged in criminal appeals. Codes are stored as numbers, so leading zeros are dropped (`0100` becomes `100`). See [Criminal offenses](#criminal-offenses). `-9` for non-criminal appeals. |
| *offense indicators* | OFFENSE | integer | *Added.* One column for each group of offense codes. See [Offense groups](#offense-groups). Blank when the offense is missing. |
| `criminal_defendant_number` | DDEFNUM | text | Defendant number in the district court for criminal cases. |
| `criminal_capital_case` | FEDCAP | integer | `1` for a federal capital case (`Y`), such as an appeal in which a defendant was sentenced to death, and `0` otherwise (`-8`). |

## Disposition

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `when_terminated` | DISP | text | How the appeal was terminated. See [Termination codes](#termination-codes). |
| `disposition` | OUTCOME | text | Outcome of an appeal decided on the merits (`when_terminated` 1, 2, or 3). See [Termination codes](#termination-codes). |
| `procedural_termination` | PROCTERM | integer | Type of procedural termination after judicial action (`when_terminated` 4). See [Termination codes](#termination-codes). |
| `non_merits_disposition` | METHOD | text | Type of termination by the clerk without judicial action (`when_terminated` 5). See [Termination codes](#termination-codes). |
| `original_proceeding_termination` | OPDISP | text | Outcome of an original proceeding: `1` granted, `2` denied, `3` dismissed or other. |
| `judgment_date` | JUDGDATE | date | Date the final judgment, decree, or order was entered. |
| `published_status` | PUBSTAT | integer | Type of opinion or order. See [Publication](#publication). |
| `published` | PUBSTAT | integer | *Added.* `1` for a published opinion (codes 2, 4, 6), `0` for an unpublished one (1, 3, 5, 7), and blank otherwise, including the undocumented code 0. |
| `joined_appeal` | JOINAPP | text | Type of joined appeal: `0` none, `1` cross appeal, `2` consolidated appeal, `3` lead case of a consolidated group. |
| `joined_docket` | CONSDKT | text | Docket number (in IDB form) of the first appeal of a cross appeal or the lead case of a consolidated group. |
| `enbanc` | ENBANC | text | `1` if the appeal was heard en banc (`Y`), `0` if not (`N`), and `Missing/Pending` for `-8`, which appears only on pending appeals. |

## Dates and timing

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `briefing_notice_date` | CRECDATE | date | Date the briefing notice or schedule was issued. Missing in every file from 2008 to 2026. |
| `brief_filed_date` | BRFILED | date | Date the last brief was received before hearing or submission. |
| `submitted_date` | SUBDATE | date | For appeals decided on the merits without a hearing, the date the appeal was submitted to the first judge on the panel. |
| `hearing_date` | HEARDATE | date | Date the appeal was argued before a panel. |
| `hearing_to_judgment` | HEARDATE, JUDGDATE | integer | *Added.* Days from `hearing_date` to `judgment_date`. |
| `notice_to_judgment` | APPDATE, JUDGDATE | integer | *Added.* Days from `appeal_date` to `judgment_date`. |
| `notice_to_hearing` | APPDATE, HEARDATE | integer | *Added.* Days from `appeal_date` to `hearing_date`. |

Each added gap is blank if either of its dates is missing. A few gaps are
negative or very long because of errors in the IDB dates.

## Panel and opinions

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `opinion_types` | OPINION | text | Separate opinions on the panel: `6` dissent only, `7` concurrence only, `8` both (not en banc), `9` both (en banc). |
| `judge_1`, `judge_2`, `judge_3` | JDGCODE1–3 | text | Statistical codes of the judges on the panel. Blank in the public files. |
| `judge_1_opinion_type`, `judge_2_opinion_type`, `judge_3_opinion_type` | JDG1INV–JDG3INV | text | Each judge's role. See [Judge roles](#judge-roles). |
| `concurrences` | JDG1INV–JDG3INV | integer | *Added.* Number of the three judges who wrote a concurrence (roles B, D, E, or G). Blank if all three roles are missing. |
| `dissents` | JDG1INV–JDG3INV | integer | *Added.* Number of the three judges who wrote a dissent (roles C, F, or G). Blank if all three roles are missing. |

For en banc appeals, the IDB records only three judges, so `concurrences` and
`dissents` count only the opinions of those three.

## Code lists

### Circuits

```python exec="true" session="appellate"
table({code: label for code, label in rules.circuits.items() if code != '-8'})
```

### Reopened or remanded

```python exec="true" session="appellate"
table(rules.reopened_or_remanded)
```

### Pro se parties

| Code | Meaning |
| --- | --- |
| `0` | Neither party is pro se |
| `1` | Appellant is pro se |
| `2` | Appellee is pro se |
| `3` | Both parties are pro se |

### Appeal types

`appeal_type` keeps the IDB code. Each code also has an indicator column named
below, and the indicator columns built from `appeal_type_termination` add
`_at_termination` to these names. Code 17 (guideline case, sentence and
conviction) has no column of its own: it is marked in both
`criminal_guidelines_sentence` and `criminal_guidelines_conviction`.

| Code | Type of appeal |
| --- | --- |
| `1` | Administrative review |
| `2` | Administrative enforcement |
| `3` | Civil, U.S. |
| `4` | Civil, private |
| `6` | Original proceeding |
| `10` | Bankruptcy, direct from bankruptcy court |
| `11` | Bankruptcy, from a bankruptcy appellate panel |
| `12` | Bankruptcy, from a district court |
| `13` | Guideline case, general |
| `14` | Pre-guideline case or other |
| `15` | Guideline case, sentence only |
| `16` | Guideline case, conviction only |
| `17` | Guideline case, sentence and conviction |
| `18` | Criminal case other than 14–17 |
| `19` | Direct criminal appeal |
| `20` | Interlocutory criminal appeal |
| `21` | Post-conviction criminal appeal |
| `22` | Miscellaneous criminal case |

```python exec="true" session="appellate"
table(rules.appeal_types_to_columns, 'Code', 'Indicator column')
```

### Writs

`writ` keeps the IDB code and `writ_termination` uses these labels.

```python exec="true" session="appellate"
table(rules.writs)
```

### Agencies

These labels follow the codebook. Sixteen codes that appear in the data but not
in the codebook (such as `DHS`, `TSA`, and `CSRT`) were identified from the
party names and circuits of the appeals that use them.

??? note "Agency codes"

    ```python exec="true" session="appellate"
    table(rules.agencies)
    ```

### Districts

The IDB stores a two-character district code. `fjc_idb` adds the two-digit
circuit in front of it (circuit 9 and district `73` become `0973`), which is
how the codebook lists districts.

??? note "District codes"

    ```python exec="true" session="appellate"
    table(rules.districts)
    ```

### Courthouses

Office codes repeat across districts, so each office is identified by its
combined district code followed by the office code (`09732` is Los Angeles).
Names are taken from Appendix D of the codebook, followed by the state's
two-letter abbreviation. Office codes that are not in the codebook, such as
Northern District of Florida offices 7, 8, and 9, are left as combined codes.

By default, twelve names that are misspelled in the codebook are corrected
(for example, `Coral Cables, FL` becomes `Coral Gables, FL`). Pass
`fix_city_spellings=False` (or `--fix-city-spellings false`) to keep the codebook
spellings.

```python exec="true" session="appellate"
table(
    {code: f'{rules.offices[code]} → {name}'
     for code, name in rules.office_spelling_fixes.items()},
    'Code', 'Correction')
```

??? note "Courthouse codes"

    ```python exec="true" session="appellate"
    table(rules.offices)
    ```

### Jurisdiction

Jurisdiction is coded only for civil appeals. For prisoner petitions (nature of
suit 510, 530, 535, 540, or 550), the codes have different meanings, which
`fjc_idb` labels separately.

| Code | Label (other civil appeals) | Label (prisoner petitions) |
| --- | --- | --- |
| `1` | U.S. Government Plaintiff | — |
| `2` | U.S. Government Defendant | Federal Prisoner |
| `3` | Federal Question | State Prisoner |
| `4` | Diversity of Citizenship | — |
| `5` | Local Question (US Territory) | Local Prisoner |
| `-8` | N/A | N/A |
| `-9` | Non-Civil Case | Non-Civil Case |

### Nature of suit

??? note "Nature of suit codes (Appendix A)"

    --8<-- "docs/codebooks/includes/appellate_nos.md"

### Nature of suit groups

Each group is an indicator column that is 1 if `nature_of_suit` is one of its
codes. The same groups are used in the civil codebook.

```python exec="true" session="appellate"
table(
    {name: ', '.join(f'`{code}`' for code in codes) or '(no codes yet)'
     for name, codes in rules.civil_nature_of_suit_columns.items()},
    'Column', 'Codes')
```

### Criminal offenses

??? note "Criminal offense codes (Appendix B)"

    --8<-- "docs/codebooks/includes/offenses.md"

### Offense groups

Each group is an indicator column that is 1 if the offense code is one of its
codes. The same groups are used in the criminal codebook. Some codes in the
data, such as `7831`, are not in Appendix B; they come from the newer D2
offense classification used by the criminal files.

```python exec="true" session="appellate"
table(
    {name: ', '.join(f'`{code}`' for code in codes)
     for name, codes in rules.criminal_offense_columns.items()},
    'Column', 'Codes')
```

### Termination codes

`when_terminated` (DISP):

| Code | Meaning |
| --- | --- |
| `1` | Merits, after oral hearing |
| `2` | Merits, after submission without hearing |
| `3` | Merits, after submission (no longer used) |
| `4` | Procedural, after other judicial action |
| `5` | Procedural, without judicial action |

`disposition` (OUTCOME), for terminations on the merits:

| Code | Meaning |
| --- | --- |
| `1` | Affirmed or enforced, including affirmed and remanded |
| `2` | Reversed or vacated, including reversed and remanded |
| `3` | Affirmed in part and reversed or vacated in part |
| `5` | Dismissed (no genuine issue, moot, lacking merit, or frivolous) |
| `6` | Remanded (the sole action was to send the case back) |
| `7` | Other merits disposition |
| `9` | Certificate of appealability denied |

`procedural_termination` (PROCTERM), for procedural terminations after judicial
action:

| Code | Meaning |
| --- | --- |
| `1` | Jurisdictional defects |
| `2` | Voluntary dismissal or settlement (FRAP 42) |
| `5` | Default |
| `6` | Certificate of probable cause denied |
| `7` | Transferred to another court of appeals |
| `8` | Dismissed, other |
| `9` | Certificate of appealability denied |

`non_merits_disposition` (METHOD), for terminations by the clerk without
judicial action:

| Code | Meaning |
| --- | --- |
| `1` | Voluntary dismissal or settlement (FRAP 42) |
| `3` | Default |
| `4` | Other |

### Publication

| Code | Meaning | `published` |
| --- | --- | --- |
| `1` | Unpublished, oral | 0 |
| `2` | Published, written, signed | 1 |
| `3` | Unpublished, written, signed | 0 |
| `4` | Published, written, unsigned, reasoned | 1 |
| `5` | Unpublished, written, unsigned, reasoned | 0 |
| `6` | Published, written, unsigned, without comment | 1 |
| `7` | Unpublished, written, unsigned, without comment | 0 |

The code `0`, which is not in the codebook, appears on about 85,000 appeals and
is left blank in `published`.

### Judge roles

| Code | Role |
| --- | --- |
| `A` | Wrote the majority opinion |
| `B` | Co-wrote the majority opinion and wrote a concurrence |
| `C` | Co-wrote the majority opinion and wrote a dissent |
| `D` | Co-wrote the majority opinion and wrote a concurrence and dissent |
| `E` | Concurred |
| `F` | Dissented |
| `G` | Concurred and dissented |
| `H` | Co-wrote the majority opinion |
| `P` | Panel member who wrote no opinion |

The codes `I` and `J` appear a few times but are not in the codebook.
