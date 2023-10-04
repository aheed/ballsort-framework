# Ballsort-framework

Python framework for Ballsort 

## To build and upload package to PyPi

### prep
if needed:
```
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
```

### build
First update version info in **lib/pyproject.toml**. Then build.

```
cd lib
python3 -m build
```

### upload
```
python3 -m twine upload  dist/*
```

When prompted for credentials enter __token__ for username. Enter an API token as password. API tokens are created at https://pypi.org/, logged in as aheed.

see [https://packaging.python.org/en/latest/tutorials/packaging-projects/]



### todo
automate package publishing

use pytest for unit testing
