process CHOPPER {

    if (workflow.containerEngine == 'singularity') {
        container = params.chopper_singularity
    } else {
        container = params.chopper_docker
    }

    publishDir "${params.output}/chopper", mode: 'copy'

    input:
    tuple val(reads_id), val(barcode), path(reads)

    output:
    tuple val(reads_id), path("*_qc_reads.fastq.gz"), emit: qc_reads

    script:
    """
    file_count=\$(ls ${params.output}/chopper/${reads_id}-*_qc_reads.fastq.gz | wc -l)
    zcat ${reads} | \
    chopper --headcrop 40 --threads ${task.cpus} | \
    chopper -l 500 --threads ${task.cpus} | \
    chopper -q 10 --threads ${task.cpus} | \
    gzip > ${reads_id}-\${file_count}_qc_reads.fastq.gz
    """
}
