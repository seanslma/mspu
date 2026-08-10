import string
from collections.abc import Iterable

import numpy as np
import pandas as pd


def gen_rand_strs(
    rng: np.random.Generator,
    str_cnt: int,
    str_len: tuple[int, int],
    str_chars: list[str],
) -> list[str]:
    str_lens = rng.integers(
        low=str_len[0], high=str_len[1], size=str_cnt, endpoint=True
    )
    rand_strs = [''.join(rng.choice(str_chars, size=str_len)) for str_len in str_lens]
    return rand_strs


def gen_str_vals(
    size: int,
    rng: np.random.Generator,
    str_cnt: int | None = None,
    str_len: int | tuple[int, int] | None = None,
    str_chars: list[str] | None = None,
    col_strs: list[str] | None = None,
) -> np.ndarray:
    if str_cnt is None:
        str_cnt = 10
    if str_len is None:
        str_len = (5, 5)
    elif isinstance(str_len, int):
        str_len = (str_len, str_len)
    if col_strs is None:
        if str_chars is None:
            str_chars = [c for c in string.ascii_letters + string.digits]
        col_strs = gen_rand_strs(rng, str_cnt, str_len, str_chars)
    val = rng.choice(col_strs, size=size)
    return val


def gen_ts_vals(
    size: int,
    rng: np.random.Generator,
    start_date: str | None = None,
    end_date: str | None = None,
    freq: str | None = None,
    random: bool = False,
) -> pd.DatetimeIndex:
    if start_date is None:
        start_date = '2024-01-01'
    if end_date is None:
        end_date = '2025-01-01'
    if freq is None:
        freq = 'D'
    if random is None:
        random = False
    val = pd.date_range(start_date, end_date, freq=freq, inclusive='left')[:size]
    if random:
        val = rng.choice(val, size=size)
    return val


def gen_num_vals(
    size: int,
    rng: np.random.Generator,
    low: float | None = None,
    high: float | None = None,
    dtype: str = 'f',
) -> np.ndarray:
    if low is None:
        low = 0
    if high is None:
        high = 2
    if dtype is None or dtype == '':
        dtype = 'f'
    func = rng.integers if dtype[0] == 'i' else rng.uniform
    vals = func(low=low, high=high, size=size)
    return vals


def gen_missing_vals(
    vals: np.ndarray,
    rng: np.random.Generator,
    dtype: str,
    missing_pct: float | None = None,
) -> np.ndarray:
    if missing_pct is None or missing_pct <= 0 or missing_pct >= 1:
        return vals
    if dtype == 's':
        missing_val = None
    elif dtype == 't':
        missing_val = np.datetime64('NaT')
    else:
        missing_val = np.nan
    if dtype == 'i':
        vals = vals.astype(np.float64)
    mask = rng.uniform(size=len(vals)) <= missing_pct
    vals[mask] = missing_val
    return vals


def sanitize_parameters(
    name_prefix: str,
    params: dict,
    par_names: list[str],
):
    if isinstance(params, int):
        cnt = params
        par = {}
    else:
        cnt = params['count']
        par = {
            k: (
                list(v) + [None] * (cnt - len(v))
                if isinstance(v, Iterable) and not isinstance(v, str)
                else [v] * cnt
            )
            for k, v in params.items()
        }
    if name_prefix in ('i', 'f'):
        par_names += ['dtype']
        par['dtype'] = [name_prefix] * cnt
    default_val = [None] * cnt
    parameters = [
        {key: par.get(key, default_val)[i] for key in par_names} for i in range(cnt)
    ]
    col_names = par.get('name')
    if col_names is None or col_names.count(None) > 1 or col_names.count('') > 1:
        col_names = [f'{name_prefix}{i}' for i in range(1, cnt + 1)]
    col_missing_pcts = par.get('missing_pct', default_val)
    return col_names, parameters, col_missing_pcts


