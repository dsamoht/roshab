process KRAKENTOOLS_KREPORT2MPA {

    publishDir "${params.output}/kraken", mode: 'copy'

    input:
    tuple val(meta), path(kraken_report)

    output:
    tuple val(meta), path('*.mpa'), emit: mpa_report

    script:
    def output_name = "XsampleX_${meta[0]}_XdateX_${meta[1]}_XsiteX_${meta[2]}"
    """
    mv ${kraken_report} ${output_name}
    kreport2mpa.py -r ${output_name} -o ${output_name}.mpa --intermediate-ranks --display-header
    """
}
