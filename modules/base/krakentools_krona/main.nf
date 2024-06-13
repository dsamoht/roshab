process KRAKENTOOLS_KRONA {

    if (workflow.containerEngine == 'singularity') {
        container = params.krakentools_singularity
    } else {
        container = params.krakentools_docker
    }

    publishDir "${params.output}/krona", mode: 'copy'

    input:
    tuple val(reads_id), path(bracken_output)

    output:
    tuple val(reads_id), path('*.krona.out'), emit: krakentools_to_krona

    script:
    """
    kreport2krona.py -r ${bracken_output} -o ${reads_id}.krona.out --no-intermediate-ranks
    """
}