process KRAKENTOOLS_COMBINEMPA {

    input:
    tuple val(group_id), val(metas), path(files)

    output:
    tuple val(group_id), path('*.combined.mpa'), emit: combined_mpa

    script:
    """
    combine_mpa.py -i ${files} -o ${group_id}.combined.mpa
    """
}
