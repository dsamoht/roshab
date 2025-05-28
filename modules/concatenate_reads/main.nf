process CONCATENATE_READS {

    container workflow.containerEngine == 'singularity' ?
        params.python_singularity : params.python_docker

    input:
    tuple val(meta), path(in_reads)

    output:
    tuple val(meta), path('*.fastq.gz'), emit: out_reads

    script:
    def sample_name = meta[0]
    """
    concatenate_reads.py ${in_reads} ${sample_name}
    """
}
