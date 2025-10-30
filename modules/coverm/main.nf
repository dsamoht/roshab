process COVERM {

    publishDir "${params.output}/coverm", mode: 'copy'

    input:
    tuple val(group_id), val(metas), path(reads)
    path genome_directory
    val db_name

    output:
    tuple val(group_id), path('*.coverm.mean.tsv'), emit: coverm_out

    script:
    def names = metas.collect { meta -> "XsampleX_${meta[0]}_XdateX_${meta[1]}_XsiteX_${meta[2]}" }
    def rename_cmds = names.withIndex().collect { name, i ->
        "ln -s ${reads[i]} ${name}.fastq.gz"
    }.join("\n")

    """
    ${rename_cmds}
    coverm genome \\
        --single XsampleX_*.fastq.gz \\
        --genome-fasta-directory ${genome_directory} \\
        --mapper minimap2-ont \\
        --methods mean trimmed_mean count \\
        --min-covered-fraction 0 \\
        --output-file ${db_name}.coverm.mean.tsv \\
        --threads ${task.cpus}
    """
}
