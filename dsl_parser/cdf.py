from typing import List
from bisect import bisect_left


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

    def simple_str(self):
        """inline (might not be necessary but fixing lark issue)"""
        return f"{{xs: {self.xs}, ys: {self.ys}}}"

    def __eq__(self, cdf):
        if self.xs == cdf.xs and self.ys == cdf.ys:
            return True
        False

    def closest_idx(self, l, n):
        pos = bisect_left(l, n)
        if pos == 0:
            return 0
        if pos+1 == len(l):
            return -1
        before = l[pos - 1]
        after = l[pos + 1]
        if after - n < n - before:
            return pos + 1
        else:
            return pos - 1

    def findY(self, x, l):
        """
        Returns the YS for the a given XS
        Assumes that the ys and xs are of equal len
        """
        return self.ys[self.closest_idx(l, x)]

    def combine_cdf(self, cdf, sample_count=10):
        "Take self and another CDF and return the zipped average of the two lists"
        # lower and upper bound of xs
        m_s = min(len(self.xs), len(cdf.xs))
        if sample_count > m_s:
            sample_count = m_s
        lower = min(self.xs[0], cdf.xs[0])
        upper = max(self.xs[-1], cdf.xs[-1])
        xs = [lower + x*(upper-lower) /
              sample_count for x in range(sample_count)]
        ys = [(cdf.findY(x, xs)+self.findY(x, xs))/2 for x in xs]
        return xs, ys

    def __add__(self, b):
        return self.combine_cdf(b)

    def __sub__(self, b):
        b.xs = map(lambda x: x*-1, b.xs)
        b.ys = map(lambda y: y*-1, b.ys)
        return self.combine_cdf(b)


def test():
    cdfA = CDF([1, 2, 3, 4, 5], [.1, .2, .3, .2, .1])
    cdfB = CDF([1, 2, 5, 7, 8], [.3, .5, .5, .3, .02])
    # TODO: Check against known successful combination
    print(cdfA.combine_cdf(cdfB))


if __name__ == "__main__":
    test()
