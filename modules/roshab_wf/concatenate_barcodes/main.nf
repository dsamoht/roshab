process CONCATENATE_BARCODES {

    if (workflow.containerEngine == 'singularity') {
        container = params.python_singularity
    } else {
        container = params.python_docker
    }

    input:
    path input_dir

    output:
    path "*.fastq.gz", emit: barcodes

    script:
    """
    concatenate_barcode.py ${input_dir} ${params.exp}
    """
}
