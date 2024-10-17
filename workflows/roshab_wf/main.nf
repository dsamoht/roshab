#!/usr/bin/env nextflow

include { BRACKEN                   } from '../../modules/base/bracken'
include { CHOPPER_CHOPPER           } from '../../modules/roshab_wf/chopper'
include { CONCATENATE_BARCODES      } from '../../modules/roshab_wf/concatenate_barcodes'
include { FASTQC                    } from '../../modules/roshab_wf/fastqc'
include { KRAKEN                    } from '../../modules/base/kraken'
include { KRAKENTOOLS_KRONA         } from '../../modules/roshab_wf/krakentools_krona'
include { KRONA                     } from '../../modules/base/krona'
include { MINIMAP as MINIMAP_TAXA   } from '../../modules/base/minimap'
include { MINIMAP as MINIMAP_GENE   } from '../../modules/base/minimap'
include { MULTIQC                   } from '../../modules/roshab_wf/multiqc'
include { NANOSTAT                  } from '../../modules/roshab_wf/nanostat'
include { SAMTOOLS as SAMTOOLS_TAXA } from '../../modules/base/samtools'
include { SAMTOOLS as SAMTOOLS_GENE } from '../../modules/base/samtools'

workflow ROSHAB_WF {

   CONCATENATE_BARCODES(params.reads)
  
   concatenated_barcodes = CONCATENATE_BARCODES.out.flatten()
    .map { file ->
        def matcher = file.name =~ /(barcode\d{2})/
        barcode_name = matcher ? params.exp + "_" + matcher[0][0] : params.exp
        return tuple(barcode_name, file)
    }
    .filter { it != null }
   
   ch_nanostats_out = NANOSTAT(concatenated_barcodes)
   ch_qc_reads = CHOPPER_CHOPPER(concatenated_barcodes)
   ch_fastqc_out = FASTQC(ch_qc_reads)
   ch_kraken_out = KRAKEN(ch_qc_reads, params.kraken_db)
   ch_minimap_taxa_out = MINIMAP_TAXA(ch_qc_reads, params.minimap_taxa_db, "taxa")
   ch_samtools_taxa_out = SAMTOOLS_TAXA(ch_minimap_taxa_out, "taxa")
   ch_minimap_gene_out = MINIMAP_GENE(ch_qc_reads, params.minimap_gene_db, "gene")
   ch_samtools_gene_out = SAMTOOLS_GENE(ch_minimap_gene_out, "gene")
   ch_bracken_out = BRACKEN(ch_kraken_out.kraken_report, params.kraken_db)
   ch_krakentools_krona = KRAKENTOOLS_KRONA(ch_bracken_out.bracken_output)
   ch_krona_out = KRONA(ch_krakentools_krona.krakentools_to_krona)

   ch_multiqc_files = Channel.empty()
   ch_multiqc_files = ch_multiqc_files.mix(ch_nanostats_out.ifEmpty([]),
                        ch_qc_reads.ifEmpty([]),
                        ch_fastqc_out,
                        ch_kraken_out,
                        ch_samtools_taxa_out.idxstatsFile.ifEmpty([]),
                        ch_samtools_gene_out.idxstatsFile.ifEmpty([]),
                        ch_bracken_out.ifEmpty([])
                        ).map { it[1] }.collect()   
   
   MULTIQC(ch_multiqc_files)

}
