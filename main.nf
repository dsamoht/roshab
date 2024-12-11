#!/usr/bin/env nextflow

include { ROSHAB_WF             } from './workflows/roshab_wf'
include { SETUP_DOCKER_WF       } from './workflows/setup_docker_wf'
include { SETUP_SINGULARITY_WF  } from './workflows/setup_singularity_wf'


info = """
  ____           _   _    _    ____         ____ _     ___ 
 |  _ \\ ___  ___| | | |  / \\  | __ )       / ___| |   |_ _|
 | |_) / _ \\/ __| |_| | / _ \\ |  _ \\ _____| |   | |    | | 
 |  _ < (_) \\__ \\  _  |/ ___ \\| |_) |_____| |___| |___ | | 
 |_| \\_\\___/|___/_| |_/_/   \\_\\____/       \\____|_____|___|
                                                                                                                      

 Taxonomic classification of ONT reads with Kraken2 and minimap2 with a focus on
 bloom-forming microorganisms.

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
"""

log.info info

if( params.help ) {
    exit 0
}

if ( !params.setup ) {

if ( !params.exp) {
    log.info "Error: experiment name not specified."
    exit 1
}

if ( !params.reads) {
    log.info "Error: reads directory not specified."
    exit 1
}

if ( !params.output) {
    log.info "Error: output directory not specified."
    exit 1
}
}

workflow {

    if (params.setup) {
        if (workflow.containerEngine == "singularity") {
        SETUP_SINGULARITY_WF()
        }
        if (workflow.containerEngine == "docker") {
        SETUP_DOCKER_WF()
        }
    }
    else {
        ROSHAB_WF()
    }

}