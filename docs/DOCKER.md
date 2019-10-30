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

## Configure
Edit the file configuration/docker.ini
You will need to provide your email address and we recommend generating and using an 
[Entrez API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

*Note: configuration can be updated (see below for details)*

## Install and build

*Note: some of these steps take >>1hr to complete depending on the speed of your internet connection, particularly 
compiling SeqRepo*

```bash
# Build the containers
$ docker-compose up --build -d

# Load UTA
$ docker-compose run uta

# Shutdown
ctrl + c

# Load seqrepo
$ docker-compose run seqrepo
```

## Launch
You can then launch the docker containers and run them using

```bash
docker-compose up
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
***Note: This step removes the container database. Effectively an uninstall***
```bash
$ docker-compose down
```

## Run
You can go into the container via bash to use
[VariantValidator](https://github.com/openvar/variantValidator/blob/master/docs/MANUAL.md) directly.

```bash
$ docker-compose run restvv bash
```

Note, that each time one of these commands is run a new container is created. 
For more information on how to use docker-compose see their [documentation](https://docs.docker.com/compose/).

It is possible to access both the UTA and Validator databases outside of docker as they expose the
 default PostgreSQL and MySQL ports (5432 and 3306 respectively). In the current set-up it is not possible to 
 access the seqrepo database outside of docker.
 
Finally, it should be noted that the current UTA docker container is not up-to-date and only contains the 
2017-10-26 release. Therefore use caution when interpreting these results, and be advised the
 VariantValidator tests will fail. 
 

## Accessing VariantValidator and reconfiguring this container
The container hosts a full install of VariantValidator. 

VariantValidator can be run on the commandline from within the container. 

Instructions can be found in the VariantValidator [manual](https://github.com/openvar/variantValidator/blob/master/docs/MANUAL.md)
