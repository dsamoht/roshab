#!/usr/bin/env nextflow

include { BRACKEN              } from '../../modules/base/bracken'
include { CHOPPER_CHOPPER      } from '../../modules/roshab_wf/chopper'
include { CONCATENATE_BARCODES } from '../../modules/roshab_wf/concatenate_barcodes'
include { FASTQC               } from '../../modules/roshab_wf/fastqc'
include { KRAKEN               } from '../../modules/base/kraken'
include { KRAKENTOOLS_KRONA    } from '../../modules/roshab_wf/krakentools_krona'
include { KRONA                } from '../../modules/base/krona'
include { MULTIQC              } from '../../modules/roshab_wf/multiqc'
include { NANOSTAT             } from '../../modules/roshab_wf/nanostat'


workflow ROSHAB_WF {

   CONCATENATE_BARCODES()
   concatenated_barcodes = CONCATENATE_BARCODES.out.flatten()
    .map { file ->
        def matcher = file.name =~ /(barcode\d{2})/
        barcode_name = matcher ? params.exp + "_" + matcher[0][0] : params.exp
        return tuple(barcode_name, file)
    }
    .filter { it != null }
   
   ch_nanostats_out = NANOSTAT(concatenated_barcodes)
   ch_qc_reads = CHOPPER_CHOPPER(concatenated_barcodes)
   ch_fastqc_out = FASTQC(concatenated_barcodes)
   ch_kraken_out = KRAKEN(ch_qc_reads, params.kraken_db)
   ch_bracken_out = BRACKEN(ch_kraken_out.kraken_report, params.kraken_db)
   ch_krakentools_krona = KRAKENTOOLS_KRONA(ch_bracken_out.bracken_output)
   ch_krona_out = KRONA(ch_krakentools_krona.krakentools_to_krona)

   ch_multiqc_files = Channel.empty()
   ch_multiqc_files = ch_multiqc_files.mix(ch_nanostats_out,
                        ch_qc_reads,
                        ch_fastqc_out,
                        ch_kraken_out,
                        ch_bracken_out
                        ).map { it[1] }.collect()   
   
   MULTIQC(ch_multiqc_files)

}
