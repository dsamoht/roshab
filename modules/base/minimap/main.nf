process MINIMAP {

    conda "bioconda::minimap2=2.26"
    if (workflow.containerEngine == 'singularity') {
        container = params.minimap_singularity
    } else {
        container = params.minimap_docker
    }

    publishDir "${params.output}/minimap", mode: 'copy'

    input:
    tuple val(reads_id), path(reads)
    path nucleotideFasta
    val fastaName

    output:
    tuple val(reads_id), path('*.map.sam'), emit: samFileOut

    script:
    """
    minimap2 -ax map-ont ${nucleotideFasta} ${reads} > ${fastaName}_${reads_id}.map.sam
    """
}
