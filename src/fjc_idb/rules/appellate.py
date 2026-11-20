"""Rules for FJC IDB appellate data."""

from __future__ import annotations

""" Opinion Rules """

published_codes: list[int] = [2, 4, 6]
unpublished_codes: list[int] = [1, 3, 5, 7]

""" Appellate Rules """

# APPTYPE codes of criminal appeals, including post-conviction (21) and
# miscellaneous criminal (22) appeals.
criminal_apptypes: list[str] = [
    '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']
sentencing_apptypes: list[int] = [13, 14, 15, 16, 17]
civil_apptypes: list[int] = [1, 2, 3, 5, 10, 11, 12]
bankruptcy_apptypes: list[int] = [10, 11, 12]

appeal_types_to_columns: dict[str, str] = {
    '1': 'civil_administrative_review',
    '2': 'civil_administrative_enforcement',
    '3': 'civil_us_party',
    '4': 'civil_non_us_party',
    '6': 'civil_original_proceeding',
    '10': 'bankruptcy_from_bankruptcy_court',
    '11': 'bankruptcy_from_bankruptcy_appellate_panel',
    '12': 'bankruptcy_from_district_court',
    '13': 'criminal_guidelines_general',
    '14': 'criminal_pre_guidelines',
    '15': 'criminal_guidelines_sentence',
    '16': 'criminal_guidelines_conviction',
    '18': 'criminal_other',
    '19': 'criminal_direct_appeal',
    '20': 'criminal_interlocutory',
    '21': 'criminal_post_conviction',
    '22': 'criminal_miscellaneous',
    '-8': 'appeal_type_missing'}
# USAPT codes marked in the columns for which side brought a criminal appeal.
criminal_appeal_sides: dict[str, str] = {
    'criminal_defendant_appeal': '0',
    'criminal_government_appeal': '1'}
# OUTCOME codes marked in the columns for the outcome of an appeal decided on
# the merits.
disposition_columns: dict[str, list[str]] = {
    'affirmed': ['1'],
    'reversed': ['2'],
    'affirmed_in_part': ['3'],
    'reversed_in_whole_or_part': ['2', '3'],
    'dismissed_on_merits': ['5'],
    'remanded_only': ['6']}
# PROSEFLE and PROSETRM codes for an appellant, an appellee, or both pro se.
pro_se_codes: list[str] = ['1', '2', '3']
# PROSEFLE and PROSETRM codes for an appellant pro se, alone or with the
# appellee.
pro_se_appellant_codes: list[str] = ['1', '3']
# JDG1INV, JDG2INV, and JDG3INV codes for judges who wrote separate opinions.
concurrence_codes: list[str] = ['B', 'D', 'E', 'G']
dissent_codes: list[str] = ['C', 'F', 'G']
# Appeal types that are marked in the columns of more than one other type.
appeal_types_in_other_columns: dict[str, list[str]] = {
    '17': ['15', '16']}
capital_case: dict[str, str] = {
    'Y': '1',
    '-8': '0'}
enbanc: dict[str, str] = {
    'N': '0',
    'Y': '1',
    '-8': 'Missing/Pending'}
in_forma_pauperis: dict[str, str] = {
    'N': '0',
    'FP': '1',
    '-8': 'Missing/Pending'}
new_filing: dict[str, str] = {
    'E': '1',
    'J': '0'}
pending: dict[str, str] = {
    'S': '1',
    'L': '0'}
reopened_or_remanded: dict[str, str] = {
    '1': 'Reopened',
    '2': 'Remanded to the court of appeals',
    '3': 'Reopened or remanded a second time',
    '4': 'Reinstated after dismissal for procedural default',
    '5': 'Reopened or remanded a third time',
    '6': 'Reopened a fourth time',
    '7': 'Reopened a fifth time',
    'M': 'Remanded from the Supreme Court',
    'S': 'Remanded from the Supreme Court a second time'}
writs: dict[str, str] = {
    '1': 'Prohibition',
    '2': 'Mandamus (fee paid)',
    '3': 'Mandamus (fee not paid)',
    '5': 'Other writ',
    '6': 'Second or successive habeas'}

""" Agency Rules """

