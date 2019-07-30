
FROM python:3.6

#RUN seqrepo -r ${SEQREPO_DATA_DIR} pull -i ${SEQREPO_DATA_RELEASE}
#RUN touch ${SEQREPO_DATA_DIR}/testing.txt

#RUN apt update && apt install -y git

WORKDIR /app

COPY . /app

RUN apt-get update

RUN pip install -r REQUIREMENTS.txt

RUN pip install -e .

COPY configuration/docker.ini /root/.variantvalidator

CMD python3 rest_variantValidator/wsgi.py