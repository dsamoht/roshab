#!/usr/bin/env python3
from glob import glob
import re
import sys


if ( sys.argv[1].endswith(".fastq.gz") or sys.argv[1].endswith(".fastq") ):
    _files = [sys.argv[1]]

else:
    _files = glob(f"{sys.argv[1]}/**/fastq_pass/**/*.fastq.gz", recursive=True)

_file_dict = {}
BARCODE_PATTERN = re.compile(r'barcode\d{2}')
EXPNAME = sys.argv[2]

for file in _files:
    match = BARCODE_PATTERN.search(file)
    if match:
        barcode_key = EXPNAME + "_" + match.group(0)
        if barcode_key not in _file_dict:
            _file_dict[barcode_key] = []
        _file_dict[barcode_key].append(file)
    else:
        if EXPNAME not in _file_dict:
            _file_dict[EXPNAME] = []
        _file_dict[EXPNAME].append(file)

for barcode, _files in _file_dict.items():
    with open(f"{barcode}.fastq.gz", "wb") as outfile:
        for fname in _files:
            with open(fname, "rb") as infile:
                for line in infile:
                    outfile.write(line)
