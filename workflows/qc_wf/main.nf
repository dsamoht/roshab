#!/usr/bin/env nextflow

include { CHOPPER      } from '../../modules/chopper'
include { PORECHOP_ABI } from '../../modules/porechop_abi'


workflow QC_WF {

    take:
    reads

    main:

    ch_porechop_out = PORECHOP_ABI(reads)
    ch_qc_reads = CHOPPER(ch_porechop_out.porechopped_reads)

    emit:
    ch_qc_reads

}
