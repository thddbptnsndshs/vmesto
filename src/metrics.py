import os

import pandas as pd
from typing import List
import numpy as np


class Scorer:
    def __init__(self, username: str = None):
        if username + '.csv' in os.listdir('resources'):
            self.corpus = pd.read_csv(username + '.csv', index_col='Unnamed: 0')
        else:
            self.corpus = None

    def get_score(self, data: List) -> float:
        data = pd.DataFrame([obj.to_dict() for obj in data])
        if self.corpus is not None:
            data = pd.concat((
                self.corpus, data
            ))
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.dropna(inplace=True, subset=['wi_ratio'])
        return round(
            (1 - data.loc[data.wi_ratio < 1].wi_ratio.mean()) * (data.wi_ratio < 1).mean() * 100, 2
        )
