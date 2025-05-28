process PLOT_GENE_MINIMAP {

    container workflow.containerEngine == 'singularity' ?
        params.pandas_singularity : params.pandas_docker
    
    publishDir "${params.output}/figures", mode: 'copy'

    input:
    tuple val(group_id), val(metas), path(files)

    output:
    tuple val(group_id), path('*.pdf'), emit: figure_file

    script:
    def names = metas.collect { meta -> "XsampleX_${meta[0]}_XdateX_${meta[1]}_XsiteX_${meta[2]}" }.join(" ")
    def cov_files = files.collect().join(" ")
    """
    cyanotoxin_bgc_genes_abundance.py -n ${names} -f ${cov_files} -g ${group_id}
    """
}