def gen_rand_df(
    nrow: int,
    str_cols: dict | None = None,
    ts_cols: dict | None = None,
    int_cols: dict | None = None,
    float_cols: dict | None = None,
    rand_seed: int = 11,
) -> pd.DataFrame:
    """
    Generate a random DataFrame with specified column types and parameters.

    Parameters
    ----------
    nrow : int
        Number of rows in the generated DataFrame.
    str_cols : dict or int, optional
        Parameters for string columns. If an integer is provided, it specifies the
        number of string columns to generate with default parameters. If a dictionary
        is provided, it should include the following keys:

        - count: number of columns
        - name: list of column names
        - str_len: int or tuple of (min, max) string length
        - str_chars: list of characters to use in strings
        - col_strs: list of lists of strings to sample from for each column (if
          provided, overrides str_len and str_chars)
    ts_cols : dict or int, optional
        Parameters for timestamp columns. If an integer is provided, it specifies the
        number of timestamp columns to generate with default parameters. If a dictionary
        is provided, it should include the following keys:

        - count: number of columns
        - name: list of column names
        - start_date: start date for timestamp generation
        - end_date: end date for timestamp generation
        - freq: frequency for timestamp generation (e.g. 'D' for daily)
        - random: whether to sample timestamps randomly from the generated range
    int_cols : dict or int, optional
        Parameters for integer columns. If an integer is provided, it specifies the
        number of integer columns to generate with default parameters. If a dictionary
        is provided, it should include the following keys:

        - count: number of columns
        - name: list of column names
        - low: lower bound for random number generation
        - high: upper bound for random number generation
        - missing_pct: percentage of values to set as missing (NaN or None)
    float_cols : dict or int, optional
        Parameters for float columns. If an integer is provided, it specifies the
        number of float columns to generate with default parameters. If a dictionary
        is provided, it should include the following keys:

        - count: number of columns
        - name: list of column names
        - low: lower bound for random number generation
        - high: upper bound for random number generation
        - missing_pct: percentage of values to set as missing (NaN or None)
    rand_seed : int, optional
        Random seed for reproducibility (default is 11).

    Returns
    -------
    pd.DataFrame
        A DataFrame with the specified random data.

    Examples
    --------

    Simply specify the number of columns for each type.

    >>> import pandas as pd
    >>> import mspu.pandas  # registry ht
    >>> from mspu.data import gen_rand_df
    >>> df = gen_rand_df(
    ...     nrow=365 * 24 * 60,
    ...     str_cols=1,
    ...     ts_cols=2,
    ...     int_cols=1,
    ...     float_cols=2,
    ... )
    >>> df.ht()
    shape: (525600, 6)
            s1            t1         t2  i1        f1        f2
    0       IZD8v 2024-01-01 2024-01-01   0  1.593760  1.648840
    1       P9r1i 2024-01-02 2024-01-02   0  1.622772  1.943180
    525598  iU68M        NaT        NaT   1  1.277124  0.093818
    525599  P9r1i        NaT        NaT   1  1.248407  0.601518

    Provide detailed parameters for each column type.

    >>> import pandas as pd
    >>> import mspu.pandas  # registry ht
    >>> from mspu.data import gen_rand_df
    >>> d2 = gen_rand_df(
    ...     nrow=10,
    ...     str_cols={
    ...         'count': 2,
    ...         'name': ['country', 'color'],
    ...         'str_len': [3, (3, 9)],
    ...         'str_cnt': [2, 5],
    ...         'col_strs': [['UK', 'US', 'AU'], ['blue', 'black', 'red']],
    ...     },
    ...     ts_cols={
    ...         'count': 2,
    ...         'name': ['start_date', 'end_date'],
    ...         'start_date': ['2020-01-01', '2024-01-01'],
    ...         'end_date': ['2021-01-01', '2025-01-01'],
    ...         'freq': 'QS',
    ...         'random': False,
    ...     },
    ...     int_cols={
    ...         'count': 1,
    ...         'name': ['quantity'],
    ...         'low': [0],
    ...         'high': [100],
    ...         'missing_pct': [0.3],
    ...     },
    ...     float_cols={
    ...         'count': 2,
    ...         'name': ['price', 'charge'],
    ...         'low': [1, 0.1],
    ...         'high': [100, 0.9],
    ...         'missing_pct': [0.3, 0.2],
    ...     },
    ... )
    >>> d2.ht(1)
    shape: (10, 7)
      country  color start_date   end_date  quantity      price    charge
    0      UK  black 2020-01-01 2024-01-01      86.0        NaN  0.657889
    9      UK  black        NaT        NaT      13.0  43.564921  0.776712
    """
    col_types = ['s', 't', 'i', 'f']
    col_params = [str_cols, ts_cols, int_cols, float_cols]
    funcs = [gen_str_vals, gen_ts_vals, gen_num_vals, gen_num_vals]
    par_names = [
        ['str_cnt', 'str_len', 'str_chars', 'col_strs'],
        ['start_date', 'end_date', 'freq', 'random'],
        ['low', 'high'],
        ['low', 'high'],
    ]
    dfs = []
    rand_rng = np.random.default_rng(seed=rand_seed)
    for i, params in enumerate(col_params):
        if params is None:
            continue
        col_names, col_params, col_missing_pcts = sanitize_parameters(
            col_types[i], params, par_names[i]
        )
        df = pd.DataFrame(
            {
                col: gen_missing_vals(
                    funcs[i](nrow, rand_rng, **col_params[j]),
                    rand_rng,
                    col_types[i],
                    col_missing_pcts[j],
                )
                for j, col in enumerate(col_names)
            }
        )
        dfs.append(df)
    if len(dfs) == 0:
        df = pd.DataFrame()
    else:
        df = pd.concat(dfs, axis=1)
    return df


if __name__ == '__main__':
    # example 1
    df = gen_rand_df(
        nrow=365 * 24 * 60,
        str_cols=1,
        ts_cols=2,
        int_cols=1,
        float_cols=2,
    )
    print(df[:2])

    # example 2
    d2 = gen_rand_df(
        nrow=10,
        str_cols={
            'count': 2,
            'name': ['country', 'color'],
            'str_len': [3, (3, 9)],
            'str_cnt': [2, 5],
            'col_strs': [['UK', 'US', 'AU'], ['blue', 'black', 'red']],
        },
        ts_cols={
            'count': 2,
            'name': ['start_date', 'end_date'],
            'start_date': ['2020-01-01', '2024-01-01'],
            'end_date': ['2021-01-01', '2025-01-01'],
            'freq': 'QS',
            'random': False,
        },
        int_cols={
            'count': 1,
            'name': ['quantity'],
            'low': [0],
            'high': [100],
            'missing_pct': [0.3],
        },
        float_cols={
            'count': 2,
            'name': ['price', 'charge'],
            'low': [1, 0.1],
            'high': [100, 0.9],
            'missing_pct': [0.3, 0.2],
        },
    )
    print(d2[:3])
