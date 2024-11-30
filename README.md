# TDict

Text dictionary for command line.

- English -> Chinese
- Chinese -> English
- Show hints if word is not found
- Support sentence translation
- Vocabulary book management
- A simple TUI app for learning word daily
  - Support word voice, disabled default
  - Support spell check, disabled default
- Word learning history graph, inspired from github person page

## Usage

```sh
➜  ~ td -h
usage: td [-h] [-u USER] [-l [LIST]] [-a ADD] [-d DELETE] [-s] [-y YEAR] [word]

positional arguments:
  word           The word to query.

options:
  -h, --help     show this help message and exit
  -u USER        Use the user account.
  -l [LIST]      List words.
  -a ADD         Add word.
  -d DELETE      Delete word.
  -s, --summary  Summary.
  -y YEAR        Depend on summary.
```

If only `td`, it will launch TUI training app.

## Install

```sh
pip install git+https://github.com/tsingwang/tdict
# or
pip install git+ssh://git@github.com/tsingwang/tdict.git
```

## Build

```sh
python setup.py sdist
pip install dist/*.tar.gz --user
```
