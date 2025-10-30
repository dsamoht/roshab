FROM mambaorg/micromamba:1.5.8

ARG ENV_NAME=roshab_env
WORKDIR /app

COPY environment.yaml .
COPY . .

RUN micromamba env create -f environment.yaml && \
    micromamba clean -a -y

CMD ["micromamba", "run", "-n", "roshab_env", "python", "./app/app.py"]
