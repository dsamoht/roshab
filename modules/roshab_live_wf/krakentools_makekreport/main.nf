process KRAKENTOOLS_MAKEKREPORT {

    if (workflow.containerEngine == 'singularity') {
        container = params.krakentools_singularity
    } else {
        container = params.krakentools_docker
    }

    publishDir "${params.output}/kraken", mode: 'copy'

    input:
    tuple val(reads_id), path(kraken_stdout_combined)
    path kraken_db

    output:
    tuple val(reads_id), path('*.kraken'), emit: kraken_report

    script:
    """
    make_kreport.py -i ${kraken_stdout_combined} -t ${kraken_db}/ktaxonomy.tsv -o ${reads_id}.kraken
    """
}