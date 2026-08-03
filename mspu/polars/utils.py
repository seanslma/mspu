import polars as pl
import polars.selectors as cs
from typing import Literal


@pl.api.register_dataframe_namespace('ht')
class PlHt:
    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def __call__(
        self,
        n: int = 2,
        c: int = None,
        w: int = None,
        r: int = None,
    ) -> None:
        """
        Polars head and tail in one command, with optional rounding.

        Parameters
        ----------
        n : int
            Number of rows to show from the head and tail. If n < 0 or n is greater than
            half the number of rows, the entire DataFrame will be shown.
        c : int
            Number of columns to show. If None or greater than the number of columns,
            all columns will be shown.
        w : int
            Width of the output in characters. If None, the width will be determined.
        r : int
            Number of decimal places to round float and decimal columns. If None or negative,
            no rounding will be applied.

        Returns
        -------
        None

        Examples
        --------
        >>> import polars as pl
        >>> import mspu.polars # registry ht
        >>> df = pl.DataFrame({
        ...   'foo': [1.12345, 2.98765, 3.14159],
        ...   'bar': [7, 8, 9],
        ...   'ham': ['x', 'y', 'z'],
        ... })
        >>> df.ht(n=1, c=2, r=2)
        shape: (3, 3)
        ┌──────┬───┬─────┐
        │ foo  ┆ … ┆ ham │
        │ ---  ┆   ┆ --- │
        │ f64  ┆   ┆ str │
        ╞══════╪═══╪═════╡
        │ 1.12 ┆ … ┆ x   │
        │ 3.14 ┆ … ┆ z   │
        └──────┴───┴─────┘
        """
        if n < 0 or self._df.shape[0] < 2 * n:
            df = self._df
        else:
            df = pl.concat([self._df[:n], self._df[-n:]])
        if r is not None and r >= 0:
            df = df.with_columns((cs.float() | cs.decimal()).round(r))
        with pl.Config(
            tbl_hide_dataframe_shape=True,
            tbl_width_chars=w,
            tbl_rows=df.shape[0],
            tbl_cols=c,
        ):
            print(f'shape: {self._df.shape}')
            print(df)


def parquet_to_csv(filepath: str):
    """
    Read parquet and save as csv.
    """
    filepath_csv = f'{filepath[:-7]}csv'
    pl.read_parquet(filepath).write_csv(filepath_csv)


def lowercase_polars_df(
    df: pl.DataFrame,
    lowercase: Literal['header', 'columns', 'both'] = 'both',
) -> pl.DataFrame:
    """
    Converts all column names and string columns to lowercase.
    """
    # Lowercase column headers
    if lowercase in ('header', 'both'):
        df = df.rename({col: col.lower() for col in df.columns})
    # Lowercase string columns
    if lowercase in ('columns', 'both'):
        df = df.with_columns([cs.string().str.to_lowercase()])
    return df


def to_float32_polars_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Convert all numerical columns type to float32.
    """
    df = df.with_columns((cs.float() | cs.decimal()).cast(pl.Float32))
    return df


def inf_count(df: pl.DataFrame) -> pl.DataFrame:
    """
    Counts the number of infinite values in each column of a Polars DataFrame.

    Returns a new DataFrame with the column names and their corresponding counts,
    sorted in descending order.
    """
    df_inf = (
        df.select([(pl.col(col).is_infinite().sum().alias(col)) for col in df.columns])
        .unpivot(variable_name='col', value_name='inf_cnt')
        .filter(pl.col('inf_cnt') > 0)
        .sort('inf_cnt', descending=True)
    )
    return df_inf


def nan_count(df: pl.DataFrame) -> pl.DataFrame:
    """
    Counts the number of NaN values in each column of a Polars DataFrame.

    Returns a new DataFrame with the column names and their corresponding counts,
    sorted in descending order.
    """
    df_nan = (
        df.select([(pl.col(col).is_nan().sum().alias(col)) for col in df.columns])
        .unpivot(variable_name='col', value_name='nan_cnt')
        .filter(pl.col('nan_cnt') > 0)
        .sort('nan_cnt', descending=True)
    )
    return df_nan


def nul_count(df: pl.DataFrame) -> pl.DataFrame:
    """
    Counts the number of null values in each column of a Polars DataFrame.

    Returns a new DataFrame with the column names and their corresponding counts,
    sorted in descending order.
    """
    df_nul = (
        df.select([(pl.col(col).is_null().sum().alias(col)) for col in df.columns])
        .unpivot(variable_name='col', value_name='nul_cnt')
        .filter(pl.col('nul_cnt') > 0)
        .sort('nul_cnt', descending=True)
    )
    return df_nul
