process NANOSTAT {

    container workflow.containerEngine == 'singularity' ?
        params.nanostat_singularity : params.nanostat_docker

    publishDir "${params.output}/nanostat", mode: 'copy'

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path('*.stats.tsv'), emit: tsv

    script:
    def sample_name = meta[0]
    """
    NanoStat -o . -n ${sample_name}.stats.tsv --tsv --fastq ${reads}
    """
}
