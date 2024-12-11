process MINIMAP {

    container workflow.containerEngine == 'singularity' ?
        params.minimap_singularity : params.minimap_docker

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
