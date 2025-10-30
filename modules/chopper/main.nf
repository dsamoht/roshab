process CHOPPER {

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*_qc_reads.fastq.gz"), emit: qc_reads

    script:
    def sample_name = meta[0]
    """
    zcat ${reads} | chopper -l 500 --threads ${task.cpus} | chopper -q 10 --threads ${task.cpus} | gzip > ${sample_name}_qc_reads.fastq.gz
    """
}

