# Taxonomic classification of ONT reads with Kraken2
## Introduction

```
  ____           _   _    _    ____         ____ _     ___ 
 |  _  \___  ___| | | |  / \  | __ )       / ___| |   |_ _|
 | |_) / _ \/ __| |_| | / _ \ |  _ \ _____| |   | |    | | 
 |  _ < (_) \__ \  _  |/ ___ \| |_) |_____| |___| |___ | | 
 |_| \_\___/|___/_| |_/_/   \_\____/       \____|_____|___|


 Taxonomic classification of ONT reads with Kraken2 and minimap2
 with a focus on bloom-forming microorganisms.

     Github: https://github.com/dsamoht/roshab-wf

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:

     nextflow run main.nf --exp [NAME] --reads [PATH] --output [PATH]

Arguments:
     --exp [NAME] : name of the experiment
     --output [PATH] : path to output directory (will be created if non-existant)
     --reads [PATH] : path to a single file or to a directory of files
                      (if directory, the subfolder `fastq_pass` will be used)

Optional argument:
    -profile singularity : use Singularity as the container engine instead of the default (Docker)
```
### Dependencies

- [Nextflow](https://www.nextflow.io/)  
- [Docker](https://www.docker.com/)
- A pre-built [Kraken2 database](https://benlangmead.github.io/aws-indexes/k2)

- __Edit__ *nextflow.config* :  
  ```  
  kraken_db = '/path/to/extracted/kraken2/database/directory'
  ```
