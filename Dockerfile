FROM python:3.6.1

WORKDIR /app

ADD Pipfile Pipfile.lock ./
RUN pip3 install pipenv
RUN pipenv install

ADD . /app/.

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    CONNECT_AUTH_TYPE=in \
    KAT_ENV=production \
    FLASK_ENV=production \
    TEST_CONNECT_SA_NS=default \
    TEST_CONNECT_SA_NAME=nectar \
    TEST_CONNECT_CLUSTER=kind-kind \
    TEST_CONNECT_CONTEXT=kind-kind \
    TEST_CONNECT_KUBECTL=kubectl

EXPOSE 5000

ENTRYPOINT ["pipenv", "run", "python3"]