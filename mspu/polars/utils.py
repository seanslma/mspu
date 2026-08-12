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
        w: int = -1,
        cw: int = None,
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
        cw : int
            Column width in characters. If None, the column width will be determined.
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
            fmt_str_lengths=cw,
        ):
            print(f'shape: {self._df.shape}')
            print(df)


def parquet_to_csv(filepath: str) -> str:
    """
    Read parquet and save as csv.

    The output path is the input path with its extension replaced by ``.csv``,
    so both ``.parquet`` and shorter variants like ``.pq`` work correctly.

    Parameters
    ----------
    filepath : str
        Path to the input parquet file.

    Returns
    -------
    str
        Path to the written csv file.
    """
    filepath_csv = filepath.rsplit('.', 1)[0] + '.csv'
    pl.read_parquet(filepath).write_csv(filepath_csv)
    return filepath_csv


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
    df = df.with_columns(cs.numeric().cast(pl.Float32))
    return df


def _count_vals(df: pl.DataFrame, method: str, out_col: str) -> pl.DataFrame:
    """
    Count special values (infinite, NaN) in numeric columns of a DataFrame.

    Non-numeric columns are skipped because ``is_infinite``/``is_nan`` are only
    supported on float/decimal columns.
    """
    numeric_cols = [
        col
        for col in df.columns
        if df.schema[col].is_float() or df.schema[col].is_decimal()
    ]
    if not numeric_cols:
        return pl.DataFrame(schema={'col': pl.String, out_col: pl.UInt32})
    df_counts = (
        df.select(
            [getattr(pl.col(col), method)().sum().alias(col) for col in numeric_cols]
        )
        .unpivot(variable_name='col', value_name=out_col)
        .filter(pl.col(out_col) > 0)
        .sort(out_col, descending=True)
    )
    return df_counts


def inf_count(df: pl.DataFrame) -> pl.DataFrame:
    """
    Counts the number of infinite values in each numeric column of a Polars DataFrame.

    Non-numeric columns are ignored. Returns a new DataFrame with the column names
    and their corresponding counts, sorted in descending order.
    """
    return _count_vals(df, 'is_infinite', 'inf_cnt')


def nan_count(df: pl.DataFrame) -> pl.DataFrame:
    """
    Counts the number of NaN values in each numeric column of a Polars DataFrame.

    Non-numeric columns are ignored. Returns a new DataFrame with the column names
    and their corresponding counts, sorted in descending order.
    """
    return _count_vals(df, 'is_nan', 'nan_cnt')


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
