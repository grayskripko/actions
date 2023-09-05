import json, os
import pandas as pd
from pandas import json_normalize

fpath = '/mnt/c/Users/srskr/Downloads/Telegram Desktop/ChatExport_2023-08-31/result.json'

def get_msg():
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

def get_clean_msg(msgs):
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

# cln.loc[lambda d: d["Lead Generation"]]

x = pd.read_csv(os.path.dirname(fpath) + '/y_clean.csv')
print(x)
