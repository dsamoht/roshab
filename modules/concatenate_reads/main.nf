process CONCATENATE_READS {

    input:
    tuple val(meta), path(in_reads)

    output:
    tuple val(meta), path('OUT/*.fastq.gz'), emit: out_reads

    script:
    def sample_name = meta[0]
    """
    ${projectDir}/bin/concatenate_reads.py --fastq ${in_reads} --output ${sample_name}.fastq.gz
    """
}
