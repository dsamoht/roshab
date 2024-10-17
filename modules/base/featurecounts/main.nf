process FEATURECOUNTS {

    conda "bioconda::subread=2.0.1"
    if (workflow.containerEngine == 'singularity') {
        container = params.subread_singularity
    } else {
        container = params.subread_docker
    }

    errorStrategy 'ignore'
    publishDir "${params.output}/featurecounts", mode: 'copy'

    input:
    tuple val(reads_id), path(genes_gff)
    tuple val(reads_id), path(sorted_bam)

    output:
    tuple val(reads_id), path("*featureCounts.txt"), emit: counts
    tuple val(reads_id), path("*featureCounts.txt.summary"), emit: summary

    script:
    options = "-L -t CDS,gene -g ID -s 0"
    def genes = genes_gff.join(' ')

    """
    cat ${genes} > global.gff 
    featureCounts ${options} -a global.gff -o featureCounts.txt ${sorted_bam}
    """
}