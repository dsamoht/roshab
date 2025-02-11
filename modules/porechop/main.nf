process PORECHOP {

    if (workflow.containerEngine == 'singularity') {
        container = params.porechop_singularity
    } else {
        container = params.porechop_docker
    }

    input:
    tuple val(reads_id), path(reads)

    output:
    tuple val(reads_id), path("*porechopped_reads.fastq.gz"), emit: porechopped_reads
    tuple val(reads_id), path("*porechop.log"), emit: log

    script:
    """
    porechop -i ${reads} -o ${reads_id}_porechopped_reads.fastq.gz > ${reads_id}_porechop.log
    """
}
