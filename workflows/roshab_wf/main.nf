#!/usr/bin/env nextflow

include { CONCATENATE_READS         } from '../../modules/concatenate_reads'
include { COVERM as COVERM_ICYATOX  } from '../../modules/coverm'
include { COVERM as COVERM_NCBI     } from '../../modules/coverm'
include { DISPATCH                  } from '../dispatch'
include { KRAKEN                    } from '../../modules/kraken'
include { KRAKENTOOLS_COMBINEMPA    } from '../../modules/krakentools_combinempa'
include { KRAKENTOOLS_KREPORT2MPA   } from '../../modules/krakentools_kreport2mpa'
include { KRAKENTOOLS_KRONA         } from '../../modules/krakentools_krona'
include { KRONA                     } from '../../modules/krona'
include { MINIMAP as MINIMAP_GENE   } from '../../modules/minimap'
include { MULTIQC                   } from '../../modules/multiqc'
include { NANOSTAT                  } from '../../modules/nanostat'
include { PLOT_GENE_MINIMAP         } from '../../modules/figures/gene_minimap'
include { PLOT_KRAKEN               } from '../../modules/figures/taxonomy_kraken'
include { QC_WF                     } from '../qc_wf'
include { SAMTOOLS as SAMTOOLS_GENE } from '../../modules/samtools'


workflow ROSHAB_WF {

    ch_input = DISPATCH()
    ch_reads = CONCATENATE_READS(ch_input)

    // Run `porechop_abi` and `chopper` if --skip_qc is not set
    if (!params.skip_qc) {
        ch_qc_reads = QC_WF(ch_reads)
    }
    else {
        ch_qc_reads = ch_reads
    }
    // Group all reads into a single channel for `CoverM`
    coverm_ch_in = ch_qc_reads
        .map { meta, file -> tuple(meta[3], [meta, file]) }
        .groupTuple()
        .map { group_id, metadata_and_file ->
            def metas = metadata_and_file.collect { it[0] }
            def files = metadata_and_file.collect { it[1] }
            return [group_id, metas, files]
        }

    // Run `Nanostat`, `Kraken` and `CoverM` 
    ch_nanostats_out = NANOSTAT(ch_qc_reads)
    ch_kraken_out = KRAKEN(ch_qc_reads, params.kraken_db)
    ch_coverm_ncbi_out = COVERM_NCBI(coverm_ch_in, params.coverm_ncbi_db, "ncbi_cyano")

    // Convert `Kraken` report to MPA format and combine MPA files per group
    ch_krakentools_kreport2mpa_out = KRAKENTOOLS_KREPORT2MPA(ch_kraken_out.kraken_report)

    ch_krakentools_combinempa_in = ch_krakentools_kreport2mpa_out
        .map { meta, file -> tuple(meta[3], [meta, file]) }
        .groupTuple()
        .map { group_id, metadata_and_file ->
            def metas = metadata_and_file.collect { it[0] }
            def files = metadata_and_file.collect { it[1] }
            return [group_id, metas, files]
        }

    ch_combinempa2_out = KRAKENTOOLS_COMBINEMPA(ch_krakentools_combinempa_in)
    
    // Plot the `Kraken` results
    ch_kraken_plot_out = PLOT_KRAKEN(ch_combinempa2_out)
    
    // Mapping reads to cyanotoxin-related genes using `Minimap2`
    ch_minimap_gene_out = MINIMAP_GENE(ch_qc_reads, params.minimap_gene_db, "gene")
    ch_samtools_gene_out = SAMTOOLS_GENE(ch_minimap_gene_out, "gene")
   
    // Plotting the results of `Minimap2`
    ch_plot_gene_map_in = ch_samtools_gene_out
        .map { meta, file -> tuple(meta[3], [meta, file]) }
        .groupTuple()
        .map { group_id, metadata_and_file ->
            def metas = metadata_and_file.collect { it[0] }
            def files = metadata_and_file.collect { it[1] }
            return [group_id, metas, files]
        }
    
    ch_minimap_gene_plot_out = PLOT_GENE_MINIMAP(ch_plot_gene_map_in)
    
    ch_krakentools_krona = KRAKENTOOLS_KRONA(ch_kraken_out.kraken_report)
    ch_krona_out = KRONA(ch_krakentools_krona.krakentools_to_krona)

    ch_multiqc_files = Channel.empty()
    ch_multiqc_files = ch_multiqc_files.mix(ch_nanostats_out.ifEmpty([]),
                       ch_kraken_out
                       ).map { it[1] }.collect()   
   
    MULTIQC(ch_multiqc_files)

}
