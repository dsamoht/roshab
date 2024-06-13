process MULTIQC {

    if (workflow.containerEngine == 'singularity') {
        container = params.multiqc_singularity
    } else {
        container = params.multiqc_docker
    }

    publishDir "${params.output}/multiqc", mode: 'copy'

    input:
    path multiqc_files, stageAs: "?/*"

    output:
    path "*.html", emit: report
    path "*_data", emit: data

    """
    multiqc -c ${projectDir}/assets/multiqc_config.yml -e general_stats . 
    """

}
