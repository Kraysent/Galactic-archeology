FROM omtoolenv

COPY . /app
RUN mkdir data
RUN mkdir data/analysis
WORKDIR /app
CMD chmod +x example_runner.sh && ./example_runner.sh