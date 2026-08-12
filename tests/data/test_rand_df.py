import numpy as np
import pandas as pd
import pytest

from mspu.data.rand_df import (
    gen_missing_vals,
    gen_num_vals,
    gen_rand_df,
    gen_rand_strs,
    gen_str_vals,
    gen_ts_vals,
)


@pytest.fixture
def rng():
    return np.random.default_rng(11)


def test_gen_rand_df_defaults():
    df = gen_rand_df(nrow=10, str_cols=1, ts_cols=1, int_cols=1, float_cols=1)
    assert df.shape == (10, 4)
    assert df.columns.tolist() == ['s1', 't1', 'i1', 'f1']
    assert pd.api.types.is_string_dtype(df['s1'])
    assert pd.api.types.is_datetime64_any_dtype(df['t1'])
    assert pd.api.types.is_integer_dtype(df['i1'])
    assert pd.api.types.is_float_dtype(df['f1'])


def test_gen_rand_df_reproducible():
    df1 = gen_rand_df(
        nrow=20, str_cols=1, ts_cols=1, int_cols=1, float_cols=1, rand_seed=42
    )
    df2 = gen_rand_df(
        nrow=20, str_cols=1, ts_cols=1, int_cols=1, float_cols=1, rand_seed=42
    )
    pd.testing.assert_frame_equal(df1, df2)


def test_gen_rand_df_named_columns():
    df = gen_rand_df(
        nrow=5,
        str_cols={'count': 2, 'name': ['country', 'color']},
        int_cols={'count': 1, 'name': ['quantity'], 'low': [0], 'high': [10]},
    )
    assert df.columns.tolist() == ['country', 'color', 'quantity']


def test_gen_rand_df_missing_values():
    df = gen_rand_df(
        nrow=100,
        int_cols={'count': 1, 'name': ['quantity'], 'missing_pct': [0.5]},
        float_cols={'count': 1, 'name': ['price'], 'missing_pct': [0.5]},
    )
    assert df['quantity'].isna().sum() > 0
    assert df['price'].isna().sum() > 0


def test_gen_rand_df_empty():
    df = gen_rand_df(nrow=10)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_gen_rand_strs():
    rng = np.random.default_rng(1)
    strs = gen_rand_strs(rng, str_cnt=5, str_len=(3, 6), str_chars=['a', 'b', 'c'])
    assert len(strs) == 5
    assert all(3 <= len(s) <= 6 for s in strs)
    assert all(set(s) <= {'a', 'b', 'c'} for s in strs)


def test_gen_str_vals_with_col_strs():
    vals = gen_str_vals(10, np.random.default_rng(1), col_strs=['UK', 'US'])
    assert set(vals) <= {'UK', 'US'}


def test_gen_ts_vals():
    # inclusive='left' excludes the end date, so 2024-01-01..2024-01-05 yields 4 days
    vals = gen_ts_vals(
        5, np.random.default_rng(1), start_date='2024-01-01', end_date='2024-01-05'
    )
    assert len(vals) == 4
    assert isinstance(vals, pd.DatetimeIndex)


def test_gen_num_vals_default_dtype():
    # dtype defaults to float; previously crashed with dtype=None
    vals = gen_num_vals(10, np.random.default_rng(1))
    assert vals.dtype.kind == 'f'
    assert vals.shape == (10,)


def test_gen_num_vals_int():
    vals = gen_num_vals(10, np.random.default_rng(1), low=0, high=5, dtype='i')
    assert vals.dtype.kind == 'i'
    assert vals.min() >= 0
    assert vals.max() < 5


def test_gen_missing_vals_noop():
    vals = np.array([1.0, 2.0, 3.0])
    out = gen_missing_vals(vals, np.random.default_rng(1), 'f', missing_pct=0)
    np.testing.assert_array_equal(out, vals)
    out = gen_missing_vals(vals, np.random.default_rng(1), 'f', missing_pct=1)
    np.testing.assert_array_equal(out, vals)


def test_gen_missing_vals_float():
    vals = np.array([1.0, 2.0, 3.0, 4.0])
    out = gen_missing_vals(vals, np.random.default_rng(1), 'f', missing_pct=0.5)
    # roughly half the values become NaN (exact count depends on the rng draw)
    assert 0 < np.isnan(out).sum() < 4


def test_gen_missing_vals_int_converts_to_float():
    vals = np.array([1, 2, 3, 4])
    out = gen_missing_vals(vals, np.random.default_rng(1), 'i', missing_pct=0.5)
    assert out.dtype.kind == 'f'
    assert 0 < np.isnan(out).sum() < 4
