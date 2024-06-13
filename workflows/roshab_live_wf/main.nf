#!/usr/bin/env nextflow

include { BRACKEN                            } from '../../modules/base/bracken'
include { CHOPPER                            } from '../../modules/roshab_live_wf/chopper'
include { FASTQC                             } from '../../modules/roshab_live_wf/fastqc'
include { KRAKEN                             } from '../../modules/base/kraken'
include { KRAKEN_CONCATENATE_STDOUT          } from '../../modules/roshab_live_wf/kraken_concatenate_stdout'
include { KRAKENTOOLS_KRONA                  } from '../../modules/base/krakentools_krona'
include { KRAKENTOOLS_MAKEKREPORT            } from '../../modules/roshab_live_wf/krakentools_makekreport'
include { KRONA                              } from '../../modules/base/krona'
include { MULTIQC                            } from '../../modules/roshab_live_wf/multiqc'
include { NANOSTAT                           } from '../../modules/roshab_live_wf/nanostat'


workflow ROSHAB_LIVE_WF {

   ch_new_reads = Channel.watchPath("${params.reads}/**fastq_pass/**.fastq.gz")
   .map { file ->
        def matcher = file.name =~ /(barcode\d{2})/
        barcode_name = matcher ? params.exp + "_" + matcher[0][0] : params.exp
        return tuple(barcode_name, matcher ? matcher[0][0]: "none", file)
    }
   .filter { it != null }

   ch_nanostat = NANOSTAT(ch_new_reads)
   ch_fastqc = FASTQC(ch_new_reads)
   ch_qc_reads = CHOPPER(ch_new_reads)
   ch_kraken_stdout = KRAKEN(ch_qc_reads, params.kraken_db)
   ch_kraken_stdout_combined = KRAKEN_CONCATENATE_STDOUT(ch_kraken_stdout.kraken_stdout)
   ch_kreport = KRAKENTOOLS_MAKEKREPORT(ch_kraken_stdout_combined.kraken_stdout_combined, params.kraken_db)

   ch_bracken_out = BRACKEN(ch_kreport, params.kraken_db)
   ch_krakentools_krona = KRAKENTOOLS_KRONA(ch_bracken_out)
   ch_krona_out = KRONA(ch_krakentools_krona)

   def extensions = ['*.html', '*.zip', '*.kraken', '*.bracken', '*.tsv']

   new_output = Channel.watchPath("${projectDir}/*/*/*")
   .filter { file -> 
        extensions.any { file.name.endsWith(it.substring(1)) }
    }
   .view()
   
   MULTIQC(new_output)

}
