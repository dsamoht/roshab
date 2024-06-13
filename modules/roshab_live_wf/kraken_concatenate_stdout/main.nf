process KRAKEN_CONCATENATE_STDOUT {

    publishDir (
        path: "${params.output}/kraken",
        mode: "copy",
        saveAs: { fn ->
           { fn.replace(".combined", "") }
        }
    )

    input:
    tuple val(reads_id), path(kraken_stdout)

    output:
    tuple val(reads_id), path('*combined.kraken.out'), emit: kraken_stdout_combined

    script:
    def stdout_files = "${params.output}/kraken/${reads_id}.kraken.out"
    """
    cat ${stdout_files} ${kraken_stdout} > ${reads_id}.combined.kraken.out
    """
}
