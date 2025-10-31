[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)

### Introduction
A dashboard made to launch genomic pipelines from raw sequencing data.
This project was developed during the RosHAB project.

The dashboard now integrates the RosHAB-CLI pipeline, made to assign taxonomy to reads
and count cyanotoxin-related genes. This software is primarly made to be used with Nanopore
reads.

```
  ____           _   _    _    ____         ____ _     ___ 
 |  _  \___  ___| | | |  / \  | __ )       / ___| |   |_ _|
 | |_) / _ \/ __| |_| | / _ \ |  _ \ _____| |   | |    | | 
 |  _ < (_) \__ \  _  |/ ___ \| |_) |_____| |___| |___ | | 
 |_| \_\___/|___/_| |_/_/   \_\____/       \____|_____|___|


 Classification and quantification of ONT reads with Kraken2 and minimap2 with a focus on
 bloom-forming microorganisms.

     Github: https://github.com/dsamoht/roshab

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```
### Dependency
- Linux or macOS
- [Docker](https://www.docker.com/)

> [!NOTE]    
> RosHAB-CLI is a Nextflow pipeline that can be used as is - without the dashboard wrapper.  
> Its dependencies are all listed in [environment.yaml](environment.yaml).  
> See ```nextflow run main.nf --help``` for further informations.
 
### Installation
```
git clone https://github.com/dsamoht/roshab && cd ./roshab && ./install.sh
```
### Run the application
```
genomic-dashboard
```
