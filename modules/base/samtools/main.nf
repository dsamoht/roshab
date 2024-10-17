process SAMTOOLS {

    conda "bioconda::samtools=1.18"
    if (workflow.containerEngine == 'singularity') {
        container = params.samtools_singularity
    } else {
        container = params.samtools_docker
    }

    publishDir "${params.output}/samtools", mode: 'copy'

    input:
    tuple val(reads_id), path(samFile)
    val fastaName

    output:
    tuple val(reads_id), path('*map.sorted.bam'), emit: bamFile
    tuple val(reads_id), path('*map.sorted.idxstat'), emit: idxstatsFile

    script:
    """
    samtools view -bS ${samFile} | samtools sort -o ${fastaName}_${reads_id}_map.sorted.bam -
    samtools index ${fastaName}_${reads_id}_map.sorted.bam
    samtools idxstats ${fastaName}_${reads_id}_map.sorted.bam > ${fastaName}_${reads_id}_map.sorted.idxstat
    """
}