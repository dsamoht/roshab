process KRAKEN {

    publishDir "${params.output}/kraken", mode: 'copy'

    input:
    tuple val(meta), path(reads)
    path db

    output:
    tuple val(meta), path('*.kraken'), emit: kraken_report
    tuple val(meta), path('*.kraken.out'), emit: kraken_stdout

    script:
    def sample_name = meta[0]
    """
    kraken2 --db ${db} --report ${sample_name}.kraken ${reads} --threads ${task.cpus} > ${sample_name}.kraken.out
    """

}
