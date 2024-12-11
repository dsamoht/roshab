process CHOPPER {

    container workflow.containerEngine == 'singularity' ?
        params.chopper_singularity : params.chopper_docker

    input:
    tuple val(reads_id), path(reads)

    output:
    tuple val(reads_id), path("*_qc_reads.fastq.gz"), emit: qc_reads

    script:
    """
    zcat ${reads} | chopper -l 500 --threads ${task.cpus} | chopper -q 10 --threads ${task.cpus} | gzip > ${reads_id}_qc_reads.fastq.gz
    """
}

