# Docker

To install rest_variantValidator via Docker, first ensure you have both docker and docker-compose installed. 
See their [documentation](https://docs.docker.com/compose/install/) for information.

Then, clone the repository and move into that directory.

```bash
$ git clone https://github.com/openvar/rest_variantValidator
cd rest_variantValidator/
``` 

## Configure
Edit the file configuration/docker.ini
You will need to provide your email address and we recommend generating and using an [Entrez API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

*Note: configuration can be updated (see below for details)*


## Launch
You can then launch the docker containers and run them using

```bash
docker-compose up
```

Note, the first time this is run it will download each of the databases including the pre-populated
validator database and could take up to 30 minutes depending on your connection. We do not recommend
running this in the background as you need to see the logs and therefore when the databases are
ready to be used.

## Access rest_variantValidator
In a web browser navigate to
[0.0.0.0:8000](http://0.0.0.0:8000/)

## Stop the app
`ctrl+c`

## Stop the remove the containers
```bash
$ docker-compose down
```

## Run
You can go into the container via bash to use
[VariantValidator](https://github.com/openvar/variantValidator/blob/develop_v1/docs/MANUAL.md) directly.

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

Instructions can be found in the VariantValidator [manual](https://github.com/openvar/variantValidator/blob/develop_v1/docs/MANUAL.md)

## Check which docker containers are running

```bash
$ docker ps -a
```

## List all docker containers
```bash
$ docker container ls -a
```

## Stop containers

```bash
$ docker stop <container>
```

## Delete containers

```bash
$ docker rm <cointainer>
```

## Delete images
```bash
$ docker rmi <image>
```