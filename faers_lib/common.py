"""Common import for files in FAERS package.
"""

"""Structure of the FAERS text files.
"""

zip_name_template = 'https://fis.fda.gov/content/Exports/faers_ascii_%dQ%d.zip'
main_data_path = './data'

data_dir_template = 'faers_ascii_%dQ%d/ascii'
delete_file_template = 'faers_ascii_%dQ%d/deleted/ADR%dQ%dDeletedCases.txt'

"""Dictionary keeping the file structure and its data type
"""
file_struct = {'demographic':
               {'name': 'DEMO%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int, 'caseversion': int,
                          'i_f_code': str, 'event_dt': str, 'mfr_dt': str,
                          'init_fda_dt': str, 'fda_dt': str, 'rept_cod': str,
                          'auth_num': str, 'mfr_num': str, 'mfr_sndr': str,
                          'lit_ref': str, 'age': float, 'age_cod': str,
                          'age_grp': str, 'sex': str, 'e_sub': str,
                          'wt': float, 'wt_cod': str,
                          'rept_dt': str, 'to_mfr': str, 'occp_cod': str,
                          'reporter_country': str, 'occr_country': str},
                'date_cols': ['event_dt', 'mfr_dt', 'init_fda_dt', 'fda_dt',
                              'rept_dt'],
                'idx_key': ['primaryid']},

               'drug':
               {'name': 'DRUG%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int,
                          'drug_seq': int, 'role_cod': str,
                          'drugname': str,
                          'prod_ai': str,
                          'val_vbm': int, 'route': str, 'dose_vbm': str,
                          'cum_dose_chr': str, 'cum_dose_unit': str,
                          'dechal': str, 'rechal': str, 'lot_num': str,
                          'exp_dt': str, 'nda_num': float,
                          'dose_amt': float, 'dose_unit': str,
                          'dose_form': str, 'dose_freq': str},
                'date_cols': ['exp_dt'],
                'idx_key': ['primaryid', 'drug_seq']},

               'indication':
               {'name': 'INDI%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int,
                          'indi_drug_seq': int,
                          'indi_pt': str},
                'date_cols': [],
                'idx_key': ['primaryid', 'indi_drug_seq']},

               'outcome':
               {'name': 'OUTC%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int, 'outc_cod': str},
                'date_cols': [],
                'idx_key': ['primaryid']},

               'reaction':
               {'name': 'REAC%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int, 'pt': str,
                          'drug_rec_act': str},
                'date_cols': [],
                'idx_key': ['primaryid', 'pt']},

               'report_sources':
               {'name': 'RPSR%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int, 'rpsr_cod': str},
                'date_cols': [],
                'idx_key': ['primaryid']},

               'therapy':
               {'name': 'THER%dQ%d.txt',
                'dtype': {'primaryid': int, 'caseid': int,
                          'dsg_drug_seq': int, 'start_dt': str,
                          'end_dt': str, 'dur': float, 'dur_cod': str},
                'date_cols': ['start_dt', 'end_dt'],
                'idx_key': ['primaryid', 'dsg_drug_seq']}}
