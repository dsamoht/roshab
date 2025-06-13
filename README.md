[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A523.04.0-23aa62.svg)](https://www.nextflow.io/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)

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
```
# Installation
### Dependencies

- [Nextflow](https://www.nextflow.io/)  
- [Docker](https://www.docker.com/)
- Pre-built [Kraken2 database](https://benlangmead.github.io/aws-indexes/k2)
- RosHAB-specific databases:
  - [BGC_cyanotoxins_plus_orthologs.fna](https://zenodo.org/records/15659134/files/BGC_cyanotoxins_plus_orthologs.fna) : Cyanotoxin-related biosynthetic gene clusters + orthologs
  - [cyanobacteriota_ncbi_dRep_n220](https://zenodo.org/records/15659134/files/cyanobacteriota_ncbi_dRep_n220.tar.gz) : Dereplicated Cyanobacteriota genomes from NCBI

- __Edit__ *nextflow.config* :  
  ```  
  kraken_db = '/absolute/path/to/extracted/kraken2/database'
  coverm_ncbi_db = '/absolute/path/to/extracted/cyanobacteriota_ncbi_dRep_n220'
  minimap_gene_db = '/absolute/path/to/BGC_cyanotoxins_plus_orthologs.fna'
  ```
### Run the pipeline
> *__Note__* : the first execution will download container images for future use
```
nextflow run main.nf -profile setup
```

### To run on your data
```
nextflow run main.nf --help
```
