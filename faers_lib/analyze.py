"""Module to facilitate the FDA Adverse event data.
Assume that data is unpacked in folder main_dir

"""


import os
import numpy as np
import pandas as pd
from .common import file_struct, data_dir_template
from .common import delete_file_template
from .common import main_data_path as main_dir
from IPython.core.display import display, HTML

display_mode = None


def bdisplay(s):
    """utility function to print string in bold face in notebook
    """
    display(HTML("<b>%s</b>" % s))

def display_frame(tbl: pd.DataFrame):
    """Display a data table. Either simple print,
    or HTML table
    """
    if display_mode in ['html', 'HTML']:
        display(HTML(tbl.to_html()))
    else:
        print(tbl)


def load_deleted_case(yyyy, qq):
    """load the file containing delete cases to a DataFrame
    """
    fname = os.path.join(main_dir, delete_file_template % (
        yyyy, qq, yyyy % 100, qq))
    if not os.path.isfile(fname):
        return None
    delete_frame = pd.read_csv(fname, sep='$', header=None)
    delete_frame.columns = ['caseid']
    delete_frame['todel'] = np.ones(delete_frame.shape[0], dtype=int)
    return delete_frame


def clean_delete_case(frame, delete_frame):
    """Delete the delete cases and return a new frame
    Implementation: Join with delete_frame -
    the non del elements are the good ones
    """
    if delete_frame is None:
        return frame
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
    if qq > 4 or qq < 1:
        print("quarter=%d must between 1 and 4." % qq)
        raise(IOError("quarter=%d must between 1 and 4." % qq))

    elif not os.path.isfile(fname):
        print('%s does not exist. Try to download' % fname)
        raise(IOError('%s does not exist. Try to download' % fname))
    try:
        frame = pd.read_csv(fname, sep='$', dtype=dtypes)
    except Exception as e:
        print("Read Usuccessful for %s. Try locate bad character in the file then clean up" % ftype)
        raise(IOError("Read Usuccessful for %s. Try locate bad character in the file then clean up" % ftype))
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


def gen_drug_demo_react_agg(all_frames):
    dr = all_frames['drug']
    de = all_frames['demographic']
    react = all_frames['reaction']
    dr_de_fr = pd.merge(
        dr[['primaryid', 'drug_seq', 'drugname']],
        de[['primaryid', 'reporter_country', 'occr_country']], how='left',
        left_on='primaryid', right_on='primaryid')
    return pd.merge(dr_de_fr, react, how='left',
                    left_on='primaryid', right_on='primaryid')


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


if __name__ == '__main__':
    # some test scripts
    pass
