
FROM python:3.6

#RUN seqrepo -r ${SEQREPO_DATA_DIR} pull -i ${SEQREPO_DATA_RELEASE}
#RUN touch ${SEQREPO_DATA_DIR}/testing.txt

#RUN apt update && apt install -y git

WORKDIR /app

COPY . /app

RUN apt-get update

RUN pip install --upgrade pip

RUN pip install -r REQUIREMENTS.txt

RUN pip install -e .

COPY configuration/docker.ini /root/.variantvalidator

CMD gunicorn -b 0.0.0.0:8000 app --workers=3 --threads=5 --worker-class=gthread --chdir ./rest_variantValidator/
