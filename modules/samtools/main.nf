process SAMTOOLS {

    container workflow.containerEngine == 'singularity' ?
        params.samtools_singularity : params.samtools_docker

    publishDir "${params.output}/samtools", mode: 'copy'

    input:
    tuple val(meta), path(samFile)
    val fastaName

    output:
    //tuple val(meta), path('*map.sorted.bam'), emit: bamFile
    tuple val(meta), path('*map.sorted.coverage'), emit: covFile

    script:
    def sample_name = meta[0]
    """
    samtools view -bS ${samFile} | samtools sort -o ${fastaName}_${sample_name}_map.sorted.bam -
    samtools index ${fastaName}_${sample_name}_map.sorted.bam
    samtools coverage ${fastaName}_${sample_name}_map.sorted.bam > ${fastaName}_${sample_name}_map.sorted.coverage
    """
}
