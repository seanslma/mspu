import pandas as pd

from mspu.datetime import explode_date_range
from mspu.datetime.utils import explode_date_range as edr_utils


def test_datetime_reexport_matches_pandas():
    assert explode_date_range is edr_utils
    assert explode_date_range.__module__ == 'mspu.pandas.datetime'


def test_datetime_reexport_works():
    df = pd.DataFrame(
        {
            'start_date': ['2023-01-01', '2023-01-02'],
            'end_date': ['2023-01-01 01:00:00', '2023-01-02 02:00:00'],
        }
    )
    result = explode_date_range(df, 'start_date', 'end_date', freq='1h')
    assert len(result) == 5
    assert 'ts' in result.columns
