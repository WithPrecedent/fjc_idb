"""Rules for criminal offense codes shared by appellate and criminal data."""

from __future__ import annotations


""" Criminal Offense Rules """

criminal_homicide: list[str] = [
    '0100',
    '0101',
    '0200',
    '0201',
    '0300',
    '0301',
    '0310',
    '0311',
    '7478']
criminal_murder: list[str] = ['0100', '0101', '0200', '0201', '7478']
criminal_theft: list[str] = [
    '0320',
    '1100',
    '1200',
    '1400',
    '1500',
    '2100',
    '2200',
    '2300',
    '2400',
    '3100',
    '3200',
    '3300',
    '3400',
    '3700',
    '3800',
    '4100',
    '4200',
    '4310',
    '4320',
    '4330',
    '4340',
    '4350',
    '4390',
    '5200']
criminal_tax: list[str] = ['4510', '4520', '4530', '4540', '8900']
criminal_fraud: list[str] = [
    '4600',
    '4601',
    '4700',
    '4800',
    '4900',
    '4910',
    '4920',
    '4931',
    '4932',
    '4933',
    '4940',
    '4941',
    '4950',
    '4960',
    '4970',
    '4980',
    '4991',
    '4992',
    '4993',
    '4994',
    '4995',
    '4996',
    '4997',
    '4998',
    '4999',
    '7331']
criminal_forgery_counterfeit: list[str] = ['5600', '5710', '5720', '5800']
criminal_money_laundering: list[str] = ['7477']
criminal_sex_abuse: list[str] = ['6100', '6110', '6200']
criminal_sex_offenses: list[str] = [
    '6100', 
    '6110',
    '6200', 
    '6300', 
    '7470', 
    '9810', 
    '9820']
criminal_marijuana: list[str] = ['6500', '6501', '6502', '6503', '6504', '6505']
criminal_drugs: list[str] = [
    '6500',
    '6501',
    '6502',
    '6503',
    '6504',
    '6505',
    '6600',
    '6700',
    '6701',
    '6702',
    '6703',
    '6704',
    '6705',
    '6706',
    '6800',
    '6801',
    '6802',
    '6803',
    '6804',
    '6805',
    '6806',
    '6807',
    '6808',
    '6809',
    '6905']
criminal_drug_possession: list[str] = ['6504', '6704', '6804']
criminal_escape: list[str] = ['7310', '7311', '7312', '7313']
criminal_racketeering: list[str] = [
    '7400',
    '7410',
    '7420',
    '7430',
    '7440',
    '7450',
    '7460',
    '7470',
    '7473',
    '7480',
    '7481',
    '7482',
    '7490']
criminal_perjury: list[str] = ['7700']
criminal_kidnapping: list[str] = ['7600', '7601', '7610', '7611']
criminal_firearms: list[str] = ['7800', '7820', '7830', '7831']
criminal_immigration: list[str] = ['8710', '8720', '8730', '8740', '8750']
criminal_terrorism_and_espionage: list[str] = [
    '9751', 
    '9752', 
    '9753', 
    '9754', 
    '9957']
# New columns marking the OFFENSE codes in each list.
criminal_offense_columns: dict[str, list[str]] = {
    'criminal_homicide': criminal_homicide,
    'criminal_murder': criminal_murder,
    'criminal_theft': criminal_theft,
    'criminal_tax': criminal_tax,
    'criminal_fraud': criminal_fraud,
    'criminal_forgery_counterfeit': criminal_forgery_counterfeit,
    'criminal_money_laundering': criminal_money_laundering,
    'criminal_sex_abuse': criminal_sex_abuse,
    'criminal_sex_offenses': criminal_sex_offenses,
    'criminal_marijuana': criminal_marijuana,
    'criminal_drugs': criminal_drugs,
    'criminal_drug_possession': criminal_drug_possession,
    'criminal_escape': criminal_escape,
    'criminal_racketeering': criminal_racketeering,
    'criminal_perjury': criminal_perjury,
    'criminal_kidnapping': criminal_kidnapping,
    'criminal_firearms': criminal_firearms,
    'criminal_immigration': criminal_immigration,
    'criminal_terrorism_and_espionage': criminal_terrorism_and_espionage}
