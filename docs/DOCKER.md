# Docker

To install rest_variantValidator via Docker, first ensure you have both docker and docker-compose installed. 
See their [documentation](https://docs.docker.com/compose/install/) for information.

Create a directory collate your cloned repositories. Move into the directory then, clone the repository. 

```bash
$ git clone https://github.com/openvar/rest_variantValidator
```

Once the repository has been cloned, cd into the rest_variantValidator directory that the clone creates.
```bash
$ cd rest_variantValidator/
``` 

If you have cloned the repository previously, update it

```bash
$ git pull
```

## Configure

***Essential step***

Edit the file configuration/docker.ini
You will need to provide an email address and an 
[Entrez API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

*Note: If you have MySQl and or Postgres databases already running, you will need to alter the ports used in the 
docker-comose.yml file. The relevant section is shown here*
```yml
services:
  vdb:
    build:
      context: .
      dockerfile: vdb_docker.df
    ports:
      - "3306:3306"
    expose:
      - "3306"
  uta:
    build:
      context: .
      dockerfile: uta_docker.df
    ports:
      - "5432:5432"
    expose:
      - "5432"
``` 

*Note: configuration can be updated (see below for details)*

## Install and build

*Note: some of these steps take >>1hr to complete depending on the speed of your internet connection, particularly 
compiling SeqRepo*

```bash
# Pull images
$ docker-compose pull

# Build
$ docker-compose build --no-cache

# Build and load restvv and databases
# This step can take >>1hour and is complete when you see the message
# - "rest_variantvalidator_seqrepo_1 exited with code 0"
$ docker-compose up

# Shutdown
ctrl + c
```

## Launch
You can then launch the docker containers and run them using

```bash
$ docker-compose up
```

Note: We do not recommend running this in the background as you need to see the logs and therefore when the databases 
are ready to be used.

## Access rest_variantValidator
In a web browser navigate to
[http://0.0.0.0:8000/webservices/variantvalidator.html](http://0.0.0.0:8000/webservices/variantvalidator.html)

## Stop the app
`ctrl+c`

***To re-launch the app, go to Launch***

## Remove the containers
***Note: This step removes the container database. Effectively an uninstall. See Updating rest_variantValidator***
```bash
$ docker-compose down
```

## Run
You can go into the container via bash to use
[VariantValidator](https://github.com/openvar/variantValidator/blob/master/docs/MANUAL.md) directly.

```bash
$ docker-compose run restvv bash
```

and you can start the REST services manually, bound to one of the following ports
```bash
# port 8000 (default)
$ gunicorn  -b 0.0.0.0:8000 app --threads=5 --worker-class=gthread --chdir ./rest_variantValidator/
 
# port 8000
$ gunicorn  -b 0.0.0.0:8080 app --threads=5 --worker-class=gthread --chdir ./rest_variantValidator/


# port 5000
$ gunicorn  -b 0.0.0.0:5000 app --threads=5 --worker-class=gthread --chdir ./rest_variantValidator/
```


Note, that each time one of these commands is run a new container is created. 
For more information on how to use docker-compose see their [documentation](https://docs.docker.com/compose/).

It is possible to access both the UTA and Validator databases outside of docker as they expose the
 default PostgreSQL and MySQL ports (5432 and 3306 respectively). In the current set-up it is not possible to 
 access the seqrepo database outside of docker.
 

## Accessing VariantValidator and reconfiguring this container
The container hosts a full install of VariantValidator. 

VariantValidator can be run on the commandline from within the container. 

Instructions can be found in the VariantValidator [manual](https://github.com/openvar/variantValidator/blob/master/docs/MANUAL.md)

## Updating rest_variantValidator
Update requires that the restvv container is deleted from your system. This is not achieved by removing the container

If you are only running rest_variantValidator in docker, we recommend deleting and re-building all containers

```bash
# Delete all containers
$ docker-compose down
$ docker system prune -a --volumes
```

***Once you have deleted the containers, got to Install and Build***

Alternatively, you may wish to try and force the containers to re-build without deleting

```bash
# Force re-build
$ docker-compose down
$ docker-compose up --force-recreate
```

***If you choose this option, make sure you see the container restvv being re-created and all Python packages being 
reinstalled in the printed logs, otherwise the container may not actually be rebuilt and the contained modules may not
 update***