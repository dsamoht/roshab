process FASTQC {

    if (workflow.containerEngine == 'singularity') {
        container = params.fastqc_singularity
    } else {
        container = params.fastqc_docker
    }

    publishDir "${params.output}/fastqc", mode: 'copy'

    input:
    tuple val(reads_id), val(barcode), path(reads)

    output:
    tuple val(reads_id), path("*.html"), emit: html
    tuple val(reads_id), path("*.zip"), emit: zip

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
    fastqc ${reads_id}.fastq.gz
    """
}
