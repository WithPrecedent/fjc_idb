"""Rules for civil cases shared by appellate and civil district data."""

from __future__ import annotations


""" Civil Litigation Rules """

civil_civil_rights: list[str] = [
    '440',
    '441',
    '442',
    '443',
    '444']
civil_personal_injury: list[str] = [
    '310',
    '340',
    '350',
    '360',
    '368']
civil_product_liability: list[str] = [
    '195',
    '245',
    '315',
    '345',
    '365',
    '368',
    '385']
civil_asbestos: list[str] = ['368']
civil_habeas: list[str] = ['530', '535']
civil_habeas_death_penalty: list[str] = ['535']
civil_prisoner_rights: list[str] = ['540', '550', '555']
civil_ip: list[str] = ['820', '830', '840']
civil_social_security: list[str] = ['860', '864']
civil_medicare: list[str] = ['861']
civil_foia: list[str] = ['895']
civil_environmental: list[str] = ['893']
civil_deportation: list[str] = ['460']

# New columns marking the NOS codes in each list.
civil_nature_of_suit_columns: dict[str, list[str]] = {
    'civil_civil_rights': civil_civil_rights,
    'civil_personal_injury': civil_personal_injury,
    'civil_product_liability': civil_product_liability,
    'civil_asbestos': civil_asbestos,
    'civil_habeas': civil_habeas,
    'civil_habeas_death_penalty': civil_habeas_death_penalty,
    'civil_prisoner_rights': civil_prisoner_rights,
    'civil_ip': civil_ip,
    'civil_social_security': civil_social_security,
    'civil_medicare': civil_medicare,
    'civil_foia': civil_foia,
    'civil_environmental': civil_environmental,
    'civil_deportation': civil_deportation}

""" Jurisdiction Rules """

prisoner_codes: list[str] = ['510', '530', '535', '540', '550']
prisoner_jurisdiction: dict[str, str] = {
    '2': 'Federal Prisoner',
    '3': 'State Prisoner',
    '5': 'Local Prisoner'}
civil_jurisdiction: dict[str, str] = {
    '1': 'U.S. Government Plaintiff',
    '2': 'U.S. Government Defendant',
    '3': 'Federal Question',
    '4': 'Diversity of Citizenship',
    '5': 'Local Question (US Territory)'}

""" Civil District Rules """

arbitration: dict[str, str] = {
    'M': 'Mandatory',
    'V': 'Voluntary',
    'E': 'Exempt',
    'Y': 'Yes, type unknown'}
civil_dispositions: dict[str, str] = {
    '0': 'Transferred to another district',
    '1': 'Remanded to state court',
    '2': 'Dismissed for want of prosecution',
    '3': 'Dismissed for lack of jurisdiction',
    '4': 'Judgment on default',
    '5': 'Judgment on consent',
    '6': 'Judgment on motion before trial',
    '7': 'Judgment on jury verdict',
    '8': 'Judgment on directed verdict',
    '9': 'Judgment on court trial',
    '10': 'Multidistrict litigation transfer',
    '11': 'Remanded to U.S. agency',
    '12': 'Dismissed voluntarily',
    '13': 'Dismissed as settled',
    '14': 'Dismissed, other',
    '15': 'Judgment on award of arbitrator',
    '16': 'Judgment staying case pending bankruptcy',
    '17': 'Judgment, other',
    '18': 'Statistical closing',
    '19': 'Appeal affirmed (magistrate judge)',
    '20': 'Appeal denied (magistrate judge)'}
# IFP uses -8 for cases that are not in forma pauperis, not for missing data.
civil_in_forma_pauperis: dict[str, str] = {
    'FP': '1',
    '-8': '0'}
class_action_terminations: dict[str, str] = {
    '2': 'Denied',
    '3': 'Granted'}
judgments: dict[str, str] = {
    '1': 'Plaintiff',
    '2': 'Defendant',
    '3': 'Both',
    '4': 'Unknown'}
jury_demands: dict[str, str] = {
    'B': 'Both',
    'D': 'Defendant',
    'P': 'Plaintiff',
    'N': 'Neither'}
natures_of_judgment: dict[str, str] = {
    '0': 'No monetary award',
    '1': 'Monetary award only',
    '2': 'Monetary award and other',
    '3': 'Injunction',
    '4': 'Forfeiture, foreclosure, or condemnation',
    '5': 'Costs only',
    '6': 'Costs and attorney fees'}
origins: dict[str, str] = {
    '1': 'Original proceeding',
    '2': 'Removed from state court',
    '3': 'Remanded from court of appeals',
    '4': 'Reinstated or reopened',
    '5': 'Transferred from another district',
    '6': 'Multidistrict litigation transfer',
    '7': 'Appeal from magistrate judge',
    '8': 'Second reopen',
    '9': 'Third reopen',
    '10': 'Fourth reopen',
    '11': 'Fifth reopen',
    '12': 'Sixth reopen',
    '13': 'Multidistrict litigation originating in the district'}
procedural_progress: dict[str, str] = {
    '1': 'Before issue joined, no court action',
    '2': 'Before issue joined, order entered',
    '11': 'Before issue joined, hearing held',
    '12': 'Before issue joined, order decided',
    '3': 'After issue joined, no court action',
    '4': 'After issue joined, judgment on motion',
    '5': 'After issue joined, pretrial conference held',
    '6': 'After issue joined, during court trial',
    '7': 'After issue joined, during jury trial',
    '8': 'After issue joined, after court trial',
    '9': 'After issue joined, after jury trial',
    '10': 'After issue joined, other',
    '13': 'After issue joined, request for trial de novo after arbitration'}
