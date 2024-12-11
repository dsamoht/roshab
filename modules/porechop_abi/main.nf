process PORECHOP_ABI {

    container workflow.containerEngine == 'singularity' ?
        params.porechop_abi_singularity : params.porechop_abi_docker

    publishDir "${params.output}/porechop_abi", mode: 'copy'

    input:
    tuple val(reads_id), path(reads)

    output:
    tuple val(reads_id), path('porechopped_reads.fastq.gz'), emit: porechopped_reads

    script:
    """
    porechop_abi --ab_initio -t ${task.cpus} -i ${reads} -o porechopped_reads.fastq.gz
    """
}
