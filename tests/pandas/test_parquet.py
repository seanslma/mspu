import pandas as pd

from mspu.pandas import pa_mod


def test_pa_mod():
    df = pd.DataFrame({'x': [-2, -8, 3]}, dtype='int64[pyarrow]')
    assert pa_mod(df.iat[1, 0], 2) == 0
    assert pa_mod(df.iat[1, 0], 3) == 1
    assert pa_mod(df['x'], 3).tolist() == [1, 1, 0]
    assert pa_mod(df['x'], 4).tolist() == [2, 0, 3]
    assert pa_mod(df['x'], 5).tolist() == [3, 2, 3]
    assert pa_mod(df['x'], 8).tolist() == [6, 0, 3]
