# gofile-dl

## Features
- Download files and folders (including nested items) from Gofile.
- Even works with "overloaded" content.

## Installation
### via [`pipx`](https://packaging.python.org/guides/installing-stand-alone-command-line-tools/) (recommended)
```
pipx install gofile-dl
```

### via [`pip`](https://pip.pypa.io/en/stable/installation/)
```
pip install --user gofile-dl
```

## Usage
```
$ gofile-dl -h
usage: gofile-dl [-h] [--input-file <file>] [--output-dir <directory>] [--flatten] [--password <password>] [--token <token>] [--dry-run] [--verbose] [--version]
                 [link ...]

positional arguments:
  link                  link to content to download (passing multiple links is supported)

options:
  -h, --help            show this help message and exit
  --input-file <file>, -i <file>
                        file containing Gofile links
  --output-dir <directory>, -o <directory>
                        directory in which to save downloaded files
  --flatten             save all files in the same directory
  --password <password>, -p <password>
                        password of password-protected files
  --token <token>, -t <token>
                        Gofile account token (guest account will be used if omitted)
  --dry-run, --simulate
                        build the download target list but do not download anything
  --verbose, -v         increase output verbosity
  --version             show program's version number and exit
```
