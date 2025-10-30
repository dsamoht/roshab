#!/usr/bin/env nextflow

include { ROSHAB_WF             } from './workflows/roshab_wf'

info = """
  ____           _   _    _    ____         ____ _     ___ 
 |  _ \\ ___  ___| | | |  / \\  | __ )       / ___| |   |_ _|
 | |_) / _ \\/ __| |_| | / _ \\ |  _ \\ _____| |   | |    | | 
 |  _ < (_) \\__ \\  _  |/ ___ \\| |_) |_____| |___| |___ | | 
 |_| \\_\\___/|___/_| |_/_/   \\_\\____/       \\____|_____|___|
                                                                                                                      

 Classification and quantification of ONT reads with Kraken2 and minimap2 with a focus on
 bloom-forming microorganisms.

     Github: https://github.com/dsamoht/roshab

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:

     nextflow run main.nf --exp [NAME] --input [PATH] --output [PATH]

Arguments:
    --exp [NAME] : name of the experiment
    --output [PATH] : path to output directory (will be created if non-existant) (default: `roshab_output`)
    --input [PATH] : path to a samplesheet (CSV) with the following columns:
                    sample_name,date,site,group,reads

Optional argument:
    --skip_qc : skip quality control step (`porechop_abi` and `chopper`)
    --help : print this help message
"""

log.info info

if( params.help ) {
    exit 0
}

if ( !params.input) {
    log.info "Error: input samplesheet not specified."
    exit 1
}

if ( !params.exp) {
    log.info "Error: experiment name not specified."
    exit 1
}

if ( !params.output) {
    log.info "Warning: output directory not specified. Using default: `roshab_output`"
    params.output = 'roshab_output'

}

workflow {

    ROSHAB_WF()

}