agencies: dict[str, str] = {
    'AGRI': 'Department of Agriculture',
    'AID': 'Agency for International Development',
    'ARMY': 'Army',
    'BATF': 'Bureau of Alcohol, Tobacco, Firearms and Explosives',
    'BCA': 'Board of Contract Appeals',
    'BOP': 'Bureau of Prisons',
    'BPA': 'Bonneville Power Administration',
    'BRB': 'Benefits Review Board',
    'CAB': 'Civil Aeronautics Board',
    'CAHO': 'Office of the Chief Administrative Hearing Officer',
    'CFPB': 'Consumer Financial Protection Bureau',
    'CFTR': 'Commodity Future Trading Commission',
    'CMCR': 'Court of Military Commission Review',
    'COAL': 'Federal Coal Commission',
    'COMM': 'Department of Commerce',
    'CBO': 'Congressional Budget Office',
    'CPSC': 'Consumer Products Safety Commission',
    'CRT': 'Copyright Royalty Tribunal',
    'CSC': 'Civil Service Commission',
    'CSRT': 'Combatant Status Review Tribunal',
    'DEA': 'Drug Enforcement Agency',
    'DHS': 'Department of Homeland Security',
    'DNFS': 'Defense Nuclear Facilities Safety Board',
    'DOD': 'Department of Defense',
    'DOE': 'Department of Energy',
    'DOI': 'Department of the Interior',
    'DOJ': 'Department of Justice',
    'DOST': 'Department of Science and Technology',
    'DVA': 'Department of Veterans Affairs',
    'EDUC': 'Department of Education',
    'EEOC': 'Equal Employment Opportunity Commission',
    'EPA': 'Environmental Protection Agency',
    'ERA': 'Economic Regulatory Administration',
    'FAA': 'Federal Aviation Administration',
    'FCC': 'Federal Communication Commission',
    'FCMS': 'Federal Coal Mine Safety Board',
    'FDA': 'Food and Drug Administration',
    'FDIC': 'Federal Deposit Insurance Corp.',
    'FEA': 'Federal Energy Agency',
    'FEC': 'Federal Election Commission',
    'FHLB': 'Federal Home Loan Bank Board',
    'FLRA': 'Federal Labor Relations Authority',
    'FLRB': 'Federal Labor Relations Board',
    'FMBD': 'Federal Maritime Board',
    'FMC': 'Federal Maritime Commission',
    'FMCS': 'Federal Motor Carrier Safety Administration',
    'FRA': 'Federal Railroad Administration',
    'FRS': 'Federal Reserve System',
    'GAO': 'Government Accounting Office',
    'GSA': 'General Services Administration',
    'HCFA': 'Health Care Financing Administration',
    'HEW': 'Department of Health, Education, and Welfare',
    'HHS': 'Department of Health and Human Services',
    'HUD': 'Department of Housing and Urban Development',
    'IBLM': 'Bureau of Land Management',
    'ITC': 'International Trade Commission',
    'LABR': 'Department of Labor (Except OSHA)',
    'LOC': 'Library of Congress',
    'MARA': 'Maritime Administration',
    'MSHA': 'Federal Mine Safety and Health Administration',
    'MSHR': 'Federal Mine Safety and Health Review',
    'MSPB': 'Merit Systems Protection Board',
    'NASA': 'National Aeronautics and Space Administration',
    'NAVY': 'Navy',
    'NCUA': 'National Credit Union Association',
    'NHTS': 'National Highway Traffic Safety Administration',
    'NPCC': 'Northwest Power and Conservation Council',
    'NRC': 'Nuclear Regulatory Commission',
    'NSF': 'National Science Foundation',
    'NTSB': 'National Transportation Safety Board',
    'OCBD': 'Office of Compliance',
    'OCC': 'Office of the Comptroller of the Currency',
    'OCWR': 'Office of Congressional Workplace Rights',
    'OFI': 'Office of the Federal Inspector',
    'OMB': 'Office of Management and Budget',
    'OPM': 'Office of Personnel Management',
    'OSFE': 'Office of Senate Fair Employment Practices',
    'OSHA': 'Occupational Safety and Health Administration',
    'OSHC': 'Occupational Safety and Health Review Commission',
    'OTS': 'Office of Thrift Supervision',
    'OWCP': 'Office of Workers Compensation',
    'PATO': 'Patent Office',
    'PRC': 'Postal Rate Commission',
    'RRAB': 'Railroad Adjustment Board',
    'RRRB': 'Railroad Retirement Board',
    # Not sure what this is, could be Regional Tribal Consultation Official.
    'RTCO': 'RTCO',
    'SBA': 'Small Business Administration',
    'SEC': 'Securities and Exchange Commission',
    'SSA': 'Social Security Administration',
    'STAT': 'Department of State',
    'STB': 'Surface Transportation Board',
    'TRAN': 'Department of Transportation',
    'TREA': 'Department of the Treasury (Except IRS)',
    'TSA': 'Transportation Security Administration',
    'TTB': 'Alcohol and Tobacco Tax and Trade Bureau',
    'USPS': 'U.S. Postal Service',
    'VET': 'Veterans Administration',
    'WMAT': 'Washington Metropolitan Area Transit',
    '0': 'Interstate Commerce Commission',
    '1': 'National Labor Relations Board',
    '3': 'Tax Court/Internal Revenue Service',
    '4': 'Federal Trade Commission',
    '6': 'Immigration and Naturalization Service',
    '7': 'Environmental Protection Agency',
    '8': 'Federal Energy Regulatory Commission',
    '-8': 'Missing',
    '-9': 'None'}
independent_agencies: list[str] = [
    'Commodity Future Trading Commission',
    'Consumer Financial Protection Bureau',
    'Consumer Products Safety Commission',
    'Equal Employment Opportunity Commission',
    'Environmental Protection Agency',
    'Federal Communication Commission',
    'Federal Deposit Insurance Corp.',
    'Federal Election Commission',
    'Federal Energy Regulatory Commission',
    'Federal Maritime Commission',
    'Federal Reserve System',
    'Federal Trade Commission',
    'General Services Administration',
    'International Trade Commission',
    'Interstate Commerce Commission',
    'National Aeronautics and Space Administration',
    'National Credit Union Association',
    'National Labor Relations Board',
    'National Science Foundation',
    'National Transportation Safety Board',
    'Nuclear Regulatory Commission',
    'Office of Personnel Management',
    'Postal Rate Commission',
    'Securities and Exchange Commission',
    'Small Business Administration',
    'Social Security Administration',
    'Surface Transportation Board',
    'U.S. Postal Service']
legislative_agencies: list[str] = [
    'Congressional Budget Office',
    'Government Accountability Office',
    'Library of Congress',
    'Office of Senate Fair Employment Practices',
    'Office of Congressional Workplace Rights']
