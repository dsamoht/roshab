workflow SETUP_DOCKER_WF {
    process KRAKEN {
          container = params.kraken_docker
          script:
          """
          exit 0
          """
    }
     process BRACKEN {
          container = params.bracken_docker
          script:
          """
          exit 0
          """
    }
     process KRAKENTOOLS {
          container = params.krakentools_docker
          script:
          """
          exit 0
          """
    }
     process KRONA {
          container = params.krona_docker
          script:
          """
          exit 0
          """
    }
     process PYTHON {
          container = params.python_docker
          script:
          """
          exit 0
          """
    }
     process CHOPPER {
          container = params.chopper_docker
          script:
          """
          exit 0
          """
    }
     process FASTQC {
          container = params.fastqc_docker
          script:
          """
          exit 0
          """
    }
     process MULTIQC {
          container = params.multiqc_docker
          script:
          """
          exit 0
          """
    }
     process MINIMAP {
          container = params.minimap_docker
          script:
          """
          exit 0
          """
    }
     process NANOSTAT {
          container = params.nanostat_docker
          script:
          """
          exit 0
          """
    }
    process SAMTOOLS {
          container = params.samtools_docker
          script:
          """
          exit 0
          """
    }
    process QUALIMAP {
          container = params.qualimap_docker
          script:
          """
          exit 0
          """
    }
    process PORECHOP {
          container = params.porechop_docker
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
