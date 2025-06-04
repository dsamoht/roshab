workflow SETUP_DOCKER_WF {
    process KRAKEN {
          container = params.kraken_docker
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
    process PANDAS {
          container = params.pandas_docker
          script:
          """
          exit 0
          """
    }
    process PORECHOP_ABI {
          container = params.porechop_abi_docker
          script:
          """
          exit 0
          """
    }

    KRAKEN()
    KRAKENTOOLS()
    KRONA()
    PANDAS()
    PYTHON()
    CHOPPER()
    MULTIQC()
    MINIMAP()
    NANOSTAT()
    SAMTOOLS()
    PORECHOP_ABI()

}
