process BRACKEN {

    if (workflow.containerEngine == 'singularity') {
        container = params.bracken_singularity
    } else {
        container = params.bracken_docker
    }

    publishDir "${params.output}/bracken", mode: 'copy'

    errorStrategy 'ignore'
    
    input:
    tuple val(reads_id), path(kraken_report)
    path db

    output:
    tuple val(reads_id), path('*.bracken'), emit: bracken_output, optional:true

    script:
    """
    est_abundance.py -i ${kraken_report} -k ${db}/database200mers.kmer_distrib -l S -t 10 -o ${reads_id}.bracken
    if [ -f *bracken_species.kraken ]; then
        mv *bracken_species.kraken ${reads_id}.bracken
    fi
    """
}
