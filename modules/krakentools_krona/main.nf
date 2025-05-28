process KRAKENTOOLS_KRONA {

    container workflow.containerEngine == 'singularity' ?
        params.krakentools_singularity : params.krakentools_docker

    publishDir "${params.output}/krona", mode: 'copy'

    input:
    tuple val(meta), path(kraken_report)

    output:
    tuple val(meta), path('*.krona.out'), emit: krakentools_to_krona

    script:
    def sample_name = meta[0]
    """
    kreport2krona.py -r ${kraken_report} -o ${sample_name}.krona.out --no-intermediate-ranks
    """
}