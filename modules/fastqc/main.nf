process FASTQC {

    container workflow.containerEngine == 'singularity' ?
        params.fastqc_singularity : params.fastqc_docker

    publishDir "${params.output}/fastqc", mode: 'copy'

    input:
    tuple val(read_id), path(reads)

    output:
    tuple val(read_id), path("*.html"), emit: html
    tuple val(read_id), path("*.zip"), emit: zip

    script:
    """
    fastqc --memory 6000 ${reads}
    """
}
