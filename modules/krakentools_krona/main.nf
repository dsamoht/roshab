process KRAKENTOOLS_KRONA {

    container workflow.containerEngine == 'singularity' ?
        params.krakentools_singularity : params.krakentools_docker

    publishDir "${params.output}/krona", mode: 'copy'

    input:
    tuple val(reads_id), path(kraken_report)

    output:
    tuple val(reads_id), path('*.krona.out'), emit: krakentools_to_krona

    script:
    """
    kreport2krona.py -r ${kraken_report} -o ${reads_id}.krona.out --no-intermediate-ranks
    """
}