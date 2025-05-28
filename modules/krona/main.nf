process KRONA {

    container workflow.containerEngine == 'singularity' ?
        params.krona_singularity : params.krona_docker

    publishDir "${params.output}/krona", mode: 'copy'

    input:
    tuple val(meta), path(krakentools_krona)

    output:
    tuple val(meta), path('*krona.html'), emit: html

    script:
    def sample_name = meta[0]
    """
    ktImportText ${krakentools_krona} -o ${sample_name}.krona.html
    """
}