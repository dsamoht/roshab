process CHOPPER_CHOPPER {

    if (workflow.containerEngine == 'singularity') {
        container = params.chopper_singularity
    } else {
        container = params.chopper_docker
    }

    input:
    tuple val(reads_id), path(raw_reads)

    output:
    tuple val(reads_id), path("*_qc_reads.fastq.gz"), emit: qc_reads

    script:
    """
    zcat ${raw_reads} | chopper --headcrop 40 --threads ${task.cpus} | chopper -l 500 --threads ${task.cpus} | chopper -q 10 --threads ${task.cpus} | gzip > ${reads_id}_qc_reads.fastq.gz
    """
}
