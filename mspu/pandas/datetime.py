from typing import Literal

import pandas as pd


def explode_date_range(
    df: pd.DataFrame,
    start_date_col: str,
    end_date_col: str,
    date_col: str = 'ts',
    freq: str = '30min',
    start_date_offset: pd.DateOffset = None,
    end_date_offset: pd.DateOffset = None,
    start_date_roll: Literal['backward', 'forward'] | None = None,
    end_date_roll: Literal['backward', 'forward'] | None = None,
    min_date: str | pd.Timestamp = None,
    max_date: str | pd.Timestamp = None,
    inclusive: Literal['both', 'left', 'right', 'neither'] = 'both',
    drop_index: bool = True,
    drop_date_cols: bool = True,
) -> pd.DataFrame:
    """
    Explode DataFrame start/end date columns to date column.

    Parameters
    ----------
    df:
        The input DataFrame with start/end date columns/index levels.
    start_date_col:
        The column name in the DataFrame for the start date.
    end_date_col:
        The column name in the DataFrame for the end date.
    date_col:
        The column name in the DataFrame for the new date.
    freq:
        The frequency of the new date column.
    start_date_offset:
        The date offset for the start date column.
    end_date_offset:
        The date offset for the end date column.
    start_date_roll:
        Roll the start_date to the start of the current/next period.
    end_date_roll:
        Roll the end date to the start of the current/next period.
    min_date:
        The min value of the start date after offset.
    max_date:
        The max value of the end date after offset.
    inclusive:
        Include boundaries; Whether to set each bound as closed or open.
    drop_index:
        This flag should be False when the input DataFrame has meaningful index.
    drop_date_cols:
        Whether to drop the start_date_col and end_date_col or not.

    Returns
    -------
    pd.DataFrame
        The DataFrame same as the input but with
        start/end date columns replaced by the new date column

    Examples
    --------
    Simple usage.

    >>> df = pd.DataFrame({
    ...     'start_date': ['2023-01-01', '2023-01-02'],
    ...     'end_date': ['2023-01-01 01:00', '2023-01-02 02:00'],
    ... })
    >>> df_exploded = explode_date_range(df, 'start_date', 'end_date', freq='1h')
    >>> print(df_exploded)
                       ts
    0 2023-01-01 00:00:00
    1 2023-01-01 01:00:00
    2 2023-01-02 00:00:00
    3 2023-01-02 01:00:00
    4 2023-01-02 02:00:00

    With offset for start and end date.

    >>> df = pd.DataFrame({
    ...     'start_date': ['2023-01-01', '2023-01-02'],
    ...     'end_date': ['2023-01-01 01:00:00', '2023-01-02 02:00:00'],
    ... })
    >>> df_exploded = explode_date_range(
    ...     df=df,
    ...     start_date_col='start_date',
    ...     end_date_col='end_date',
    ...     freq='1h',
    ...     start_date_offset=pd.DateOffset(hours=1),
    ...     end_date_offset=pd.DateOffset(hours=-1),
    ... )
    >>> print(df_exploded)
                       ts
    0 2023-01-02 01:00:00

    With rolling start and end date to the nearest frequency (hour).

    >>> df = pd.DataFrame({
    ...     'start_date': ['2023-01-01 00:30', '2023-01-02 00:30'],
    ...     'end_date': ['2023-01-01 01:30', '2023-01-02 02:30'],
    ... })
    >>> df_exploded = explode_date_range(
    ...     df=df,
    ...     start_date_col='start_date',
    ...     end_date_col='end_date',
    ...     freq='1h',
    ...     start_date_roll='forward',
    ...     end_date_roll='backward',
    ... )
    >>> print(df_exploded)
                       ts
    0 2023-01-01 01:00:00
    1 2023-01-02 01:00:00
    2 2023-01-02 02:00:00
    """
    if not drop_index:
        levels_old = list(df.index.names)
        index_names = [
            f'_idx{i}' if name is None else name for i, name in enumerate(levels_old)
        ]
        df = df.rename_axis(index_names, axis=0)
        if start_date_col in df.columns and end_date_col in df.columns:
            levels = index_names
        else:
            if drop_date_cols:
                levels = [
                    level
                    for level in index_names
                    if level not in (start_date_col, end_date_col)
                ]
                levels_old = [
                    level
                    for level in levels_old
                    if level not in (start_date_col, end_date_col)
                ]
            else:
                levels = index_names
                # move start/end_date_col to index if one exists
                if start_date_col in df.columns:
                    levels += [start_date_col]
                    levels_old += [start_date_col]
                elif end_date_col in df.columns:
                    levels += [end_date_col]
                    levels_old += [end_date_col]
            levels += [date_col]
            levels_old += [date_col]

    df = df.reset_index(drop=drop_index)
    df[start_date_col] = pd.to_datetime(df[start_date_col])
    df[end_date_col] = pd.to_datetime(df[end_date_col])

    # offset start date
    if start_date_offset is not None:
        df[start_date_col] += start_date_offset

    # roll start date
    if start_date_roll is not None:
        roll_freq = freq if freq[-1] != 'S' else freq[:-1]
        extra_period = 0 if start_date_roll == 'backward' else 1
        df[start_date_col] = (
            df[start_date_col].dt.to_period(roll_freq) + extra_period
        ).dt.start_time

    # limit start_date and replace null with min_date
    if min_date is not None:
        min_date = pd.to_datetime(min_date)
        df[start_date_col] = (
            df[start_date_col]
            .fillna(min_date)
            .where(df[start_date_col] > min_date, min_date)
        )

    # offset end date
    if end_date_offset is not None:
        df[end_date_col] += end_date_offset

    # roll end date
    if end_date_roll is not None:
        roll_freq = freq if freq[-1] != 'S' else freq[:-1]
        extra_period = 0 if end_date_roll == 'backward' else 1
        df[end_date_col] = (
            df[end_date_col].dt.to_period(roll_freq) + extra_period
        ).dt.start_time

    # limit end_date and replace null with max_date
    if max_date is not None:
        max_date = pd.to_datetime(max_date)
        df[end_date_col] = (
            df[end_date_col]
            .fillna(max_date)
            .where(df[end_date_col] < max_date, max_date)
        )

    # inclusive parameter is supported since pandas 1.4
    inclusive_par = {'inclusive': inclusive}

    # if inclusive = 'left' we expect date_end is exclusive
    #   so records with start_date == end_date should be excluded
    # also reset index to ensure index start from 0 and is consecutive
    if inclusive == 'left':
        df = df.query(f'{start_date_col} < {end_date_col}').reset_index(drop=True)
    else:
        df = df.query(f'{start_date_col} <= {end_date_col}').reset_index(drop=True)

    # get exploded timestamp column
    if df.empty:
        dt = (
            pd.DataFrame(
                {
                    'i': pd.Series(dtype='int'),
                    date_col: pd.Series(dtype='datetime64[ns]'),
                }
            )
            .set_index('i')
            .rename_axis(None, axis=0)
        )
    else:
        dt = (
            pd.concat(
                [
                    pd.DataFrame(
                        {
                            'i': i,
                            date_col: pd.date_range(
                                start=s, end=e, freq=freq, **inclusive_par
                            ),
                        }
                    )
                    for i, (s, e) in enumerate(
                        zip(df[start_date_col], df[end_date_col])
                    )
                ]
            )
            .set_index('i')
            .rename_axis(None, axis=0)
        )

    # drop start_date_col and end_date_col
    if drop_date_cols:
        df = df.drop(columns=[start_date_col, end_date_col])

    # sample df based on new timestamp column
    df = df.reindex(dt.index)
    df[date_col] = dt[date_col]

    # set index
    if drop_index:
        df = df.reset_index(drop=True)
    else:
        df = df.set_index(levels).rename_axis(levels_old, axis=0)

    return df
