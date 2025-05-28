process MINIMAP {

    container workflow.containerEngine == 'singularity' ?
        params.minimap_singularity : params.minimap_docker

    input:
    tuple val(meta), path(reads)
    path nucleotideFasta
    val fastaName

    output:
    tuple val(meta), path('*.map.sam'), emit: samFileOut

    script:
    def sample_name = meta[0]
    """
    minimap2 -ax map-ont --secondary=no -t ${task.cpus} ${nucleotideFasta} ${reads} > ${fastaName}_${sample_name}.map.sam
    """
}
