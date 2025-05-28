#!/usr/bin/env python3
import os
import sys
import gzip
import shutil
from pathlib import Path


def find_fastq_files(directory, extensions):
    return sorted([
        str(f) for ext in extensions
        for f in Path(directory).rglob(f'*{ext}')
        if f.is_file()
    ])

def main(in_reads, sample_name):
    out_file = f"{sample_name}.fastq.gz"

    if os.path.isfile(in_reads):
        if in_reads.endswith('.gz'):
            os.symlink(in_reads, out_file)
        else:
            with open(in_reads, 'rb') as f_in, gzip.open(out_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    elif os.path.isdir(in_reads):
        compressed_exts = ['.fastq.gz', '.fq.gz']
        uncompressed_exts = ['.fastq', '.fq']

        compressed = find_fastq_files(in_reads, compressed_exts)
        uncompressed = find_fastq_files(in_reads, uncompressed_exts)

        if compressed and uncompressed:
            print("ERROR: Directory contains both compressed and uncompressed FASTQ files.", file=sys.stderr)
            sys.exit(1)
        elif compressed:
            with open(out_file, 'wb') as out_f:
                for fpath in compressed:
                    with open(fpath, 'rb') as in_f:
                        shutil.copyfileobj(in_f, out_f)
        elif uncompressed:
            with gzip.open(out_file, 'wb') as out_f:
                for fpath in uncompressed:
                    with open(fpath, 'rb') as in_f:
                        shutil.copyfileobj(in_f, out_f)
        else:
            print(f"ERROR: No FASTQ files found in directory '{in_reads}'.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"ERROR: '{in_reads}' is neither a file nor a directory.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: concat_reads.py <in_reads> <sample_name>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
