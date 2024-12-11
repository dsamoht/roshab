process CONCATENATE_BARCODES {

    container workflow.containerEngine == 'singularity' ?
        params.python_singularity : params.python_docker
    
    input:
    path input_dir

    output:
    path "*.fastq.gz", emit: barcodes

    script:
    """
    concatenate_barcode.py ${input_dir} ${params.exp}
    """
}
