process SAMTOOLS {

    container workflow.containerEngine == 'singularity' ?
        params.samtools_singularity : params.samtools_docker

    publishDir "${params.output}/samtools", mode: 'copy'

    input:
    tuple val(reads_id), path(samFile)
    val fastaName

    output:
    tuple val(reads_id), path('*map.sorted.bam'), emit: bamFile
    tuple val(reads_id), path('*map.sorted.coverage'), emit: idxstatsFile

    script:
    """
    samtools view -bS ${samFile} | samtools sort -o ${fastaName}_${reads_id}_map.sorted.bam -
    samtools index ${fastaName}_${reads_id}_map.sorted.bam
    samtools coverage ${fastaName}_${reads_id}_map.sorted.bam > ${fastaName}_${reads_id}_map.sorted.coverage
    """
}