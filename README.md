# gofile-dl

```
usage: gofile-dl [-h] [--dry-run] [--flatten] [--output-dir <directory>] [--password <password>] [--token <token>] [--verbose] [--version] link [link ...]

positional arguments:
  link

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             Do not download anything.
  --flatten             Save all files in the same directory. Only used with --output-dir.
  --output-dir <directory>, -o <directory>
                        Directory in which to save files. Non-existent directories will be created.
  --password <password>, -p <password>
                        Password for password-protected files.
  --token <token>, -t <token>
                        Account token. If not specified, a guest account will be created.
  --verbose, -v         Increase output verbosity.
  --version             show program's version number and exit
```
