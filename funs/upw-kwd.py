import os
import pandas as pd
import numpy as np
from functools import reduce

fpath = '/mnt/c/Users/srskr/Downloads/Telegram Desktop/ChatExport_2023-10-05/result.json'


def filter_labeled():
    return pd.read_csv(os.path.dirname(fpath) + '/y_clean.csv')\
        .drop(columns=['text'])\
        .assign(cat=lambda d: d['cat'].str.strip())\
        .pipe(lambda d: pd.get_dummies(d, prefix='cat', columns=['cat'], drop_first=True))\
        .rename(columns={'label': 'y'})\
        .assign(y = lambda d: (~d['y'].astype(bool)).astype(int))
        

xy = filter_labeled()
nnot = ['Data Entry', 'Google Analytics', 'cat_Full Stack Development', 'Market Research', 'Automation']

xy2 = reduce(lambda d, c: d.loc[lambda dd: ~dd[c].astype(bool)], [xy] + nnot)

print(f'{len(xy)} -> {len(xy2)}')
xy2.agg(lambda x: np.round(xy2['y'].loc[x.astype(bool)].mean(), 2))\
    .to_frame('mn')\
    .assign(n = xy2.agg(sum))\
    .assign(i = lambda d: (np.sqrt(d['mn'] * d['n'])).round(1))\
    .sort_values('i', ascending=False)\
    .drop(columns=['i'])\
    .pipe(lambda d: print(d.head(15)))