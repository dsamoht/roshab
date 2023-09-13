#!/usr/bin/env nextflow

process kraken2 {

    publishDir 'results/kraken2/', mode: 'copy', pattern: 'kraken2.tax.report'

    input:
    path rawReads

    output:
    path 'kraken2.tax.report', emit: kraken2OutputDir

    script:
    """
    kraken2 --db /app --report kraken2.tax.report ${rawReads}
    """
}

process bracken {

    publishDir 'results/kraken2/', mode: 'copy', pattern: 'kraken2.report.bracken'

    input:
    path kraken2OutputDir

    output:
    path 'kraken2.report.bracken', emit: brackenOutputDir

    script:
    """
    python3 /app/Bracken/src/est_abundance.py -i ${kraken2OutputDir} -k /app/database300mers.kmer_distrib -l S -o kraken2.report.bracken
    """
}

process plotly {

    publishDir 'results/plots/', mode: 'copy', pattern: 'kraken2.bracken.viz.html'

    input:
    path kraken2OutputDir
    path brackenOutputDir

    output:
    path 'kraken2.bracken.viz.html', emit: htmlOutput

    script:
    """
    python3 /app/scripts/taxonomy.py ${kraken2OutputDir} ${brackenOutputDir} kraken2.bracken.viz.html
    """
}

process flye {

    publishDir 'results/flye/'

    input:
    path rawReads

    output:
    path 'flye_out', emit: flyeOutputDir

    script:
    """
    flye --nano-raw ${rawReads} -o 'flye_out' --meta --threads 4
    """
}

process prodigal {

    publishDir 'results/prodigal/', mode: 'copy', pattern: 'coords.gbk'
    publishDir 'results/prodigal/', mode: 'copy', pattern: 'genes.faa'

    input:
    path flyeOutputDir

    output:
    path 'coords.gbk', emit: coordsOut
    path 'genes.faa', emit: genesOut

    script:
    """
    prodigal -i ${flyeOutputDir}/assembly.fasta -o coords.gbk -a genes.faa -p meta
    """
}

process cdhit2d {

    publishDir 'results/cd-hit-2d/'

    input:
    path genesOut

    output:
    path 'mibig.clstr', emit: coordsOut

    script:
    """
    cd-hit-2d -i /app/data/mibig_prot_seqs_3.1.fasta -i2 ${genesOut} -o mibig_db -c 0.9 -n 5 -d 0 -M 0 -T 0
    """
}

workflow {

    kraken2(params.raw_reads)
    bracken(kraken2.out.kraken2OutputDir)
    plotly(kraken2.out.kraken2OutputDir, bracken.out.brackenOutputDir)

}
