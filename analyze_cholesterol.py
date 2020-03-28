"""Script to analyze cholesterol.
    First identify the drugs used in cholesterol treatment
    Then link with drug, indication and outcome
    What to see if age, dose and weight affect severe outcome
    Severe outcome mean Death, life threatening outcome or disability
    Enrich to make weight in kg, dose_freq in day and dose in mg
    Convert to make dose pert day
    Then run a logistic regression
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from faers_lib.analyze import load_one_quarter


convert_fname = 'cfg/convert.txt'


def get_chol_data_frame(all_frames):
    """First identify the drugs used in cholesterol treatment
    Then link with drug, indication and outcome
    """

    idpts = all_frames['indication'].indi_pt.unique()
    choles_indi = np.array(
        [a for a in idpts
         if ('choles' in a.lower() and 'cholestasis' not in a.lower())])
    choles_indi = pd.DataFrame({"indi_pt": choles_indi})
    choles_indi_all = pd.merge(
        all_frames['indication'], choles_indi, how='inner', on='indi_pt')
    drug_indi = pd.merge(
        choles_indi_all, all_frames['drug'],
        how='inner', left_on=['primaryid', 'indi_drug_seq'],
        right_on=['primaryid', 'drug_seq'], suffixes=('', '_y'))
    drug_indi.drop(columns=['caseid_y'], inplace=True)

    demo_drug_indi = pd.merge(
        drug_indi, all_frames['demographic'],
        how='inner', on='primaryid', suffixes=('', '_y'))

    demo_drug_indi.drop(columns=['caseid_y'], inplace=True)
    outcome_demo_drug_indi = pd.merge(
        demo_drug_indi, all_frames['outcome'],
        how='inner', on='primaryid', suffixes=('', '_y'))
    outcome_demo_drug_indi.drop(columns=['caseid_y'], inplace=True)
    """
    react_outcome_demo_drug_indi = pd.merge(
       outcome_demo_drug_indi, all_frames['reaction'],
       how='inner', on='primaryid', suffixes=('', '_y'))
    react_outcome_demo_drug_indi.drop(columns=['caseid_y'], inplace=True)
    """
    return outcome_demo_drug_indi, demo_drug_indi


def uniformizing_age_dose_weight(mf, cvt_fr):
    """Uniformizng data to make sure weight, freq, dose in one unit
    """
    def check_bad_code(col, field):
        ucode = mf[col].unique()
        ucode = ucode[~pd.isnull(ucode)]
        map_frame = cvt_fr.loc[cvt_fr.FIELD == field]
        diff = np.setdiff1d(ucode, map_frame.UNIT)
        if diff.shape[0] > 0:
            print('bad code %s %s %s' % (col, field, str(diff)))

    col = 'wt_cod'
    field = 'DEMOGRAPHIC.WT_COD'
    check_bad_code(col, field)
    # convert weight to kg
    mf['wt_in_kg'] = np.full((mf.shape[0]), np.nan)

    for idx in cvt_fr.loc[cvt_fr.FIELD == field].index:
        unt = cvt_fr.loc[idx, 'UNIT']
        ft = cvt_fr.loc[idx, 'FACTOR']

        mf.loc[mf[col] == unt, 'wt_in_kg'] = mf.loc[mf[col] == unt, 'wt'] * ft

    col = 'age_cod'
    field = 'DEMOGRAPHIC.AGE_COD'
    check_bad_code(col, field)
    # convert weight to kg
    mf['age_in_yr'] = np.full((mf.shape[0]), np.nan)

    for idx in cvt_fr.loc[cvt_fr.FIELD == field].index:
        unt = cvt_fr.loc[idx, 'UNIT']
        ft = cvt_fr.loc[idx, 'FACTOR']

        mf.loc[mf[col] == unt, 'age_in_yr'] = mf.loc[mf[col] == unt, 'age'] * ft        

    col = 'dose_unit'
    field = 'DRUG.DOSE_UNIT'
    check_bad_code(col, field)

    mf['dose_in_mg'] = np.full((mf.shape[0]), np.nan)

    for idx in cvt_fr.loc[cvt_fr.FIELD == field].index:
        unt = cvt_fr.loc[idx, 'UNIT']
        base = cvt_fr.loc[idx, 'BASE']
        ft = cvt_fr.loc[idx, 'FACTOR']
        if base == 'MG':
            mf.loc[mf[col] == unt, 'dose_in_mg'] =\
                mf.loc[mf[col] == unt, 'dose_amt'] * ft

    col = 'dose_freq'
    field = 'DRUG.DOSE_FREQ'
    check_bad_code(col, field)
    mf['freq_in_day'] = np.full((mf.shape[0]), np.nan)
    for idx in cvt_fr.loc[cvt_fr.FIELD == field].index:
        unt = cvt_fr.loc[idx, 'UNIT']
        ft = cvt_fr.loc[idx, 'FACTOR']

        mf.loc[mf[col] == unt, 'freq_in_day'] = ft

    mf['dose_per_day'] = mf['freq_in_day'] * mf['dose_in_mg']
    to_fill = pd.isnull(mf.dose_per_day) & ~pd.isnull(mf.dose_in_mg)
    mf.loc[to_fill, 'dose_per_day'] = mf.loc[to_fill, 'dose_in_mg'].values
    return mf


def bdisplay(s):
    print(s)


def analyze_cholesterol(all_frames):
    """Do the main analysis.
    call functions to populate the main cholesterol data frame
    populate
    """
    cvt_fr = pd.read_csv(convert_fname, sep='|')
    # main data frame
    out_dr_de_indi, dr_de_indi = get_chol_data_frame(all_frames)
    dr_de_indi = uniformizing_age_dose_weight(dr_de_indi, cvt_fr)
    # rs = outcome_demo_drug_indi
    tmp_fr = pd.crosstab(
        index=[out_dr_de_indi.primaryid,
               out_dr_de_indi.drug_seq],
        columns=out_dr_de_indi.outc_cod)
    summ_fr = pd.merge(
        dr_de_indi.reset_index(), tmp_fr,
        how='inner', on=['primaryid', 'drug_seq'])
    """
    summ_fr['severe'] = ((summ_fr.DE == 1) | (summ_fr.DS == 1) |
                         (summ_fr.LT == 1)).astype(int)
    """
    summ_fr['severe'] = ((summ_fr.DE == 1)).astype(int)

    summ_fr['dose_norm'] = summ_fr.dose_per_day / summ_fr.dose_per_day.std()
    summ_fr['wt_norm'] = summ_fr.wt_in_kg / summ_fr.wt_in_kg.std()

    for f_icpt in [True, False]:
        bdisplay("Doing intercept=%s" % str(f_icpt))
        logistic = LogisticRegression(
            penalty='l1',
            max_iter=1000, fit_intercept=True, solver='liblinear')

        bdisplay("Regress by Age, dose, wt")
        Big = summ_fr[['age_in_yr', 'dose_per_day', 'wt_in_kg', 'severe']].loc[
            ~pd.isnull(summ_fr.age_in_yr) & ~pd.isnull(summ_fr.dose_in_mg) &
            ~pd.isnull(summ_fr.wt_in_kg) & ~pd.isnull(summ_fr.severe)]
        logistic.fit(Big.iloc[:, :-1], Big.iloc[:, -1])
        print('coeffs %s' % str(logistic.coef_))
        print('Good sample size %d' % Big.describe().iloc[0, 0])

        bdisplay("Regress Dose, wt")
        Big = summ_fr[['dose_per_day', 'wt_in_kg', 'severe']].loc[
            ~pd.isnull(summ_fr.dose_in_mg) &
            ~pd.isnull(summ_fr.wt_in_kg)]
        logistic.fit(Big.iloc[:, :-1], Big.iloc[:, -1])
        print('coeffs %s' % str(logistic.coef_))
        print('Good sample size %d' % Big.describe().iloc[0, 0])

        bdisplay("Regress Age")
        Big = summ_fr[['age_in_yr', 'severe']].loc[
            ~pd.isnull(summ_fr.age_in_yr)]
        logistic.fit(Big.iloc[:, :-1], Big.iloc[:, -1])
        print('coeffs %s' % str(logistic.coef_))
        print('Good sample size %d' % Big.describe().iloc[0, 0])

        bdisplay("Regress Dose")
        Big = summ_fr[['dose_per_day', 'severe']].loc[
            ~pd.isnull(summ_fr.dose_per_day)]
        logistic.fit(Big.iloc[:, :-1], Big.iloc[:, -1])
        print('coeffs %s' % str(logistic.coef_))
        print('Good sample size %d' % Big.describe().iloc[0, 0])

        bdisplay("Regress wt")
        Big = summ_fr[['wt_in_kg', 'severe']].loc[
            ~pd.isnull(summ_fr.wt_in_kg)]
        logistic.fit(Big.iloc[:, :-1], Big.iloc[:, -1])
        print('coeffs %s' % str(logistic.coef_))
        print('Good sample size %d' % Big.describe().iloc[0, 0])


        
if __name__ == '__main__':
    all_frames = load_one_quarter(2017, 1)
    analyze_cholesterol(all_frames)
