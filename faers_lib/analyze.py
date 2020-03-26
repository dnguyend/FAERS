"""Module to facilitate the FDA Adverse event data.
Assume that data is unpacked in folder main_dir

"""


import os
import numpy as np
import pandas as pd
from .common import file_struct, data_dir_template
from .common import delete_file_template
from .common import main_data_path as main_dir
from IPython.core.display import display

display_mode = None


def display_frame(tbl: pd.DataFrame):
    """Display a data table. Either simple print,
    or HTML table
    """
    if display_mode in ['html', 'HTML']:
        display(tbl.to_html())
    else:
        print(tbl)


def load_deleted_case(yyyy, qq):
    """load the file containing delete cases to a DataFrame
    """
    fname = os.path.join(main_dir, delete_file_template % (
        yyyy, qq, yyyy % 100, qq))
    delete_frame = pd.read_csv(fname, sep='$', header=None)
    delete_frame.columns = ['caseid']
    delete_frame['todel'] = np.ones(delete_frame.shape[0], dtype=int)
    return delete_frame


def clean_delete_case(frame, delete_frame):
    """Delete the delete cases and return a new frame
    Implementation: Join with delete_frame -
    the non del elements are the good ones
    """
    tfr = pd.merge(frame, delete_frame, how='left',
                   on=['caseid'])
    return tfr.loc[pd.isnull(tfr.todel)][frame.columns]


def load_one_file(ftype, yyyy, qq, delete_frame):
    """load one file to a data frame. The structure
    of the file/dataframe is specified in the Dictionary file_struct
    """
    q_dir = os.path.join(main_dir, data_dir_template % (yyyy, qq))
    fname = os.path.join(q_dir, file_struct[ftype]['name'] % (yyyy % 100, qq))
    dtypes = file_struct[ftype]['dtype']
    date_cols = file_struct[ftype]['date_cols']
    frame = pd.read_csv(fname, sep='$', dtype=dtypes)
    for cc in date_cols:
        frame[cc] = pd.to_datetime(frame[cc], format='%Y%m%d', errors='coerce')
    frame = clean_delete_case(frame, delete_frame)
    # frame.set_index(file_struct[ftype]['idx_key'], inplace=True)
    return frame


def load_one_quarter(yyyy, qq):
    """Load all files from one quarter to all_frames
    """
    # yyyy = 2019
    # qq = 4
    # therapy
    all_frames = dict()
    delete_frame = load_deleted_case(yyyy, qq)

    for ftype in file_struct:
        all_frames[ftype] = load_one_file(ftype, yyyy, qq, delete_frame)
    return all_frames


def _get_drugs_with_many_AE(all_frames):
    """Misc test, showing drugs with many AE
    Showing AE on different countries
    """
    dr = all_frames['drug']
    e_by_drug = dr[['drugname', 'primaryid']].groupby(
        'drugname').count()
    e_by_drug.rename(columns={'primaryid': 'prim_cnt'}, inplace=True)
    display_frame(e_by_drug.describe())
    esort = e_by_drug.sort_values(by='prim_cnt', ascending=False)
    # print(esort.shape)
    # print(esort.loc[esort.primaryid > 100].shape)
    display_frame(esort.head(10))
    drug_idx = 690
    display_frame(esort.iloc[690:790])
    # try a middle of the pack
    one_drug = esort.iloc[drug_idx, :].name
    averse_by_country(all_frames, one_drug)


def averse_by_country(all_frames, one_drug):
    """Showing adverse events by country for a particular drug
    """
    dr = all_frames['drug']
    de = all_frames['demographic']
    react = all_frames['reaction']
    dr_de_fr = pd.merge(
        dr[['primaryid', 'drug_seq', 'drugname']],
        de[['primaryid', 'reporter_country', 'occr_country']], how='left',
        left_on='primaryid', right_on='primaryid')
    dr_de_react_fr = pd.merge(dr_de_fr, react, how='left',
                              left_on='primaryid', right_on='primaryid')
    """
    dr_de_react_fr = pd.merge(dr_de_fr, react, how='left',
                              left_on='primaryid', right_on='primaryid')
    """
    analyze_one_drug_by_country(dr_de_react_fr, one_drug,
                                cntry_field='occr_country')
    analyze_one_drug_by_country(dr_de_react_fr, one_drug,
                                cntry_field='reporter_country')


