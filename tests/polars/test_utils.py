import polars as pl

from mspu.polars import (
    inf_count,
    lowercase_polars_df,
    nan_count,
    nul_count,
    to_float32_polars_df,
)
from mspu.polars.utils import parquet_to_csv


def test_ht_accessor_registered():
    df = pl.DataFrame({'foo': [1.12345, 2.98765], 'bar': [7, 8]})
    assert hasattr(df, 'ht')


def test_ht_rounding(capsys):
    df = pl.DataFrame({'foo': [1.12345, 2.98765, 3.14159], 'bar': [7, 8, 9]})
    df.ht(n=1, c=2, r=2)
    out = capsys.readouterr().out
    assert '1.12' in out
    assert '3.14' in out


def test_lowercase_polars_df():
    df = pl.DataFrame({'Name': ['Alice', 'Bob'], 'City': ['NYC', 'LAX']})
    result = lowercase_polars_df(df)
    assert result.columns == ['name', 'city']
    assert result['name'].to_list() == ['alice', 'bob']


def test_lowercase_headers_only():
    df = pl.DataFrame({'Name': ['Alice'], 'City': ['NYC']})
    result = lowercase_polars_df(df, lowercase='header')
    assert result.columns == ['name', 'city']
    assert result['name'].to_list() == ['Alice']


def test_lowercase_columns_only():
    df = pl.DataFrame({'Name': ['Alice'], 'City': ['NYC']})
    result = lowercase_polars_df(df, lowercase='columns')
    assert result.columns == ['Name', 'City']
    assert result['Name'].to_list() == ['alice']


def test_to_float32_polars_df():
    df = pl.DataFrame({'a': [1, 2], 'b': [1.5, 2.5], 'c': ['x', 'y']})
    result = to_float32_polars_df(df)
    assert result.schema['a'] == pl.Float32
    assert result.schema['b'] == pl.Float32
    assert result.schema['c'] == pl.String


def test_inf_count():
    df = pl.DataFrame({'a': [1.0, float('inf')], 'b': [1.0, 2.0]})
    result = inf_count(df)
    assert result['col'].to_list() == ['a']
    assert result['inf_cnt'].to_list() == [1]


def test_inf_count_ignores_non_numeric():
    # previously crashed on string columns
    df = pl.DataFrame({'a': [1.0, float('inf')], 's': ['x', 'y']})
    result = inf_count(df)
    assert result['col'].to_list() == ['a']


def test_nan_count():
    df = pl.DataFrame({'a': [1.0, float('nan')], 'b': [1.0, 2.0]})
    result = nan_count(df)
    assert result['col'].to_list() == ['a']
    assert result['nan_cnt'].to_list() == [1]


def test_nan_count_ignores_non_numeric():
    df = pl.DataFrame({'a': [1.0, float('nan')], 's': ['x', 'y']})
    result = nan_count(df)
    assert result['col'].to_list() == ['a']


def test_counts_no_numeric_columns():
    df = pl.DataFrame({'s': ['x', None]})
    assert inf_count(df).shape == (0, 2)
    assert nan_count(df).shape == (0, 2)


def test_nul_count():
    df = pl.DataFrame({'a': [1, None], 'b': [1.0, 2.0], 's': ['x', None]})
    result = nul_count(df)
    assert set(result['col'].to_list()) == {'a', 's'}
    assert result['nul_cnt'].to_list() == [1, 1]


def test_parquet_to_csv_pq(tmp_path):
    df = pl.DataFrame({'a': [1, 2], 'b': ['x', 'y']})
    pq_path = tmp_path / 'data.pq'
    df.write_parquet(pq_path)
    csv_path = parquet_to_csv(str(pq_path))
    assert csv_path == str(tmp_path / 'data.csv')
    assert pl.read_csv(csv_path).equals(df)


def test_parquet_to_csv_full_extension(tmp_path):
    df = pl.DataFrame({'a': [1, 2]})
    pq_path = tmp_path / 'data.parquet'
    df.write_parquet(pq_path)
    csv_path = parquet_to_csv(str(pq_path))
    assert csv_path == str(tmp_path / 'data.csv')
