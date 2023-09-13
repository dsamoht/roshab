# RosHAB: Rapid on-site detection of Harmful Algal Blooms
## Introduction
### Dependencies

- [Nextflow](https://www.nextflow.io/)  
- [Docker](https://www.docker.com/)

### Pull the docker image
```
docker pull dsamoht/roshab-dev
```
### Launch the pipeline on raw reads
```
nextflow run roshab-wf.nf --raw_reads /path/to/raw-reads.fastq.fz
```