def analyze_one_drug_by_country(
        dr_de_react_fr, one_drug, cntry_field='occr_country',
        show_top=10):
    """Summarizing AE data on one drug by country.
    We can choose eiither occr_country or reporter_country
    """
    print('reporting on %s for %s by country and reaction' % (
        cntry_field, one_drug))
    data = dr_de_react_fr.loc[dr_de_react_fr.drugname == one_drug]

    by_cntry_tbl = data[['primaryid', cntry_field]].groupby(
        by=[cntry_field]).count().sort_values(
            by='primaryid', ascending=False)
    by_cntry_tbl.rename(columns={'primaryid': 'cnt'}, inplace=True)
    display_frame(by_cntry_tbl.head(show_top))
    print("---------------------")
    print("TOP EVENTS BY COUNTRY:")
    for c in by_cntry_tbl.index[:5]:
        react_by_cntry = data.loc[data[cntry_field] == c][
            [cntry_field, 'pt', 'primaryid']].groupby(
                [cntry_field, 'pt']).count().sort_values(
                    by=['primaryid'], ascending=False)
        react_by_cntry.rename(columns={'primaryid': 'cnt'}, inplace=True)
        display_frame(react_by_cntry.head(show_top))


def _analyze_by_disease_area(all_frames, dr_de_react_fr):
    """ test script to find a list of drugs used to
    treat many diseases. Then break down AE by disease
    for one example
    """

    indication = all_frames['indication']
    dr = all_frames['drug']
    dr_de_indication_fr = pd.merge(
        dr_de_react_fr, indication,
        how='inner', left_on=('primaryid', 'drug_seq'),
        right_on=('primaryid', 'indi_drug_seq'))

    # look for some drug use for treatment of several diseases:
    i_drug_name = pd.merge(
        dr[['primaryid', 'drug_seq', 'drugname']],
        indication[['primaryid', 'indi_drug_seq', 'indi_pt']],
        how='inner', left_on=['primaryid', 'drug_seq'],
        right_on=['primaryid', 'indi_drug_seq'])
    disct_drug_name = i_drug_name[['drugname', 'indi_pt']].groupby(
        by=['drugname', 'indi_pt']).count().reset_index()

    drug_disease = disct_drug_name.groupby(
        by=['drugname']).count().sort_values(
            by='indi_pt', ascending=False)
    drug_disease.rename(columns={'primaryid': 'cnt'}, inplace=True)
    display_frame(drug_disease)
    a_drug = drug_disease.index[0]
    analyze_by_disease_area_by_drug(a_drug, dr_de_indication_fr)


def analyze_by_disease_area_by_drug(a_drug, dr_de_indication_fr):
    """ analyze AE by disease area
    """
    data_by_drug = dr_de_indication_fr.loc[
        dr_de_indication_fr.drugname == a_drug]
    by_disease = data_by_drug[['indi_pt', 'primaryid']].groupby(
        by=['indi_pt']).count().sort_values(by=['primaryid'], ascending=False)
    # print(by_disease.head())
    print("---------------------")
    print("TOP EVENTS BY INDICATION:")

    for ipt in by_disease.index[1:10].values:
        data = data_by_drug.loc[data_by_drug.indi_pt == ipt]
        ipt_report = data[['indi_pt', 'primaryid', 'drugname', 'pt']].groupby(
            by=['indi_pt', 'drugname', 'pt']).count().sort_values(
                by='primaryid', ascending=False)
        ipt_report.rename(columns={'primaryid': 'cnt'}, inplace=True)
        display_frame(ipt_report.head(10))


