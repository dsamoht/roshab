#!/usr/bin/env python3
import argparse
import gzip
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description="Concatenate FASTQ files from a file or directory.")
parser.add_argument('--fastq', nargs='+', help='fastq file(s) or directories containing them')
parser.add_argument('--output', help='concatenated output fastq.gz file')

def concatenate_reads(input_path_list, output_file):
    fastq_files = []
    exts = ['*.fastq', '*.fq', '*.fastq.gz', '*.fq.gz']

    for path in input_path_list:
        p = Path(path)
        if p.is_file():
            fastq_files.append(p)
        elif p.is_dir():
            for ext in exts:
                fastq_files.extend(p.rglob(ext))

    if not fastq_files:
        raise FileNotFoundError("No FASTQ files found in input path(s): " + ", ".join(input_path_list))

    with gzip.open(output_file, 'wb') as out_f:
        for fastq_file in fastq_files:
            open_func = gzip.open if fastq_file.suffix == '.gz' else open
            with open_func(fastq_file, 'rb') as in_f:
                shutil.copyfileobj(in_f, out_f)

if __name__ == "__main__":
    args = parser.parse_args()
    Path("OUT").mkdir(exist_ok=True)
    concatenate_reads(args.fastq, Path("OUT").joinpath(args.output))
