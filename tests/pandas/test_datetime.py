import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from mspu.pandas import explode_date_range


def test_basic():
    df = pd.DataFrame(
        {
            'start_date': ['2023-01-01', '2023-01-02'],
            'end_date': ['2023-01-01 01:00:00', '2023-01-02 02:00:00'],
        }
    )

    result = explode_date_range(df, 'start_date', 'end_date', freq='1h')
    expected = pd.DataFrame(
        {
            'ts': pd.to_datetime(
                [
                    '2023-01-01 00:00:00',
                    '2023-01-01 01:00:00',
                    '2023-01-02 00:00:00',
                    '2023-01-02 01:00:00',
                    '2023-01-02 02:00:00',
                ]
            )
        }
    )

    assert_frame_equal(result[['ts']], expected)


def test_with_offsets():
    df = pd.DataFrame(
        {
            'start_date': ['2023-01-01', '2023-01-02'],
            'end_date': ['2023-01-01 01:00:00', '2023-01-02 02:00:00'],
        }
    )

    result = explode_date_range(
        df,
        'start_date',
        'end_date',
        freq='1h',
        start_date_offset=pd.DateOffset(hours=1),
        end_date_offset=pd.DateOffset(hours=-1),
    )
    expected = pd.DataFrame({'ts': pd.to_datetime(['2023-01-02 01:00:00'])})

    assert_frame_equal(result[['ts']], expected)


def test_with_roll():
    df = pd.DataFrame(
        {
            'start_date': ['2023-01-01 00:30:00', '2023-01-02 00:30:00'],
            'end_date': ['2023-01-01 01:30:00', '2023-01-02 02:30:00'],
        }
    )

    result = explode_date_range(
        df,
        'start_date',
        'end_date',
        freq='1h',
        start_date_roll='forward',
        end_date_roll='backward',
    )
    expected = pd.DataFrame(
        {
            'ts': pd.to_datetime(
                ['2023-01-01 01:00:00', '2023-01-02 01:00:00', '2023-01-02 02:00:00']
            )
        }
    )

    assert_frame_equal(result[['ts']], expected)


def test_empty_dataframe():
    df = pd.DataFrame(columns=['start_date', 'end_date'])
    result = explode_date_range(df, 'start_date', 'end_date', freq='1h')
    expected = pd.DataFrame(columns=['ts'], dtype='datetime64[ns]')

    assert_frame_equal(result, expected)


def test_invalid_column_names():
    df = pd.DataFrame(
        {'start_date': ['2023-01-01'], 'end_date': ['2023-01-01 01:00:00']}
    )

    with pytest.raises(KeyError):
        explode_date_range(df, 'invalid_start', 'end_date', freq='1h')


def test_min_max_date():
    df = pd.DataFrame(
        {
            'start_date': ['2022-12-31', '2023-01-01'],
            'end_date': ['2023-01-01 01:00:00', '2023-01-02 02:00:00'],
        }
    )
    result = explode_date_range(
        df,
        'start_date',
        'end_date',
        freq='1h',
        min_date='2023-01-01',
        max_date='2023-01-02 01:00:00',
    )
    # first row's start clamps up to min_date, last row's end clamps down to max_date
    assert result['ts'].min() == pd.Timestamp('2023-01-01 00:00:00')
    assert result['ts'].max() == pd.Timestamp('2023-01-02 01:00:00')


def test_inclusive_left_excludes_equal_dates():
    df = pd.DataFrame(
        {
            'start_date': ['2023-01-01 00:00:00', '2023-01-02 00:00:00'],
            'end_date': ['2023-01-01 00:00:00', '2023-01-02 01:00:00'],
        }
    )
    result = explode_date_range(
        df, 'start_date', 'end_date', freq='1h', inclusive='left'
    )
    # row with start == end is dropped entirely
    assert len(result) == 1
    assert result['ts'].iloc[0] == pd.Timestamp('2023-01-02 00:00:00')


def test_keep_index_and_date_cols():
    df = pd.DataFrame(
        {
            'id': ['a', 'b'],
            'start_date': ['2023-01-01', '2023-01-02'],
            'end_date': ['2023-01-01 01:00:00', '2023-01-02 01:00:00'],
        }
    ).set_index('id')
    result = explode_date_range(
        df,
        'start_date',
        'end_date',
        freq='1h',
        drop_index=False,
        drop_date_cols=False,
    )
    assert 'id' in result.index.names
    assert 'start_date' in result.columns
    assert 'end_date' in result.columns
    assert len(result) == 4