def drug_used_together(all_frames):
    """List of drugs being used together
    """
    dr = all_frames['drug'][['primaryid', 'drugname']]
    dcnt = dr.groupby(by=['primaryid']).count()
    dcnt.reset_index(inplace=True)
    dcnt = dcnt.loc[dcnt.drugname > 1][['primaryid']]

    has_two = pd.merge(
        dr, dcnt, how='inner', left_on='primaryid', right_on='primaryid')

    has_two = has_two.groupby(
        ['primaryid', 'drugname']).count().reset_index().sort_values(
        ['primaryid', 'drugname'])

    pairs = pd.merge(
        has_two, has_two, how='inner',
        left_on='primaryid', right_on='primaryid').groupby(
            ['drugname_x', 'drugname_y']).count()
    pairs.reset_index(inplace=True)
    pairs = pairs.loc[pairs.drugname_x > pairs.drugname_y].sort_values(
        by='primaryid', ascending=False)
    pairs.rename(columns={'primaryid': 'cnt'}, inplace=True)
    return pairs


def validate_therapy_date(all_frames):
    """Start and end_dt data seems to be wrong
    for some therapy. Whe show the ones with bad data
    """
    therapy = all_frames['therapy']
    t1 = therapy.loc[~pd.isnull(therapy.start_dt) &
                     ~pd.isnull(therapy.end_dt) &
                     (therapy.start_dt > therapy.end_dt)]
    return t1


def check_drug_pairs(all_frames, drg1, drg2):
    """ Some drug are shown in the same trial.
    We double check that in fact the start and end date
    overlap for at least some trial
    """
    dr = all_frames['drug'][['primaryid', 'drug_seq', 'drugname']]
    therapy = all_frames['therapy'][['primaryid', 'dsg_drug_seq',
                                     'start_dt', 'end_dt']].set_index(
        ['primaryid', 'dsg_drug_seq'])
    dr1 = dr.loc[dr.drugname == drg1]
    dr2 = dr.loc[dr.drugname == drg2]
    dr_all = pd.merge(dr1, dr2, how='inner', on='primaryid')
    dr_all = dr_all.join(therapy, on=['primaryid', 'drug_seq_x'])
    dr_all = dr_all.join(therapy, on=['primaryid', 'drug_seq_y'],
                         lsuffix='_x', rsuffix='_y')
    dr_all.rename(columns={'primaryid': 'cnt'}, inplace=True)
    dr_all = dr_all.loc[~pd.isnull(dr_all.start_dt_x) &
                        ~pd.isnull(dr_all.start_dt_y) &
                        ~pd.isnull(dr_all.end_dt_x) &
                        ~pd.isnull(dr_all.end_dt_y)]
    return dr_all, dr_all.loc[(dr_all.start_dt_x < dr_all.end_dt_y) &
                              (dr_all.start_dt_y < dr_all.end_dt_x)]


def companion_drug(all_frames, a_drug):
    """ Give the list of drugs used together
    with a drug in a trial. If count is small
    it could be 1-off
    """
    dr = all_frames['drug'].loc[all_frames['drug'].drugname == a_drug]
    uq_cnt = dr[['primaryid', 'drug_seq']].groupby(
        by=['primaryid']).count().reset_index()

    all_cpn = pd.merge(
        all_frames['drug'][['primaryid', 'drugname']], uq_cnt[['primaryid']],
        how='inner', on='primaryid')
    all_cpn = all_cpn.loc[all_cpn.drugname != a_drug]
    cpn_list = all_cpn.groupby('drugname').count().sort_values(
        by='primaryid', ascending=False)
    cpn_list.rename(columns={"primaryid": "cnt"}, inplace=True)
    return cpn_list


def test_summarize_data(all_frames):
    """ check that all_frames has been loaded correctly
    """
    for kk in all_frames:
        print(kk)
        afile = all_frames[kk]
        print(afile.shape)
        print(afile.columns)
    print(data_dir_template)


if __name__ == '__main__':
    # some test scripts
    pass
