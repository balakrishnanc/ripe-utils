# About

`list.py` is a Python script that retrieves the details of all RIPE Atlas probes.


## Dependencies

The script requires Python 3.x and the package `requests`.


## Usage

```
$ ./list.py -h
usage: list.py [-h] [--version] -o output

List all RIPE Atlas probes.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -o output, --output output
                        Relative/absolute path of output file.
```


## Example

```
$ ./list.py -o "atlas-probes-`date +%Y%m%d.txt`"
```
