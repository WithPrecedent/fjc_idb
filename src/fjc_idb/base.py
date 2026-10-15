"""Column specifications for each type of FJC IDB file.

Each case type has a dictionary of `Column` instances, keyed by the name each
column has after parsing. The specifications say how to clean, decode, type,
and rename every column in the original files.

"""

from __future__ import annotations

import dataclasses
from typing import Any

from . import options, rules


@dataclasses.dataclass
class Column:
    """A column in an FJC IDB file and how to parse it.

    Attributes:
        import_name: The column name in the FJC IDB files.
        name: The column name used when columns are renamed.
        data_type: The type the column is converted to.
        missing_value: The code (or list of codes) that marks missing data in
            the FJC IDB files, or None if no code marks missing data.
        missing_replacement: The value written in place of missing data when
            the data is exported.
        decoder: Labels that replace the codes in the column, keyed by code.
            Codes without a label are kept as they are.

    Examples:
        A text column whose codes are replaced with circuit names, and a date
        column whose missing dates are written as 'NA':

            Column('CIRCUIT', 'circuit', str, decoder = rules.circuits)
            Column(
                'DKTDATE', 'docket_date', 'date',
                missing_value = options._MISSING_DATE,
                missing_replacement = 'NA')

    """

    import_name: str
    name: str
    data_type: str | type
    missing_value: Any = '-8'
    missing_replacement: Any = ''
    decoder: dict[str, Any] | None = None


