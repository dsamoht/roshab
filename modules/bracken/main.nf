process BRACKEN {

    if (workflow.containerEngine == 'singularity') {
        container = params.bracken_singularity
    } else {
        container = params.bracken_docker
    }

    publishDir "${params.output}/kraken", mode: 'copy'
    
    //errorStrategy 'ignore'

    input:
    path krakenOutputFile
    path kraken_db
    path reads_id

    output:
    path '*.bracken', emit: brackenOutputFile
    path '*_bracken_species.kraken', emit: brackenOutputForKrona

    script:
    """
    reads_id=\$(cat ${reads_id})
    echo \$reads_id > reads_id
    est_abundance.py -i ${krakenOutputFile} -k ${kraken_db}/database200mers.kmer_distrib -l S -t 10 -o \${reads_id}.bracken
    """
}