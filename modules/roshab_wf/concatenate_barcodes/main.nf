process CONCATENATE_BARCODES {

    //if (workflow.containerEngine == 'singularity') {
    //    container = params.python_singularity
    //} else {
    //    container = params.python_docker
    //}

    output:
    path "*.fastq.gz", emit: barcodes

    script:
    """
    python $projectDir/bin/concatenate_barcode.py ${params.reads} ${params.exp}
    """
}
