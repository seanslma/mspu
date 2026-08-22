# mspu

[![PyPI - Version](https://img.shields.io/pypi/v/mspu?color=blue)](https://pypi.org/project/mspu/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/mspu)](https://pypi.org/project/mspu/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## MSPU: Minimal Set of Python Utilities

**Lightweight utilities for pandas and Polars.**

The `mspu` package provides a collection of commonly used utilities for DataFrame testing, manipulation, and inspection.

It currently includes:

- `ht` — Display the head and tail of pandas and Polars DataFrames.
- `gen_rand_df` — Generate dummy pandas DataFrames for testing.
- `explode_date_range` — Efficiently expand date ranges in pandas DataFrames into rows.

## Installation

Using `pip`:
```bash
pip install mspu
```

Using `uv`:
```bash
uv pip install mspu
```

## Quick Start

Display the head and tail of a DataFrame simultaneously with some display settings.

Import `mspu.pandas` to register the `ht` accessor on pandas DataFrames.

```python
import pandas as pd
import mspu.pandas

df = pd.DataFrame({
  'foo': [1.12345, 2.98765, 3.14159],
  'bar': [7, 8, 9],
  'ham': ['x', 'y', 'z'],
})
# n: 1 - one row from the head and one row from the tail are displayed
# c: 2 - two columns are displayed
# r: 3 - the number of decimal places for number rounding
# w: -1 - unlimited display width
df.ht(n=1, c=2, r=3, w=-1)
```

The DataFrame will be displayed as:
```
shape: (3, 3)
     foo  ...  ham
0  1.123  ...    x
2  3.142  ...    z
```

## Documentation

See the [mspu documentation](https://seanslma.github.io/mspu) for more details.
