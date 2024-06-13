process GET_READS_INFO {
    // Inspect the file name and get
    // the barcode number if present.
    // returns: "[experiment-name]_[barcode]"

    input:
    path input_reads
    val exp_name

    output:
    path 'reads_id', emit: reads_id

    script:
    """
    #!/usr/bin/env bash
    tmp=\$(echo ${input_reads} | sed 's/.fastq.*//')
    if [[ \$tmp =~ barcode[0-9]{2} ]]; then
    barcode=\$(echo \$tmp | awk -F 'barcode' '{print \$NF}' | awk -F '_' '{print \$1}')
    echo ${exp_name}_barcode\${barcode} > reads_id
    else
    echo ${exp_name} > reads_id
    fi
    """

}