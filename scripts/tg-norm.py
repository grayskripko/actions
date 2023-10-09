import json, os
import pandas as pd
import numpy as np
from pandas import json_normalize
from functools import reduce


def get_msgs(fpath):
    with open(fpath, 'r') as f:
        return json_normalize(json.load(f)['messages'])

def clean_alittle(msg):
    return ''.join([x if isinstance(x, str) else x['text'] for x in msg])\
        .replace('\n\n', '\n').replace('\nclick to apply', '')

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
        .pipe(lambda d: d.set_axis(d.columns.str.lower(), axis=1))
        # .pipe(lambda d: d.drop([col for col in d.select_dtypes(include=['number']) if d[col].sum() < 3], axis=1))


if __name__ == '__main__':
    fpath = '/mnt/c/Users/srskr/Downloads/Telegram Desktop/ChatExport_2023-10-05/result.json'
    cln = clean(get_msgs(fpath))
    print(cln)
    # cln.to_csv(os.path.dirname(fpath) + '/clean.csv', index=False)
    cln\
        .assign(power_bi=lambda d: d['text'].str.lower().str.contains('power bi'))\
        .query('power_bi')\
        .drop(columns=['power_bi'])\
        .loc[:, lambda d: d.nunique() == 2]\
        .pipe(lambda d: d.set_axis(d.columns.str.upper(), axis=1))
    #     .sort_values(ascending=False)\
    #     .loc[lambda x: x > 1]\
    #     .pipe(print)