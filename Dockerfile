FROM omtoolenv

COPY . /app
RUN mkdir data
RUN mkdir data/analysis
WORKDIR /app
CMD python main.py create /app/examples/creation_config.yaml