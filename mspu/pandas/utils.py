import datetime

import pandas as pd


@pd.api.extensions.register_dataframe_accessor('ht')
class PdHt:
    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj

    def __call__(
        self,
        n: int = 2,
        c: int = None,
        w: int = -1,
        cw: int = None,
        r: int = None,
    ) -> None:
        """
        Pandas head and tail in one command, with optional rounding.

        Parameters
        ----------
        n : int
            Number of rows to show from the head and tail. If n < 0 or n is greater than
            half the number of rows, the entire DataFrame will be shown.
        c : int
            Number of columns to show. If None or greater than the number of columns,
            all columns will be shown.
        w : int
            Display width in characters. If None, pandas default is used.
        cw : int
            Column width in characters. If None, pandas default is used.
        r : int
            Number of decimal places to round float columns. If None or negative,
            no rounding will be applied.

        Returns
        -------
        None

        Examples
        --------
        >>> import pandas as pd
        >>> import mspu.pandas # registry ht
        >>> df = pd.DataFrame({
        ...     'foo': [1.12345, 2.98765, 3.14159],
        ...     'bar': [7, 8, 9],
        ...     'ham': ['x', 'y', 'z'],
        ... })
        >>> df.ht(n=1, c=2, r=2)
        shape: (3, 3)
            foo  ...  ham
        0  1.12  ...    x
        2  3.14  ...    z
        """
        # Columns to show
        if isinstance(c, int) and c <= 0:
            c = None

        # Display width
        if isinstance(w, int) and w <= 0:
            w = 1000

        # Slice head + tail (or full df)
        if n < 0 or self._obj.shape[0] <= 2 * n:
            df = self._obj
        else:
            df = pd.concat([self._obj.iloc[:n], self._obj.iloc[-n:]])

        # Round float columns
        if r is not None and r >= 0:
            float_cols = df.select_dtypes(include='float').columns
            df[float_cols] = df[float_cols].round(r)

        with pd.option_context(
            'display.show_dimensions',
            False,
            'display.width',
            w,
            'display.max_rows',
            df.shape[0],
            'display.max_columns',
            c,
            'display.max_colwidth',
            cw,
        ):
            print(f'shape: {self._obj.shape}')
            print(df)


def create_empty_df(
    col_types: dict[str, str],
    ind_types: dict[str, str] = None,
) -> pd.DataFrame:
    """
    Create an empty df with specified index and column types
    col_types: column name and type
    ind_types: index level name and type
    """
    if ind_types is None:
        ind_types = {}
    df = pd.DataFrame({
        key: pd.Series(dtype=value)
        for key, value in {**ind_types, **col_types}.items()
    })
    if ind_types:
        df = df.set_index(list(ind_types.keys()))
    return df


def explode_int_range(df, col, start_col, end_col, step=1):
    if df.empty:
        dt = create_empty_df({
            'i': 'int',
            'v': 'int',
        })
    else:
        dt = pd.concat([
            pd.DataFrame({'i': i, 'v': range(start, end + 1, step)})
            for i, (start, end) in enumerate(zip(df[start_col], df[end_col]))
        ])
    dt = dt.set_index('i').rename_axis(None, axis=0)
    df = df.reindex(dt.index).assign(**{col: dt.v})
    return df


def remove_cols_utc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts datetime columns in UTC to timezone-naive (tz=None).

    Only columns whose timezone offset is exactly UTC are converted, so
    columns with fixed offsets like ``+02:00`` are left untouched.
    """
    for col in df.select_dtypes(include=['datetimetz']).columns:
        tz = df[col].dt.tz
        if tz is not None and tz.utcoffset(None) == datetime.timedelta(0):
            df[col] = df[col].dt.tz_localize(None)
    return df


def df_diffs(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    left_suffix: str = '_df1',
    right_suffix: str = '_df2',
) -> pd.DataFrame:
    """
    Get rows in two dfs that are different to each other.

    Comparison is based on df MultiIndex.

    Parameters
    ----------
    df1 : pd.DataFrame
        First DataFrame to compare.
    df2 : pd.DataFrame
        Second DataFrame to compare.
    left_suffix : str
        Suffix to append to column names from df1 in the output DataFrame.
    right_suffix : str
        Suffix to append to column names from df2 in the output DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame containing rows that are different between df1 and df2, with suffixes
        indicating the source of each column.

    Examples
    --------
    >>> import pandas as pd
    >>> from mspu.pandas import df_diffs
    >>> df1 = pd.DataFrame({
    ...     'fruit': ['apple', 'banana', 'apple'],
    ...     'id': [1, 2, 4],
    ...     'store': ['us', 'uk', 'cn'],
    ...     'price': [4, 3.1, 2.5],
    ... }).set_index(['fruit', 'id'])
    >>> print(df1)
            store  price
    fruit  id
    apple  1     us    4.0
    banana 2     uk    3.1
    apple  4     cn    2.5
    >>> df2 = pd.DataFrame({
    ...     'fruit': ['apple', 'banana', 'apple'],
    ...     'id': [1, 3, 4],
    ...     'store': ['us', 'uk', 'cn'],
    ...     'price': [4, 3.2, 2.5],
    ... }).set_index(['fruit', 'id'])
    >>> print(df2)
            store  price
    fruit  id
    apple  1     us    4.0
    banana 3     uk    3.2
    apple  4     cn    2.5
    >>> diff = df_diffs(df1, df2)
    >>> print(diff)
              store_df1  price_df1 store_df2  price_df2
    fruit  id
    banana 2         uk        3.1       NaN        NaN
           3        NaN        NaN        uk        3.2
    """
    # Perform an outer join
    df_joined = pd.merge(
        df1,
        df2,
        how='outer',
        left_index=True,
        right_index=True,
        suffixes=(left_suffix, right_suffix),
    )

    # Compare the columns to find differences
    d1_joined = df_joined.filter(like=left_suffix).rename(
        columns=lambda x: x.rsplit('_', 1)[0]
    )
    d2_joined = df_joined.filter(like=right_suffix).rename(
        columns=lambda x: x.rsplit('_', 1)[0]
    )

    # Compare two dfs with `ne`, col names must be the same
    diffs = df_joined[d1_joined.ne(d2_joined).any(axis=1)]

    return diffs


if __name__ == '__main__':
    # Create two example DataFrames with string columns
    df1 = pd.DataFrame(
        {
            'fruit': ['apple', 'banana', 'apple'],
            'id': [1, 2, 4],
            'store': ['us', 'uk', 'cn'],
            'price': [4, 3.1, 2.5],
        }
    ).set_index(['fruit', 'id'])

    df2 = pd.DataFrame(
        {
            'fruit': ['apple', 'banana', 'apple'],
            'id': [1, 3, 4],
            'store': ['us', 'uk', 'cn'],
            'price': [4, 3.2, 2.5],
        }
    ).set_index(['fruit', 'id'])

    df = df_diffs(df1, df2)

    # Show the resulting differences
    print(df)
