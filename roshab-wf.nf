#!/usr/bin/env nextflow

include { ROSHAB_WF      } from './workflows/roshab_wf'
include { ROSHAB_LIVE_WF } from './workflows/roshab_live_wf'


info = """
  ____           _   _    _    ____      _____           _ 
 |  _ \\ ___  ___| | | |  / \\  | __ )    |_   _|__   ___ | |
 | |_) / _ \\/ __| |_| | / _ \\ |  _ \\ _____| |/ _ \\ / _ \\| |
 |  _ < (_) \\__ \\  _  |/ ___ \\| |_) |_____| | (_) | (_) | |
 |_| \\_\\___/|___/_| |_/_/   \\_\\____/      |_|\\___/ \\___/|_|
                                                           

 Taxonomic classification of ONT reads with Kraken2.
 2 modes:
        - normal : run the pipeline on already existing files
        - live (not supported yet): run the pipeline during sequencing on newly generated files
     
     Github: https://github.com/dsamoht/roshab-wf
     Version: still no release

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:

     nextflow run roshab-wf.nf -profile local,docker --exp [NAME] --reads [PATH] --output [PATH]

Arguments:
     --exp [NAME] : name of the experiment
     --output [PATH] : path to output directory (will be created if non-existant)
     --reads [PATH] : path to a single file or to a directory of files
                      (if directory, the subfolder `fastq_pass` will be used)

Optional arguments:
     --live : to run the "live" workflow
"""

log.info info

if( params.help ) {

log.info info
    exit 0
}

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


workflow {

    if (params.live) {

        ROSHAB_LIVE_WF()

    } else {

        ROSHAB_WF()

    }

}
