process NANOSTAT {

    if (workflow.containerEngine == 'singularity') {
        container = params.nanostat_singularity
    } else {
        container = params.nanostat_docker
    }

    publishDir "${params.output}/nanostat", mode: 'copy'

    input:
    tuple val(reads_id), val(barcode), path(reads)

    output:
    tuple val(reads_id), path('*.stats.tsv'), emit: tsv

    script:
    def fastq_files = "${params.reads}/**fastq_pass/**.fastq.gz"
    """
    if [ ${barcode} == none ]
    then
    fastq_files=\$(ls ${fastq_files}) 
    else
    fastq_files=\$(ls ${fastq_files} | grep ${barcode})
    fi

    cat \${fastq_files} > ${reads_id}.fastq.gz

    NanoStat -o . -n ${reads_id}.stats.tsv --tsv --fastq ${reads_id}.fastq.gz
    """
}
