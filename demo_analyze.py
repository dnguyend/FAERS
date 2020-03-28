"""Test scripts to demonstrate analyze module.
Everything in here will be in the notebook. This
is just in case there is a problem running the notebook
"""


import pandas as pd

from faers_lib.analyze import load_one_quarter, display_frame
from faers_lib.analyze import drug_used_together, gen_drug_demo_react_agg
from faers_lib.common import data_dir_template


def analyze_pairs(pairs):
    from faers_lib.analyze import check_drug_pairs, companion_drug
    from faers_lib.analyze import display_frame
    pairs.set_index(['drugname_x', 'drugname_y'], inplace=True)
    print(pairs.head(20))
    print(pairs.loc['PRILOSEC', 'NEXIUM'])
    print(check_drug_pairs(all_frames, 'PRILOSEC', 'NEXIUM'))
    print(check_drug_pairs(all_frames, 'PREVACID', 'NEXIUM'))
    display_frame(companion_drug(all_frames, 'NEXIUM').head(10))


def get_drugs_with_many_AE(all_frames):
    """Misc test, showing drugs with many AE
    Showing AE on different countries
    """
    dr = all_frames['drug']
    e_by_drug = dr[['drugname', 'primaryid']].groupby(
        'drugname').count()
    e_by_drug.rename(columns={'primaryid': 'prim_cnt'}, inplace=True)
    display_frame(e_by_drug.describe())
    esort = e_by_drug.sort_values(by='prim_cnt', ascending=False)
    return esort


def analyze_by_disease_area(all_frames, drug_demo_react_agg):
    """ test script to find a list of drugs used to
    treat many diseases. Then break down AE by disease
    for one example
    """

    indication = all_frames['indication']
    dr = all_frames['drug']
    dr_de_indication_fr = pd.merge(
        drug_demo_react_agg, indication,
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
    # display_frame(drug_disease)
    a_drug = drug_disease.index[0]
    analyze_by_disease_area_by_drug(a_drug, dr_de_indication_fr)


def adverse_by_country(all_frames, one_drug):
    """Showing adverse events by country for a particular drug
    """

    dr_de_react_fr = gen_drug_demo_react_agg(all_frames)

    analyze_one_drug_by_country(dr_de_react_fr, one_drug,
                                cntry_field='occr_country')
    analyze_one_drug_by_country(dr_de_react_fr, one_drug,
                                cntry_field='reporter_country')


def analyze_one_drug_by_country(
        drug_demo_react_agg, one_drug, cntry_field='occr_country',
        show_top=10):
    """Summarizing AE data on one drug by country.
    We can choose eiither occr_country or reporter_country
    """
    print('reporting on %s for %s by country and reaction' % (
        cntry_field, one_drug))
    data = drug_demo_react_agg.loc[
        drug_demo_react_agg.drugname == one_drug]

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


def analyze_by_disease_area_by_drug(a_drug, dr_de_indication_fr, show_top=10):
    """ analyze AE by disease area
    """
    data_by_drug = dr_de_indication_fr.loc[
        dr_de_indication_fr.drugname == a_drug]
    by_disease = data_by_drug[['indi_pt', 'primaryid']].groupby(
        by=['indi_pt']).count().sort_values(by=['primaryid'], ascending=False)
    # print(by_disease.head())
    print("---------------------")
    print("TOP EVENTS BY INDICATION:")

    for ipt in by_disease.index[:show_top].values:
        data = data_by_drug.loc[data_by_drug.indi_pt == ipt]
        ipt_report = data[['indi_pt', 'primaryid', 'drugname', 'pt']].groupby(
            by=['indi_pt', 'drugname', 'pt']).count().sort_values(
                by='primaryid', ascending=False)
        ipt_report.rename(columns={'primaryid': 'cnt'}, inplace=True)
        display_frame(ipt_report.head(show_top))


def analyze_disease(all_frames):
    import pandas as pd
    dr = all_frames['drug']
    de = all_frames['demographic']
    react = all_frames['reaction']
    dr_de_fr = pd.merge(
        dr[['primaryid', 'drug_seq', 'drugname']],
        de[['primaryid', 'reporter_country', 'occr_country']], how='left',
        left_on='primaryid', right_on='primaryid')
    dr_de_react_fr = pd.merge(
        dr_de_fr, react, how='left',
        left_on='primaryid', right_on='primaryid')
    analyze_by_disease_area(all_frames, dr_de_react_fr)


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
    all_frames = load_one_quarter(2019, 4)
    test_summarize_data(all_frames)
    pairs = drug_used_together(all_frames)
    analyze_pairs(pairs)

    esort = get_drugs_with_many_AE(all_frames)
    display_frame(esort.head(10))
    # try one drug
    drug_idx = 690
    display_frame(esort.iloc[690:790])

    # try a middle of the pack
    one_drug = esort.iloc[drug_idx, :].name
    adverse_by_country(all_frames, one_drug)

    analyze_disease(all_frames)
    pass
