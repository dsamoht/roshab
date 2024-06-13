process MULTIQC {

    if (workflow.containerEngine == 'singularity') {
        container = params.multiqc_singularity
    } else {
        container = params.multiqc_docker
    }

    maxForks 1

    publishDir "${params.output}/multiqc", mode: 'copy'

    errorStrategy 'retry'
    maxRetries 10

    input:
    path new_output

    output:
    path "*multiqc_report.html", emit: report
    path "*_data", emit: data

    """
    multiqc -c ${projectDir}/assets/multiqc_config.yml -e general_stats --force ${params.output} 
    """

}
