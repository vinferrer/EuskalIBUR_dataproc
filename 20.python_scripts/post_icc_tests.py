#!/usr/bin/env python3

import os
from copy import deepcopy
from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from scipy.stats import ttest_rel
from statsmodels.formula.api import ols

P_VALS = [0.05, 0.01, 0.001]

CTYPE_LIST = ['intrasub', 'intrases', 'total']
FTYPE_LIST = ['echo-2', 'optcom', 'meica-aggr', 'meica-orth', 'meica-cons',
              'all-orth']

SET_DPI = 100
FIGSIZE = (18, 10)


def t_test_and_export(f_dict, filename):
    # Prepare pandas dataframes
    df = pd.DataFrame(columns=['ftype1', 'ftype2', 't', 'p'])

    # Run t-test and append results to the df
    for ftype_one, ftype_two in list(combinations(FTYPE_LIST, 2)):
        t, p = ttest_rel(f_dict[ftype_one], f_dict[ftype_two])
        df = df.append({'ftype1': ftype_one, 'ftype2': ftype_two,
                        't': t, 'p': p}, ignore_index=True)

    df.to_csv(filename.format(p_val='no_thr'))
    # Threshold t-tests and export them
    t_mask = dict.fromkeys(P_VALS, df.copy(deep=True))
    for p_val in P_VALS:
        # Compute Sidak correction
        p_corr = 1-(1-p_val)**(1/len(list(combinations(FTYPE_LIST, 2))))
        t_mask[p_val]['p'] = t_mask[p_val]['p'].mask(t_mask[p_val]['p'] > p_corr)
        t_mask[p_val].to_csv(filename.format(p_val=p_val))


def anova_and_export(f_dict, filename, map):
    df = pd.DataFrame(columns=['val', 'ftype'])

    # Rearrange data in long format table
    for ftype in FTYPE_LIST:
        tdf = pd.DataFrame(data=f_dict[ftype], columns=['val', ])
        tdf['ftype'] = ftype
        df = df.append(tdf)

    # Seaborn it out!
    plt.figure(figsize=FIGSIZE, dpi=SET_DPI)
    sns.boxenplot(x='ftype', y='val', data=df)
    plt.xlabel('')
    plt.ylabel(f'{map.upper()}')
    fig_name = f'{filename}.png'
    plt.savefig(fig_name, dpi=SET_DPI)
    plt.clf()
    plt.close()

    # ANOVA
    model = ols('val ~ C(ftype)', data=df).fit()

    # Export table
    with open(f'{filename}.txt', 'w') as f:
        print(sm.stats.anova_lm(model, typ=2), file=f)


# THIS IS MAIN
cwd = os.getcwd()
os.chdir('/data/CVR_reliability/tests')

# Prepare dictionaries
icc = {'cvr': {}, 'lag': {}}
t_icc = {'cvr': {}, 'lag': {}}

d = dict.fromkeys(FTYPE_LIST, '')
cov = {'cvr': {'intrasub': deepcopy(d),
               'intrases': deepcopy(d),
               'total': deepcopy(d)},
       'lag': {'intrasub': deepcopy(d),
               'intrases': deepcopy(d),
               'total': deepcopy(d)}}
t_cov = {'cvr': {'intrasub': deepcopy(d),
                 'intrases': deepcopy(d),
                 'total': deepcopy(d)},
         'lag': {'intrasub': deepcopy(d),
                 'intrases': deepcopy(d),
                 'total': deepcopy(d)}}


for map in ['cvr', 'lag']:
    # Read files and import ICC and CoV values
    for ftype in FTYPE_LIST:
        icc[map][ftype] = np.genfromtxt(f'val/ICC2_{map}_masked_{ftype}.txt')[:, 3]

        for ctype in CTYPE_LIST:
            # Actually testing the absolute of the CoV
            cov[map][ctype][ftype] = np.absolute(np.genfromtxt(f'val/CoV_{ctype}_{map}_masked_{ftype}.txt')[:, 3])

    # Tests
    t_test_and_export(icc[map], f'Ttests_ICC_{map.upper()}_{{p_val}}.csv')
    anova_and_export(icc[map], f'ANOVA_ICC_{map.upper()}', map)

    for ctype in CTYPE_LIST:
        t_test_and_export(cov[map][ctype], f'Ttests_CoV_{ctype}_{map.upper()}_{{p_val}}.csv')
        anova_and_export(cov[map][ctype], f'ANOVA_CoV_{ctype}_{map.upper()}', map)


os.chdir(cwd)
