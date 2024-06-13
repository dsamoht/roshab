process KRONA {

    if (workflow.containerEngine == 'singularity') {
        container = params.krona_singularity
    } else {
        container = params.krona_docker
    }

    publishDir "${params.output}/krona", mode: 'copy'

    input:
    tuple val(reads_id), path(krakentools_krona)

    output:
    tuple val(reads_id), path('*krona.html'), emit: html

    script:
    """
    ktImportText ${krakentools_krona} -o ${reads_id}.krona.html
    """
}