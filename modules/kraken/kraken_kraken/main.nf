process KRAKEN_KRAKEN {

    if (workflow.containerEngine == 'singularity') {
        container = params.kraken_singularity
    } else {
        container = params.kraken_docker
    }

    publishDir "${params.output}/kraken", mode: 'copy'

    input:
    path reads
    path db
    path reads_id

    output:
    path '*.kraken', emit: krakenOutputFile
    path '*.kraken.out', emit: krakenStdOutput

    script:
    """
    reads_id=\$(cat ${reads_id})
    echo \$reads_id > reads_id
    kraken2 --db ${db} --report \${reads_id}.kraken ${reads} --threads ${task.cpus} > \${reads_id}.kraken.out
    """
}
