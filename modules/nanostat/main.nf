process NANOSTAT {

    container workflow.containerEngine == 'singularity' ?
        params.nanostat_singularity : params.nanostat_docker

    publishDir "${params.output}/nanostat", mode: 'copy'

    input:
    tuple val(reads_id), path(reads)

    output:
    tuple val(reads_id), path('*.stats.tsv'), emit: tsv

    script:
    """
    NanoStat -o . -n ${reads_id}.stats.tsv --tsv --fastq ${reads}
    """
}
