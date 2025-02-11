workflow SETUP_SINGULARITY_WF {
    process KRAKEN {
          container = params.kraken_singularity
          script:
          """
          exit 0
          """
    }
     process BRACKEN {
          container = params.bracken_singularity
          script:
          """
          exit 0
          """
    }
     process KRAKENTOOLS {
          container = params.krakentools_singularity
          script:
          """
          exit 0
          """
    }
     process KRONA {
          container = params.krona_singularity
          script:
          """
          exit 0
          """
    }
     process PYTHON {
          container = params.python_singularity
          script:
          """
          exit 0
          """
    }
     process CHOPPER {
          container = params.chopper_singularity
          script:
          """
          exit 0
          """
    }
     process FASTQC {
          container = params.fastqc_singularity
          script:
          """
          exit 0
          """
    }
     process MULTIQC {
          container = params.multiqc_singularity
          script:
          """
          exit 0
          """
    }
     process MINIMAP {
          container = params.minimap_singularity
          script:
          """
          exit 0
          """
    }
     process NANOSTAT {
          container = params.nanostat_singularity
          script:
          """
          exit 0
          """
    }
    process SAMTOOLS {
          container = params.samtools_singularity
          script:
          """
          exit 0
          """
    }

    process QUALIMAP {
          container = params.qualimap_singularity
          script:
          """
          exit 0
          """
    }
    process PORECHOP {
          container = params.porechop_singularity
          script:
          """
          exit 0
          """
    }

    KRAKEN()
    BRACKEN()
    KRAKENTOOLS()
    KRONA()
    PYTHON()
    CHOPPER()
    FASTQC()
    MULTIQC()
    MINIMAP()
    NANOSTAT()
    SAMTOOLS()
    QUALIMAP()
    PORECHOP()

}
