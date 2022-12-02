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
usage: td [-h] [-l] [-a] [-d] [word]

positional arguments:
  word          The word to query.

options:
  -h, --help    show this help message and exit
  -l, --list    List words.
  -a, --add     Add word.
  -d, --delete  Delete word.
```

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
