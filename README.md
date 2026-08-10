# mspu

Ma's python utils (`mspu`) package. It currently includes some commonly used functions, like `gen_rand_df` (creating dummy pandas dataframes for testing) and `explode_date_range` (exploding date ranges with high performance), as well as `ht` (displaying both pandas and polars dataframe head and tail).

## How to install `mspu`

Using `pip`:
```sh
pip install mspu
```

Using `uv`:
```sh
uv pip install mspu
```

## Features

### Random data generation (`mspu.data`)

Create reproducible dummy dataframes for testing:

```python
from mspu.data import gen_rand_df
import mspu.pandas  # registers the .ht accessor

df = gen_rand_df(
    nrow=100,
    str_cols=1,
    ts_cols=2,
    int_cols=1,
    float_cols=2,
)
df.ht()
```

### Head and tail in one command (`mspu.pandas.ht`, `mspu.polars.ht`)

Show head and tail of a dataframe at once, with optional rounding:

```python
import pandas as pd
import mspu.pandas  # registers the .ht accessor

df = pd.DataFrame({'foo': [1.12345, 2.98765, 3.14159], 'bar': [7, 8, 9]})
df.ht(n=1, c=2, r=2)
```

The same works for polars dataframes after `import mspu.polars`.

### Exploding date ranges (`mspu.pandas.explode_date_range`)

Explode start/end date columns into a dense timestamp column — about `30x` faster than `df.explode` for large frames:

```python
import pandas as pd
from mspu.pandas import explode_date_range

df = pd.DataFrame({
    'start_date': ['2023-01-01', '2023-01-02'],
    'end_date': ['2023-01-01 01:00:00', '2023-01-02 02:00:00'],
})
df_exploded = explode_date_range(df, 'start_date', 'end_date', freq='1h')
```

### File I/O helpers (`mspu.io`)

Convenience wrappers for reading and writing text and JSON files:

```python
from mspu.io import read_json, write_json, read_text, write_text

write_json('config.json', {'mode': 'fast'}, mkdir=True)
config = read_json('config.json')
```

### Encryption utilities (`mspu.security`)

Fernet-based key management and file/text encryption:

```python
from mspu.security import create_key, load_key, encrypt_file, decrypt_file

create_key('my-key.key')
key = load_key('my-key.key')
encrypt_file(key, 'credentials.json')   # writes credentials_.json
db_cred = decrypt_file(key, 'credentials_.json')
```

## The document for `mspu`

Visit the [document](https://seanslma.github.io/mspu) for more details.
