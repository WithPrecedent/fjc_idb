"""Rules for FJC IDB criminal district data."""

from __future__ import annotations

""" Criminal District Rules """

case_types: dict[str, str] = {
    'CR': 'Criminal',
    'MJ': 'Magistrate'}
counsel: dict[str, str] = {
    '0': 'Not reported',
    '1': 'Criminal Justice Act appointment',
    '2': 'Private counsel',
    '3': 'Pro se',
    '4': 'Self',
    '5': 'None or other',
    '6': 'Public or community defender',
    '7': 'Pro bono'}
criminal_dispositions: dict[str, str] = {
    '0': 'Rule 20(a)/21 transfer',
    '1': 'Dismissed',
    '2': 'Acquitted by court',
    '3': 'Acquitted by jury',
    '4': 'Convicted on guilty plea',
    '5': 'Convicted on nolo contendere plea',
    '8': 'Convicted by court after trial',
    '9': 'Convicted by jury after trial',
    '10': 'NARA Titles I and III',
    '11': 'Nolle prosequi',
    '12': 'Pretrial diversion',
    '13': 'Mistrial',
    '14': 'Statistically closed',
    '15': 'Dismissed without prejudice',
    '16': 'Not guilty by reason of insanity (court trial)',
    '17': 'Guilty but insane (court trial)',
    '18': 'Not guilty by reason of insanity (jury trial)',
    '19': 'Guilty but insane (jury trial)',
    '20': 'Dismissal superseded',
    '21': 'Reassigned from judge to magistrate judge'}
# STATUSCD uses E for pending and J for terminated defendants.
criminal_pending: dict[str, str] = {
    'E': '1',
    'J': '0'}
first_appearances: dict[str, str] = {
    'A': 'Arrest',
    'B': 'Appeared on summons',
    'C': 'In U.S. custody',
    'D': 'Appeared on complaint',
    '1': 'First appearance after indictment or information',
    '2': 'Papers received after Rule 20(a)/21 transfer',
    '3': 'Guilty plea withdrawn'}
fugitive_statuses: dict[str, str] = {
    'N': 'Not a fugitive',
    'Y': 'Fugitive one year or less',
    'Z': 'Fugitive more than one year'}
offense_levels: dict[str, str] = {
    '1': 'Petty offense',
    '3': 'Class A misdemeanor',
    '4': 'Felony'}
proceedings: dict[str, str] = {
    '1': 'Indictment filed',
    '2': 'Misdemeanor information or criminal contempt notice',
    '3': 'Felony information with waiver of indictment',
    '4': 'Remand from appellate court for resentencing',
    '5': 'Removal from state court',
    '6': 'Case reopening',
    '7': 'Appeal from magistrate judge',
    '8': 'Adult Rule 20(a)/21 transfer',
    '9': 'Juvenile proceeding',
    '10': 'Consent to trial before a magistrate judge on complaint',
    '11': 'Remand from appellate court for retrial',
    '12': 'Retrial after mistrial',
    '13': 'Juvenile to be tried as an adult',
    '14': 'Violation notice',
    '16': 'Superseding indictment',
    '17': 'Superseding information',
    '18': 'Superseding felony information with waiver of indictment',
    '19': 'Indictment unsealed',
    '20': 'Indictment',
    '21': 'Felony waiver not signed',
    '22': 'Sealed misdemeanor information',
    '23': 'Misdemeanor information unsealed',
    '24': 'Sealed felony information with waiver of indictment',
    '25': 'Felony information unsealed',
    '26': 'Sealed indictment',
    '27': 'Review of crack cocaine sentences'}
