from __future__ import annotations

import dataclasses
from typing import Any

from . import rules


@dataclasses.dataclass
class Feature:
    """A dataclass representing a feature in the FJC IDB dataset."""

    import_name: str
    name: str
    data_type: str | type
    missing_value: Any = "NA"
    decoder: dict[str, Any] | None = None


appellate_columns: dict[str, Feature] = {
    "circuit": Feature("CIRCUIT", "circuit", str, decoder=rules.circuits),
    "docket_num_idb": Feature("DOCKET", "docket_num_idb", str),
    "reopened_or_remanded": Feature("REOPEN", "reopened_or_remanded", str),
    "docket_date": Feature("DKTDATE", "docket_date", "date"),
    "us_appellant": Feature("USAPT", "us_appellant", "int"),
    "appellant": Feature("APPELLAN", "appellant", str),
    "us_appellee": Feature("USAPE", "us_appellee", "int"),
    "appellee": Feature("APPELLEE", "appellee", str),
    "appeal_type": Feature("APPTYPE", "appeal_type", str),
    "writ": Feature("ORGPROC", "writ", "int"),
    "agency": Feature("AGENCY", "agency", str, decoder=rules.agencies),
    "jurisdiction": Feature("JURIS", "jurisdiction", "int"),
    "nos": Feature("NOS", "nature_of_suit", int),
    "offense": Feature("OFFENSE", "criminal_offense", int),
    "dcirc": Feature("DCIRC", "circuit_of_origin", str, decoder=rules.circuits),
    "ddist": Feature(
        "DDIST", "district_of_origin", str, decoder=rules.districts
    ),
    "doffice": Feature("DOFFICE", "district_city", str),
    "ddocket": Feature("DDOCKET", "district_docket", str),
    "ddefnum": Feature("DDEFNUM", "criminal_defendant_number", str),
    "fedcap": Feature("FEDCAP", "capital_case", str),
    "ddktdate": Feature("DDKTDATE", "district_docket_date", "date"),
    "appdate": Feature("APPDATE", "appeal_date", "date"),
    "transdate": Feature("TRANSDATE", "last_date", "date"),
    "transcode": Feature("TRANSCODE", "new_filing", str),
    "djudge": Feature("DJUDGE", "district_judge", str),
    "filefee": Feature("FILEFEE", "in_forma_pauperis", str),
    "disp": Feature("DISP", "when_terminated", str),
    "outcome": Feature("OUTCOME", "disposition", str),
    "procterm": Feature("PROCTERM", "procedural_termination", int),
    "method": Feature("METHOD", "non_merits_disposition", str),
    "published_status": Feature("PUBSTAT", "published_status", int),
    "opdisp": Feature("OPDISP", "original_proceeding_termination", str),
    "joinapp": Feature("JOINAPP", "joined_appeal", str),
    "consdkt": Feature("CONSDKT", "joined_docket", str),
    "crecdate": Feature("CRECDATE", "briefing_notice_date", "date"),
    "brfiled": Feature("BRFILED", "brief_filed_date", "date"),
    "subdate": Feature("SUBDATE", "submitted_date", "date"),
    "heardate": Feature("HEARDATE", "hearing_date", "date"),
    "judgdate": Feature("JUDGDATE", "judgment_date", "date"),
    "opinion": Feature("OPINION", "opinion_types", str),
    "jdgcode1": Feature("JDGCODE1", "judge_1", str),
    "jdg1inv": Feature("JDG1INV", "judge_1_opinion_type", str),
    "jdgcode2": Feature("JDGCODE2", "judge_2", str),
    "jdg2inv": Feature("JDG2INV", "judge_2_opinion_type", str),
    "jdgcode3": Feature("JDGCODE3", "judge_3", str),
    "jdg3inv": Feature("JDG3INV", "judge_3_opinion_type", str),
    "tapeyear": Feature("TAPEYEAR", "data_file_year", int),
    "prosefle": Feature("PROSEFLE", "pro_se_at_filing", int),
    "prosetrm": Feature("PROSETRM", "pro_se_at_termination", str),
    "statuscd": Feature("STATUSCD", "status_record", str),
    "enbanc": Feature("ENBANC", "enbanc", str),
    "trmtype": Feature("TRMTYPE", "appeal_type_termination", str),
    "torprocsub": Feature("TORPROCSUB", "writ_termination", str),
    "trmfee": Feature("TRMFEE", "in_forma_pauperis_termination", str),
}


def parse_docket_number(docket_number: str) -> str:
    """Parse a docket number into its components and unite into a string.

    Args:
        docket_number (str): The docket number to parse.

    Returns:
        string of hyphenated docket number in standard form.

    """
    if len(docket_number) < 6:
        raise ValueError(f"Invalid docket number: {docket_number}")
    year = docket_number[:2]
    docket_num = docket_number[2:]
    if len(docket_num) > 4 and docket_num[0] == "0":
        docket_num = docket_num[1:]
    return f"{year}-{docket_num}"
