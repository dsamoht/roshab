process PLOT_KRAKEN {

    container workflow.containerEngine == 'singularity' ?
        params.pandas_singularity : params.pandas_docker
    
    publishDir "${params.output}/figures", mode: 'copy'

    input:
    tuple val(group_id), path(combined_mpa)

    output:
    tuple val(group_id), path('*.pdf'), emit: figure_file

    script:
    """
    kraken_cyano_report.py -i ${combined_mpa} -n ${group_id}
    """
}
