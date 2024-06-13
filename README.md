# Taxonomic classification of ONT reads with Kraken2
## Introduction

```
  ____           _   _    _    ____      _____           _ 
 |  _ \ ___  ___| | | |  / \  | __ )    |_   _|__   ___ | |
 | |_) / _ \/ __| |_| | / _ \ |  _ \ _____| |/ _ \ / _ \| |
 |  _ < (_) \__ \  _  |/ ___ \| |_) |_____| | (_) | (_) | |
 |_| \_\___/|___/_| |_/_/   \_\____/      |_|\___/ \___/|_|
                                                           

 Taxonomic classification of ONT reads with Kraken2.
 2 modes:
        - normal : run the pipeline on already existing files
        - live (not supported yet) : run the pipeline during sequencing on newly generated files
     
     Github: https://github.com/dsamoht/roshab-wf
     Version: still no release

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:

     nextflow run roshab-wf.nf -profile local,docker --exp [NAME] --reads [PATH] --output [PATH]

Arguments:
     --exp [NAME] : name of the experiment
     --output [PATH] : path to output directory (will be created if non-existant)
     --reads [PATH] : path to the reads file

Optional arguments:
     --live : to run the "live" workflow
"""
```
### Dependencies

- [Nextflow](https://www.nextflow.io/)  
- [Docker](https://www.docker.com/)
- A pre-built [Kraken2 database](https://benlangmead.github.io/aws-indexes/k2)

- __Edit__ *nextflow.config* :  
  ```  
  kraken_db = '/path/to/extracted/kraken2/database/directory'
  ```
