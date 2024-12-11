process KRAKEN {

    container workflow.containerEngine == 'singularity' ?
            params.kraken_singularity : params.kraken_docker

    publishDir "${params.output}/kraken", mode: 'copy'

    input:
    tuple val(reads_id), path(reads)
    path db

    output:
    tuple val(reads_id), path('*.kraken'), emit: kraken_report
    tuple val(reads_id), path('*.kraken.out'), emit: kraken_stdout

    script:
    """
    kraken2 --db ${db} --report ${reads_id}.kraken ${reads} --threads ${task.cpus} > ${reads_id}.kraken.out
    """

}
