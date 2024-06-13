process NANOSTAT {

    if (workflow.containerEngine == 'singularity') {
        container = params.nanostat_singularity
    } else {
        container = params.nanostat_docker
    }

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
