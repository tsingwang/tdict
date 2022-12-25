# TDict

Text dictionary for command line.

- English -> Chinese
- Chinese -> English
- Show hints if word is not found
- Support sentence translation
- Vocabulary book management
- A simple TUI app for learning word from vocabulary book daily

## Usage

```bash
➜  ~ td -h
usage: td [-h] [-l [LIST]] [-a ADD] [-d DELETE] [-s] [word]

positional arguments:
  word           The word to query.

options:
  -h, --help     show this help message and exit
  -l [LIST]      List words.
  -a ADD         Add word.
  -d DELETE      Delete word.
  -s, --summary  Summary by month.
```

If only `td`, it will launch TUI training app.

## Install

```bash
pip install git+https://github.com/tsingwang/tdict
# or
pip install git+ssh://git@github.com/tsingwang/tdict.git
```

## Build

```bash
python setup.py sdist
pip install dist/<pkg> --user
```
