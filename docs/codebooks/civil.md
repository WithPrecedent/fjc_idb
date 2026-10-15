# Civil District Codebook

This codebook describes the civil CSV file that `fjc-idb` creates from the FJC
Integrated Database (IDB) files for civil cases in the U.S. district courts. It
follows the FJC's *Civil Documentation* for 1988 forward (October 25, 2023),
adapted to the column names, labels, and added columns that `fjc-idb`
produces. The original codebook is available from the
[FJC IDB page](https://www.fjc.gov/research/idb).

```python exec="true" session="civil"
from fjc_idb import rules


def table(codes, code_header = 'Code', label_header = 'Label'):
    lines = [f'| {code_header} | {label_header} |', '| --- | --- |']
    lines += [f'| `{code}` | {label} |' for code, label in codes.items()]
    print('\n'.join(lines))
```

## About the data

- **One row per case.** Each row is a civil case. The district, office, and
  docket number together identify a case; a case that is reopened, remanded,
  or transferred can appear again with a new row.
- **Years.** The IDB has one file for each statistical year, which runs from
  October 1 through September 30. Each file holds the cases terminated that
  year. The most recent files also hold a snapshot of cases still pending when
  the file was made.
- **Pending cases.** A pending case is repeated in each file until it ends, so
  `fjc-idb` keeps pending cases only from the latest file in the range. In
  those rows, `pending` is 1 and `data_file_year` is 2099.
- **Records are updated.** Each record reflects the case as of the latest
  update the FJC received, so information that changed during the case (such
  as pro se or in forma pauperis status) can be overwritten.
- **Column order.** The CSV keeps the order of the original file, with each
  added column placed next to the column it comes from. The tables below group
  the columns by subject instead.

## Conventions

| Topic | How `fjc-idb` handles it |
| --- | --- |
| Column names | Each original IDB field is renamed to a descriptive name. Pass `rename_columns=False` (or `--rename-columns false`) to keep the IDB names, such as `PROCPROG`. |
| Missing data | The IDB code `-8` and the date 1900-01-01 mean missing data. They are written as `NA` in date columns and left blank in all other columns, unless a column below says otherwise. |
| Labels | Columns marked with a label table have their codes replaced by labels. Codes with no label are kept as they are. |
| Indicators | Added indicator columns are `1` for yes and `0` for no. |
| Added columns | Columns marked *added* are created by `fjc-idb` and are not in the IDB. |

## Case identification

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `circuit` | CIRCUIT | text | Circuit in which the case was filed. See [Circuits](#circuits). |
| `district` | DISTRICT | text | District in which the case was filed. The IDB's two-character code is combined with the circuit to match the district list in the appellate codebook. See [Districts](#districts). |
| `district_courthouse` | OFFICE | text | Office within the district where the case was filed, as "City, ST". See [Courthouses](#courthouses). |
| `docket` | DOCKET | text | Docket number assigned by the clerk: a two-digit docket year (usually the calendar year of filing) and a five-digit sequence number. |
| `origin` | ORIGIN | text | How the case came to the district court. See [Origins](#origins). |
| `mdl_docket` | MDLDOCK | text | Four-digit docket number of the multidistrict litigation the case is part of. |
| `data_file_year` | TAPEYEAR | integer | Statistical year of the file the row comes from: the year the case was terminated, or 2099 for pending cases. |
| `pending` | STATUSCD | integer | `1` for a pending case (IDB code `S`) and `0` for a terminated case (`L`). |

## Nature of the case

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `jurisdiction` | JURIS | text | Basis of federal jurisdiction. See [Jurisdiction](#jurisdiction). |
| `nature_of_suit` | NOS | integer | Nature of the action. See [Nature of suit](#nature-of-suit). |
| *nature of suit indicators* | NOS | integer | *Added.* One column for each group of nature of suit codes. See [Nature of suit groups](#nature-of-suit-groups). |
| `us_code_title` | TITL | text | Title of the U.S. Code cited for the cause of action (optional for the courts). |
| `us_code_section` | SECTION | text | Section of the U.S. Code (optional). |
| `us_code_subsection` | SUBSECT | text | Subsection of the U.S. Code (optional). |
| `diversity_residence` | RESIDENC | text | For diversity cases, the citizenship of the plaintiff (first digit) and the defendant (second digit). See [Diversity residence](#diversity-residence). |
| `class_action` | CLASSACT | integer | `1` if the plaintiff alleged a class action under Rule 23. The IDB stores `-8` for all other cases, which is left blank. |
| `class_action_termination` | TRCLACT | text | Ruling on class certification. See [Class action rulings](#class-action-rulings). |
| `amount_demanded` | DEMANDED | integer | Amount sought by the plaintiff, in thousands of dollars. Amounts under $500 appear as `1` and amounts over $10 million as `9999`. Courts have not always reported this field in thousands, so it may be inaccurate. |
| `jury_demand` | JURY | text | Party or parties demanding a jury trial. See [Jury demands](#jury-demands). |
| `county` | COUNTY | text | County of residence of the first listed plaintiff (or of the first listed defendant when the United States is the plaintiff, or of the land in a condemnation case). `88888` means outside the home state and `99999` outside the United States. |

## Parties

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `plaintiff` | PLT | text | First listed plaintiff. |
| `defendant` | DEF | text | First listed defendant. |
| `pro_se` | PROSE | integer | Pro se parties. See [Pro se parties](#pro-se-parties). Blank in records posted before October 1995. |
| `pro_se_party` | PROSE | integer | *Added.* `1` if any party was pro se (codes 1, 2, or 3), `0` if none was, and blank if `pro_se` is missing. |
| `in_forma_pauperis` | IFP | integer | `1` for a case proceeding in forma pauperis (`FP`) and `0` otherwise. Unlike the appellate files, the civil codebook defines `-8` as "not IFP," so it becomes `0` rather than blank. Captured since October 2000. |

## Judges

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `filing_judge` | FILEJUDG | text | Judge originally assigned. Blank in the public files. |
| `filing_magistrate_judge` | FILEMAG | text | Magistrate judge originally assigned. Blank in the public files. |
| `termination_judge` | TERMJUDG | text | Judge assigned at disposition. Blank in the public files. |
| `termination_magistrate_judge` | TERMMAG | text | Magistrate judge assigned at disposition. Blank in the public files. |

## Transfers and arbitration

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `transfer_date` | TRANSDAT | date | Date the papers of a transferred case were received in this district. |
| `transfer_office` | TRANSOFF | text | Office of the district that lost the case. |
| `transfer_docket` | TRANSDOC | text | Docket number of the case in the district that lost it. |
| `transfer_origin` | TRANSORG | text | Origin of the case in the district that lost it. See [Origins](#origins). The codes `B` and `C`, which are not in the codebook, are kept as they are. |
| `arbitration_at_filing` | ARBIT | text | Participation in a court's formal arbitration program at filing. See [Arbitration](#arbitration). |
| `arbitration_at_termination` | TRMARB | text | Participation in arbitration at termination. See [Arbitration](#arbitration). |

## Dates and timing

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `filing_date` | FILEDATE | date | Date the case was filed in the district. |
| `filing_date_used_by_ao` | FDATEUSE | date | Date the AO used to place the case in a statistical year of filing. Use it to match the AO's published tables. |
| `termination_date` | TERMDATE | date | Date the court received the final judgment or the order disposing of the case. |
| `termination_date_used_by_ao` | TDATEUSE | date | Date the AO used to place the case in a statistical year of termination. |
| `filing_to_termination` | FILEDATE, TERMDATE | integer | *Added.* Days from `filing_date` to `termination_date`. Blank if either date is missing. |
| `issue_joined_date` | DJOINED | date | Date issue was joined. Rarely entered and no longer used. |
| `pretrial_conference_date` | PRETRIAL | date | Date of the pretrial conference. Rarely entered and no longer used. |
| `trial_began_date` | TRIBEGAN | date | Date trial began. Rarely entered and no longer used. |
| `trial_ended_date` | TRIALEND | date | Date trial ended. Rarely entered and no longer used. |

## Disposition

| Column | IDB field | Type | Description |
| --- | --- | --- | --- |
| `procedural_progress` | PROCPROG | text | How far the case had progressed when it was disposed of. See [Procedural progress](#procedural-progress). |
| `disposition` | DISP | text | How the case was disposed of. See [Dispositions](#dispositions). |
| `nature_of_judgment` | NOJ | text | Type of final judgment. See [Natures of judgment](#natures-of-judgment). |
| `judgment_for` | JUDGMENT | text | Party in whose favor final judgment was entered. See [Judgments](#judgments). The codebook uses both `0` and `-8` for missing data, so both are left blank. |
| `amount_received` | AMTREC | integer | Amount received, in thousands of dollars. The AO advises against using this field because courts do not report it uniformly (some use `9999` for amounts over $1 million and others as a filler). |

## Code lists

### Circuits

```python exec="true" session="civil"
table({code: label for code, label in rules.circuits.items() if code != '-8'})
```

### Districts

The IDB stores a two-character district code. `fjc-idb` adds the two-digit
circuit in front of it (circuit 9 and district `73` become `0973`), which is
how the appellate codebook lists districts.

??? note "District codes"

    ```python exec="true" session="civil"
    table(rules.districts)
    ```

### Courthouses

Office codes repeat across districts, so each office is identified by its
combined district code followed by the office code (`09732` is Los Angeles).
The names come from Appendix D of the appellate codebook, which uses the same
office codes, and are followed by the state's two-letter abbreviation. Office
codes that are not in that list, such as Northern District of Florida offices
7, 8, and 9 (used by more than 100,000 recent cases), are left as combined
codes. By default, twelve names misspelled in the codebook are corrected; pass
`fix_city_spellings=False` (or `--fix-city-spellings false`) to keep the codebook
spellings. The appellate codebook lists
[every courthouse code](appellate.md#courthouses).

### Origins

```python exec="true" session="civil"
table(rules.origins)
```

Code `13` has been valid since July 1, 2016.

### Jurisdiction

For prisoner petitions (nature of suit 510, 530, 535, 540, or 550), the codes
have different meanings, which `fjc-idb` labels separately.

| Code | Label (other cases) | Label (prisoner petitions) |
| --- | --- | --- |
| `1` | U.S. Government Plaintiff | — |
| `2` | U.S. Government Defendant | Federal Prisoner |
| `3` | Federal Question | State Prisoner |
| `4` | Diversity of Citizenship | — |
| `5` | Local Question (US Territory) | Local Prisoner |

### Nature of suit

??? note "Nature of suit codes"

    --8<-- "docs/codebooks/includes/civil_nos.md"

### Nature of suit groups

Each group is an indicator column that is 1 if `nature_of_suit` is one of its
codes. The same groups are used in the appellate codebook.

```python exec="true" session="civil"
table(
    {name: ', '.join(f'`{code}`' for code in codes) or '(no codes yet)'
     for name, codes in rules.civil_nature_of_suit_columns.items()},
    'Column', 'Codes')
```

### Diversity residence

Used only when jurisdiction is diversity of citizenship. The first digit is the
plaintiff's citizenship and the second the defendant's, so `24` is a citizen of
another state suing a corporation incorporated or based in this state.

| Digit | Citizenship |
| --- | --- |
| `1` | Citizen of this state |
| `2` | Citizen of another state |
| `3` | Citizen or subject of a foreign country |
| `4` | Incorporated or principal place of business in this state |
| `5` | Incorporated and principal place of business in another state |
| `6` | Foreign nation |

### Class action rulings

```python exec="true" session="civil"
table(rules.class_action_terminations)
```

### Jury demands

```python exec="true" session="civil"
table(rules.jury_demands)
```

### Arbitration

Only about twenty courts take part in the formal arbitration program. Code `Y`
is used only at filing.

```python exec="true" session="civil"
table(rules.arbitration)
```

### Pro se parties

| Code | Meaning |
| --- | --- |
| `0` | No pro se plaintiffs or defendants |
| `1` | One or more pro se plaintiffs, but no pro se defendants |
| `2` | One or more pro se defendants, but no pro se plaintiffs |
| `3` | One or more pro se plaintiffs and one or more pro se defendants |

### Procedural progress

Issue is joined when the defendant answers the complaint. "No court action"
means the case was withdrawn or settled without a judge or magistrate judge
taking part.

```python exec="true" session="civil"
table(rules.procedural_progress)
```

### Dispositions

```python exec="true" session="civil"
table(rules.civil_dispositions)
```

A statistical closing (`18`) is used for a case pending more than three years
with no activity for more than twelve months and all contemplated proceedings
completed.

### Natures of judgment

```python exec="true" session="civil"
table(rules.natures_of_judgment)
```

### Judgments

```python exec="true" session="civil"
table(rules.judgments)
```
