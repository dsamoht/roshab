process KRONA {

    container workflow.containerEngine == 'singularity' ?
        params.krona_singularity : params.krona_docker

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