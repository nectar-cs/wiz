FROM gcr.io/nectar-bazaar/py-ci:latest

WORKDIR /app

ADD Pipfile Pipfile.lock ./
RUN pip3 install pipenv
RUN pipenv install

ADD . /app

EXPOSE 5000

ARG CODECOV_TOKEN
ENV CODECOV_TOKEN=$CODECOV_TOKEN

ENTRYPOINT ["/py-ci/start.sh"]