appellate_columns: dict[str, Column] = {
    'circuit': Column('CIRCUIT', 'circuit', str, decoder = rules.circuits),
    'docket_num_idb': Column('DOCKET', 'docket_num_idb', str),
    'reopened_or_remanded': Column(
        'REOPEN', 'reopened_or_remanded', str,
        decoder = rules.reopened_or_remanded),
    'docket_date': Column(
        'DKTDATE', 'docket_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'us_appellant': Column('USAPT', 'us_appellant', 'int'),
    'appellant': Column('APPELLAN', 'appellant', str),
    'us_appellee': Column('USAPE', 'us_appellee', 'int'),
    'appellee': Column('APPELLEE', 'appellee', str),
    'appeal_type': Column('APPTYPE', 'appeal_type', str),
    'writ': Column('ORGPROC', 'writ', 'int'),
    'agency': Column('AGENCY', 'agency', str, decoder = rules.agencies),
    'jurisdiction': Column('JURIS', 'jurisdiction', str),
    'nature_of_suit': Column('NOS', 'nature_of_suit', int),
    'criminal_offense': Column('OFFENSE', 'criminal_offense', int),
    'circuit_of_origin': Column(
        'DCIRC', 'circuit_of_origin', str, decoder = rules.circuits),
    'district_of_origin': Column(
        'DDIST', 'district_of_origin', str, decoder = rules.districts),
    'district_courthouse': Column(
        'DOFFICE', 'district_courthouse', str, decoder = rules.offices),
    'district_docket': Column('DDOCKET', 'district_docket', str),
    'criminal_defendant_number': Column(
        'DDEFNUM', 'criminal_defendant_number', str),
    'criminal_capital_case': Column(
        'FEDCAP', 'criminal_capital_case', int, missing_value = None,
        decoder = rules.capital_case),
    'district_docket_date': Column(
        'DDKTDATE', 'district_docket_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'appeal_date': Column(
        'APPDATE', 'appeal_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'last_date': Column(
        'TRANSDATE', 'last_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    # 'R' is not in the codebook and only appears on a few pending cases.
    'new_filing': Column(
        'TRANSCODE', 'new_filing', int, missing_value = 'R',
        decoder = rules.new_filing),
    'district_judge': Column('DJUDGE', 'district_judge', str),
    'in_forma_pauperis': Column(
        'FILEFEE', 'in_forma_pauperis', int,
        decoder = rules.in_forma_pauperis),
    'when_terminated': Column('DISP', 'when_terminated', str),
    'disposition': Column('OUTCOME', 'disposition', str),
    'procedural_termination': Column(
        'PROCTERM', 'procedural_termination', int),
    'non_merits_disposition': Column('METHOD', 'non_merits_disposition', str),
    'published_status': Column('PUBSTAT', 'published_status', int),
    'original_proceeding_termination': Column(
        'OPDISP', 'original_proceeding_termination', str),
    'joined_appeal': Column('JOINAPP', 'joined_appeal', str),
    'joined_docket': Column('CONSDKT', 'joined_docket', str),
    'briefing_notice_date': Column(
        'CRECDATE', 'briefing_notice_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'brief_filed_date': Column(
        'BRFILED', 'brief_filed_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'submitted_date': Column(
        'SUBDATE', 'submitted_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'hearing_date': Column(
        'HEARDATE', 'hearing_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'judgment_date': Column(
        'JUDGDATE', 'judgment_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'opinion_types': Column('OPINION', 'opinion_types', str),
    'judge_1': Column('JDGCODE1', 'judge_1', str),
    'judge_1_opinion_type': Column('JDG1INV', 'judge_1_opinion_type', str),
    'judge_2': Column('JDGCODE2', 'judge_2', str),
    'judge_2_opinion_type': Column('JDG2INV', 'judge_2_opinion_type', str),
    'judge_3': Column('JDGCODE3', 'judge_3', str),
    'judge_3_opinion_type': Column('JDG3INV', 'judge_3_opinion_type', str),
    'data_file_year': Column('TAPEYEAR', 'data_file_year', int),
    'pro_se_at_filing': Column('PROSEFLE', 'pro_se_at_filing', int),
    'pro_se_at_termination': Column('PROSETRM', 'pro_se_at_termination', str),
    'pending': Column('STATUSCD', 'pending', int, decoder = rules.pending),
    'enbanc': Column(
        'ENBANC', 'enbanc', str, missing_value = None, decoder = rules.enbanc),
    'appeal_type_termination': Column(
        'TRMTYPE', 'appeal_type_termination', str),
    'writ_termination': Column(
        'TORPROCSUB', 'writ_termination', str, decoder = rules.writs),
    'in_forma_pauperis_termination': Column(
        'TRMFEE', 'in_forma_pauperis_termination', str, missing_value = None,
        decoder = rules.in_forma_pauperis)}

civil_columns: dict[str, Column] = {
    'circuit': Column('CIRCUIT', 'circuit', str, decoder = rules.circuits),
    'district': Column('DISTRICT', 'district', str, decoder = rules.districts),
    'district_courthouse': Column(
        'OFFICE', 'district_courthouse', str, decoder = rules.offices),
    'docket': Column('DOCKET', 'docket', str),
    'origin': Column('ORIGIN', 'origin', str, decoder = rules.origins),
    'filing_date': Column(
        'FILEDATE', 'filing_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'filing_date_used_by_ao': Column(
        'FDATEUSE', 'filing_date_used_by_ao', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'jurisdiction': Column('JURIS', 'jurisdiction', str),
    'nature_of_suit': Column('NOS', 'nature_of_suit', int),
    'us_code_title': Column('TITL', 'us_code_title', str),
    'us_code_section': Column('SECTION', 'us_code_section', str),
    'us_code_subsection': Column('SUBSECT', 'us_code_subsection', str),
    'diversity_residence': Column('RESIDENC', 'diversity_residence', str),
    'jury_demand': Column(
        'JURY', 'jury_demand', str, decoder = rules.jury_demands),
    'class_action': Column('CLASSACT', 'class_action', int),
    'amount_demanded': Column('DEMANDED', 'amount_demanded', int),
    'filing_judge': Column('FILEJUDG', 'filing_judge', str),
    'filing_magistrate_judge': Column(
        'FILEMAG', 'filing_magistrate_judge', str),
    'county': Column('COUNTY', 'county', str),
    'arbitration_at_filing': Column(
        'ARBIT', 'arbitration_at_filing', str, decoder = rules.arbitration),
    'mdl_docket': Column('MDLDOCK', 'mdl_docket', str),
    'plaintiff': Column('PLT', 'plaintiff', str),
    'defendant': Column('DEF', 'defendant', str),
    'transfer_date': Column(
        'TRANSDAT', 'transfer_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'transfer_office': Column('TRANSOFF', 'transfer_office', str),
    'transfer_docket': Column('TRANSDOC', 'transfer_docket', str),
    'transfer_origin': Column(
        'TRANSORG', 'transfer_origin', str, decoder = rules.origins),
    'termination_date': Column(
        'TERMDATE', 'termination_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'termination_date_used_by_ao': Column(
        'TDATEUSE', 'termination_date_used_by_ao', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'class_action_termination': Column(
        'TRCLACT', 'class_action_termination', str,
        decoder = rules.class_action_terminations),
    'termination_judge': Column('TERMJUDG', 'termination_judge', str),
    'termination_magistrate_judge': Column(
        'TERMMAG', 'termination_magistrate_judge', str),
    'procedural_progress': Column(
        'PROCPROG', 'procedural_progress', str,
        decoder = rules.procedural_progress),
    'disposition': Column(
        'DISP', 'disposition', str, decoder = rules.civil_dispositions),
    'nature_of_judgment': Column(
        'NOJ', 'nature_of_judgment', str, decoder = rules.natures_of_judgment),
    'amount_received': Column('AMTREC', 'amount_received', int),
    'judgment_for': Column(
        'JUDGMENT', 'judgment_for', str, missing_value = ['-8', '0'],
        decoder = rules.judgments),
    'issue_joined_date': Column(
        'DJOINED', 'issue_joined_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'pretrial_conference_date': Column(
        'PRETRIAL', 'pretrial_conference_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'trial_began_date': Column(
        'TRIBEGAN', 'trial_began_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'trial_ended_date': Column(
        'TRIALEND', 'trial_ended_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'arbitration_at_termination': Column(
        'TRMARB', 'arbitration_at_termination', str,
        decoder = rules.arbitration),
    'pro_se': Column('PROSE', 'pro_se', int),
    'in_forma_pauperis': Column(
        'IFP', 'in_forma_pauperis', int, missing_value = None,
        decoder = rules.civil_in_forma_pauperis),
    'pending': Column('STATUSCD', 'pending', int, decoder = rules.pending),
    'data_file_year': Column('TAPEYEAR', 'data_file_year', int)}

def _offense_columns(stage: str, number: int) -> dict[str, Column]:
    """Returns the columns describing one of the five offenses of a defendant.

    Args:
        stage: 'filing' or 'termination'.
        number: The rank of the offense by severity, from 1 to 5.

    Returns:
        dict[str, Column]: The offense columns, keyed by column name.

    """
    prefix = stage[0].upper()
    specs = [
        Column(
            f'{prefix}TITLE{number}', f'{stage}_title_section_{number}', str),
        Column(
            f'{prefix}OFFLVL{number}', f'{stage}_offense_level_{number}', str,
            decoder = rules.offense_levels),
        Column(f'{prefix}OFFCD{number}', f'{stage}_offense_ao_{number}', str),
        Column(f'D2{prefix}OFFCD{number}', f'{stage}_offense_d2_{number}', str),
        Column(f'{prefix}SEV{number}', f'{stage}_severity_{number}', str)]
    return {spec.name: spec for spec in specs}

def _sentence_columns(number: int) -> dict[str, Column]:
    """Returns the columns describing the outcome of one offense at termination.

    Args:
        number: The rank of the offense by severity, from 1 to 5.

    Returns:
        dict[str, Column]: The outcome columns, keyed by column name.

    """
    specs = [
        Column(
            f'DISP{number}', f'disposition_{number}', str,
            decoder = rules.criminal_dispositions),
        Column(f'PRISTIM{number}', f'prison_months_{number}', int),
        Column(f'PRISCD{number}', f'prison_code_{number}', str),
        Column(f'PROBMON{number}', f'probation_months_{number}', int),
        Column(f'PROBCD{number}', f'probation_code_{number}', str),
        Column(
            f'SUPVREL{number}', f'supervised_release_months_{number}', int),
        Column(f'FINEAMT{number}', f'fine_{number}', int)]
    return {spec.name: spec for spec in specs}

criminal_columns: dict[str, Column] = {
    'fiscal_year': Column('FISCALYR', 'fiscal_year', int),
    'circuit': Column('CIRCUIT', 'circuit', str, decoder = rules.circuits),
    'district': Column('DISTRICT', 'district', str, decoder = rules.districts),
    'district_courthouse': Column(
        'OFFICE', 'district_courthouse', str, decoder = rules.offices),
    'docket': Column('DOCKET', 'docket', str),
    'defendant_number': Column('DEFNO', 'defendant_number', int),
    'court_defendant_number': Column('CTDEF', 'court_defendant_number', int),
    'defendant_name': Column('NAME', 'defendant_name', str),
    'reopen_sequence': Column('REOPSEQ', 'reopen_sequence', int),
    'case_type': Column(
        'TYPEREG', 'case_type', str, decoder = rules.case_types),
    'case_type_transfer': Column(
        'TYPETRN', 'case_type_transfer', str, decoder = rules.case_types),
    'case_type_magistrate': Column(
        'TYPEMAG', 'case_type_magistrate', str, decoder = rules.case_types),
    'defendant_key': Column('DEFLGKY', 'defendant_key', str),
    'case_key': Column('CASLGKY', 'case_key', str),
    'magistrate_docket': Column('MAGDOCK', 'magistrate_docket', str),
    'magistrate_defendant_number': Column(
        'MAGDEF', 'magistrate_defendant_number', int),
    'pending': Column(
        'STATUSCD', 'pending', int, decoder = rules.criminal_pending),
    'fugitive_status': Column(
        'FUGSTAT', 'fugitive_status', str, decoder = rules.fugitive_statuses),
    'fugitive_start_date': Column(
        'FGSTRTDATE', 'fugitive_start_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'fugitive_end_date': Column(
        'FGENDDATE', 'fugitive_end_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'filing_date': Column(
        'FILEDATE', 'filing_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'proceeding_date': Column(
        'PROCDATE', 'proceeding_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'proceeding': Column(
        'PROCCD', 'proceeding', str, decoder = rules.proceedings),
    'first_appearance_date': Column(
        'APPDATE', 'first_appearance_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'first_appearance': Column(
        'APPCD', 'first_appearance', str, decoder = rules.first_appearances),
    'filing_judge': Column('FJUDGE', 'filing_judge', str),
    'filing_counsel': Column(
        'FCOUNSEL', 'filing_counsel', str, decoder = rules.counsel),
    **{
        name: spec
        for number in range(1, 6)
        for name, spec in _offense_columns('filing', number).items()},
    'county': Column('COUNTY', 'county', str),
    'transfer_district': Column('TRANDIST', 'transfer_district', str),
    'transfer_office': Column('TRANOFF', 'transfer_office', str),
    'transfer_docket': Column('TRANDOCK', 'transfer_docket', str),
    'transfer_defendant_number': Column(
        'TRANDEF', 'transfer_defendant_number', str),
    'last_update_date': Column(
        'UPDATE', 'last_update_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'disposition_date': Column(
        'DISPDATE', 'disposition_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'sentencing_date': Column(
        'SENTDATE', 'sentencing_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'termination_date': Column(
        'TERMDATE', 'termination_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'days_to_proceeding': Column('INT1', 'days_to_proceeding', int),
    'days_proceeding_to_disposition': Column(
        'INT2', 'days_proceeding_to_disposition', int),
    'days_disposition_to_sentencing': Column(
        'INT3', 'days_disposition_to_sentencing', int),
    'termination_courthouse': Column(
        'TERMOFF', 'termination_courthouse', str, decoder = rules.offices),
    'termination_judge': Column('TJUDGE', 'termination_judge', str),
    'termination_counsel': Column(
        'TCOUNSEL', 'termination_counsel', str, decoder = rules.counsel),
    **{
        name: spec
        for number in range(1, 6)
        for name, spec in {
            **_offense_columns('termination', number),
            **_sentence_columns(number)}.items()},
    'prison_total_months': Column('PRISTOT', 'prison_total_months', int),
    'probation_total_months': Column(
        'PROBTOT', 'probation_total_months', int),
    'fine_total': Column('FINETOT', 'fine_total', int),
    'count_filed_including_transfers': Column(
        'CTFILTRN', 'count_filed_including_transfers', int),
    'count_filed': Column('CTFIL', 'count_filed', int),
    'count_filed_without_reopens': Column(
        'CTFILWOR', 'count_filed_without_reopens', int),
    'count_filed_reopens': Column('CTFILR', 'count_filed_reopens', int),
    'count_terminated_including_transfers': Column(
        'CTTRTRN', 'count_terminated_including_transfers', int),
    'count_terminated': Column('CTTR', 'count_terminated', int),
    'count_terminated_without_reopens': Column(
        'CTTRWOR', 'count_terminated_without_reopens', int),
    'count_terminated_reopens': Column(
        'CTTRR', 'count_terminated_reopens', int),
    'count_pending': Column('CTPN', 'count_pending', int),
    'count_pending_without_fugitives': Column(
        'CTPNWOF', 'count_pending_without_fugitives', int),
    'source': Column('SOURCE', 'source', str),
    'version': Column('VER', 'version', int),
    'load_date': Column(
        'LOADDATE', 'load_date', 'date',
        missing_value = options._MISSING_DATE, missing_replacement = 'NA'),
    'data_file_year': Column('TAPEYEAR', 'data_file_year', int)}
