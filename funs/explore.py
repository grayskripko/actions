import json, os
import pandas as pd
import numpy as np
from pandas import json_normalize
from functools import reduce

fpath = '/mnt/c/Users/srskr/Downloads/Telegram Desktop/ChatExport_2023-08-31/result.json'


def get_msgs():
    with open(fpath, 'r') as f:
        return json_normalize(json.load(f)['messages'])

def clean_alittle(msg):
    return ''.join([x if isinstance(x, str) else x['text'] for x in msg])\
        .replace('\n\n', '\n').replace('\nclick to apply', '')

def to_str(msgs):
    return '\n\n'.join(
        msgs['text']\
        .map(clean_alittle)\
        .head()\
        .tolist())

def clean(msgs):
    return msgs['text']\
        .map(clean_alittle)\
        .drop_duplicates()\
        .pipe(lambda s: s.set_axis(s))\
        .pipe(lambda s: s.str.extract(r'Skills:(.*)').squeeze().str.strip().str.split('\s*,\s*'))\
        .rename('skill')\
        .explode()\
        .loc[lambda s: s != '']\
        .to_frame()\
        .assign(val = 1)\
        .pivot(columns='skill', values='val')\
        .fillna(0).astype(int)\
        .reset_index()\
        .assign(cat = lambda df: df['text'].str.extract(r'Category:(.*)').squeeze())\
        .pipe(lambda d: d.drop([col for col in d.select_dtypes(include=['number']) if d[col].sum() < 3], axis=1))
# cln.to_csv(os.path.dirname(fpath) + '/clean.csv', index=False)


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
#     .assign(y = lambda d: (~d['y'].astype(bool)).astype(int))
print(f'{len(xy)} -> {len(xy2)}')
xy2.agg(lambda x: np.round(xy2['y'].loc[x.astype(bool)].mean(), 2))\
    .to_frame('mn')\
    .assign(n = xy2.agg(sum))\
    .assign(i = lambda d: (np.sqrt(d['mn'] * d['n'])).round(1))\
    .sort_values('i', ascending=False)\
    .drop(columns=['i'])\
    .pipe(lambda d: print(d.head(15)))