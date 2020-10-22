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

*Note: If you have MySQL and or Postgres databases already running, you may encounter an error during the following 
build stage e.g.*  

> "ERROR: for vdb  Cannot start service vdb: Ports are not available: listen tcp 0.0.0.0:3306: bind: address already in use" 

*In this case you will need to alter the ports used in the docker-comose.yml file*
*The relevant section is shown here with recommended changes*
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

*Note: You may encounter a build error relating to other unavailable ports e.g.*  

> "Cannot start service restvv: Ports are not available: listen tcp 0.0.0.0:8080: bind: address already in use" 

*In this case you will need to alter the ports used in the docker-comose.yml file*
*The relevant section is shown here with recommended changes*

```yml
  restvv:
    build: .
    depends_on:
      - vdb
      - uta
    volumes:
      - seqdata:/usr/local/share/seqrepo
    ports:
      - "5000:5000"
      - "8000:8000"
      # - "8080:8080"
```

*If you encounter these issues, stop the build by pressing `ctrl+c` then run*

```bash
$ docker-compose down
$ docker-compose up --force-recreate
```

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

## Launch the rest_VariantValidator API
You run the API directly in the docker container directly via bash

```bash
$ docker-compose run restvv bash
```
tart the REST services manually, bound to one of the following commands. Note, if you get an error saying 
there is a conflict on for example port 8000, try starting with an alternate version of the commands provided
```bash
# Start
$ docker-compose up

# Shutdown
ctrl + c

 ```
## Access rest_variantValidator
In a web browser navigate to
[http://0.0.0.0:8000](http://0.0.0.0:8000)
***Note: you may need to change :8080 to one of :5000 or :8000 depending on the activation command***

## Stop the app and exit the container
`ctrl+c`

```bash
$ exit
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
under sections **Database updates** and **Operation**

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
 
 ## Removing the containers
```bash
$ docker-compose down
```