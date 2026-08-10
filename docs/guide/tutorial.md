# Quick Tutorial: Using explode_date_range

This tutorial shows you how to use the `mspu.pandas.explode_date_range` function.

## 1. Install the package

First, ensure you have the `mspu` package installed:
```sh
pip install mspu
```

## 2. Displaying dataframe

When you print a pandas DataFrame, sometimes the default settings are not good enough so you need to adjust the display width, number of rows and columns. Here we provide a simple function for your convenience. Importing `mspu.pandas` registers the `.ht` accessor on `pd.DataFrame`:

```py
import pandas as pd
import mspu.pandas  # registers the .ht accessor
df = pd.DataFrame({
  'foo': [1.12345, 2.98765, 3.14159],
  'bar': [7, 8, 9],
  'ham': ['x', 'y', 'z'],
})
df.ht(n=1, c=2, r=3)
```

The output:
```
shape: (3, 3)
     foo  ...  ham
0  1.123  ...    x
2  3.142  ...    z
```

## 3. Creating random data

The `gen_rand_df` can be used to create random data in a pandas DataFrame for testing.

In this example, we'll create a dataframe with one string column, two timestamp columns, one integer column, and two float columns, for one year with a resolution of one minute.

```py
from mspu.data import gen_rand_df

df = gen_rand_df(
    nrow=100,
    str_cols=1,
    ts_cols={
        'count': 2,
        'name': ['start_date', 'end_date'],
        'start_date': ['2020-01-01', '2023-01-01'],
        'end_date': ['2023-01-01', '2025-01-01'],
        'freq': 'MS',
        'random': True,
    },
    int_cols=1,
    float_cols=2,
)
df.ht(1, c=-1, r=2)
```
Outputs:
```
shape: (100, 6)
       s1 start_date   end_date  i1    f1    f2
0   IZD8v 2022-10-01 2023-12-01   0  1.43  1.78
99  y5HeH 2020-12-01 2024-07-01   0  1.13  1.11

```

## 4. Using the `explode_date_range` function

This function can be used to explode two datetime columns in a pandas DataFrame to a list of datetime values as a new column. It's about `30x` faster than using the pandas `df.explode` function.
```py
import time
from mspu.pandas import explode_date_range

# assume we already created the df in the previous section
t0 = time.time()
df_exploded = explode_date_range(
    df=df,
    start_date_col='start_date',
    end_date_col='end_date',
    date_col='ts',
    freq='30min',
    inclusive='left',
    drop_date_cols=True,
)
print(f'mspu explode time: {time.time() - t0:.3f} seconds')
df_exploded.ht(2,r=2)
```
Outputs:
```
mspu explode time: 0.235 seconds
shape: (4415424, 5)
            s1  i1    f1    f2                  ts
0        IZD8v   0  1.43  1.78 2022-10-01 00:00:00
1        IZD8v   0  1.43  1.78 2022-10-01 00:30:00
4415422  y5HeH   0  1.13  1.11 2024-06-30 23:00:00
4415423  y5HeH   0  1.13  1.11 2024-06-30 23:30:00
```

Now let's use `explode` from pandas:
```py
t1 = time.time()
df['ts'] = [
    pd.date_range(start, end, freq='30min', inclusive='left')
    for start, end in zip(df['start_date'].values, df['end_date'].values)
]
df_exploded_pandas = df.drop(columns=['start_date', 'end_date']).explode('ts')
print(f'pandas explode time: {time.time() - t1:.3f} seconds')
print(df_exploded.equals(df_exploded_pandas.reset_index(drop=True)))
```
Outputs:
```
pandas explode time: 4.117 seconds
True
```
