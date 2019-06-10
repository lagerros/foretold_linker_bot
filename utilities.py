from typing import List
from itertools import zip_longest
from statistics import mean

class CDF():
    """
    CDF class that holds the info for a Foretold CDF
    """
    def __init__(self, xs: List, ys: List, *args, **kwargs):
        self.xs = xs
        self.ys = ys
        return super().__init__(*args, **kwargs)

    def __str__(self):
        # TODO: check json format feature to avoid manually constructing string. IMPORTANT FOR LIST Logic
        return f"""{{
            floatCdf: {{
                xs: {self.xs},
                ys: {self.ys}
            }},
        }}
        """
    
    def __eq__(self, cdf):
        if self.xs == cdf.xs and self.ys == cdf.ys:
            return True
        False

    def combine_cdf(self, cdf):
        "Take self and another CDF and return the zipped average of the two lists"
        xs = [mean(i) for i in zip_longest([self.xs, cdf.xs], fillvalue=0.0)]
        ys = [mean(i) for i in zip_longest([self.ys, cdf.ys], fillvalue=0.0)]
        return xs, ys
               