process PORECHOP_ABI {

    if (workflow.containerEngine == 'singularity') {
        container = params.porechop_abi_singularity
    } else {
        container = params.porechop_abi_docker
    }

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*porechopped_reads.fastq.gz"), emit: porechopped_reads
    tuple val(meta), path("*porechop.log"), emit: log

    script:
    def sample_name = meta[0]
    """
    porechop_abi --ab_initio -t ${task.cpus} -i ${reads} -o ${sample_name}_porechopped_reads.fastq.gz > ${sample_name}_porechop.log
    """
}
