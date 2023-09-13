FROM ubuntu:xenial

WORKDIR /app

COPY ./taxonomy.py /app/scripts/

COPY ./mibig_prot_seqs_3.1.fasta /app/data/

ADD cd-hit-v4.8.1-2019-0228.tar.gz /app/

RUN apt-get update && apt-get install -y make \
    gcc \
    g++ \
    python3 \
    python3-pip \
    zlib1g-dev \
    wget \
    git

RUN pip3 install --no-cache-dir setuptools && \
    pip3 install --upgrade "pip < 21.0" && \
    pip3 install --no-cache-dir plotly && \
    pip3 install --no-cache-dir pandas

RUN git clone https://github.com/hyattpd/Prodigal.git --branch v2.6.3 && \
    git clone https://github.com/fenderglass/Flye.git --branch 2.9.2 && \
    git clone https://github.com/DerrickWood/kraken2.git --branch v2.1.3 && \
    git clone https://github.com/jenniferlu717/Bracken --branch v2.8

RUN wget https://genome-idx.s3.amazonaws.com/kraken/k2_standard_08gb_20230605.tar.gz && \
    tar -xvf k2_standard_08gb_20230605.tar.gz && \
    rm -rf k2_standard_08gb_20230605.tar.gz

WORKDIR /app/cd-hit-v4.8.1-2019-0228

RUN make

WORKDIR /app/cd-hit-v4.8.1-2019-0228/cd-hit-auxtools

RUN make

WORKDIR /app/kraken2

RUN ./install_kraken2.sh .

WORKDIR /app/Flye

RUN python3 setup.py install

WORKDIR /app/Prodigal

RUN make

WORKDIR /app/Bracken

RUN bash install_bracken.sh

WORKDIR /app

ENV PATH=$PATH:/app/Prodigal:/app/Flye/bin:/app/kraken2/:/app/Bracken/src:/app/cd-hit-v4.8.1-2019-0228:/app/scripts