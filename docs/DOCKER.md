# Running rest_VariantValidator in Docker

## Prerequisites

To install rest_variantValidator via Docker, first ensure that you have both docker and docker-compose installed. 
See their [documentation](https://docs.docker.com/compose/install/) for information.


## Clone the rest_VariantValidator Repository
Create a directory to collate your cloned repositories. Move into the directory, then clone the repository. 

```bash
$ git clone https://github.com/openvar/rest_variantValidator
```

Once the repository has been cloned, cd into the rest_variantValidator directory that the clone creates.

```bash
$ cd rest_variantValidator
``` 

If you have cloned the repository previously, update it prior to installing/re-installing using Docker

```bash
$ git pull
```

## Configuring the software

Edit the file located in `configuration/docker.ini`
You will need to provide an email address

**Optional (from VariantValidator v2.0.0 - September 2021)** Generate an Entrez API key. This will be necessary if you 
do not update your container for more than 12 months; else leave as `None`. See 
[Entrez API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/) for details

Note: Reconfiguration can be achieved by accessing the docker container through bash. See below for entry and the 
VariantValidator [manual](https://github.com/openvar/variantValidator/blob/master/docs/MANUAL.md) for details

## Build the container

*Note: some of these steps take >>1hr to complete depending on the speed of your internet connection, particularly 
compiling SeqRepo*

- Pull images

```bash
$ docker-compose pull
```

#### Build and startup procedure

rest_VariantValidator can be built in Production mode and Development mode. Development mode mounts the root directory 
of the host git Repository to the equivalent project directory in the docker container. This means that changes to the 
code on the host machine are mapped into the container allowing on-the-fly development.
Choose one of the following commands to build and start the rest_VariantValidaor containers

- Production build
```bash
# Build
$ docker-compose build --no-cache rv-vvta rv-vdb rv-seqrepo rest-variantvalidator
```
- Development and testing build
```bash
# Build
$ docker-compose -f docker-compose.yml -f docker-compose-dev.yml build --no-cache rv-vvta rv-vdb rv-seqrepo rest-variantvalidator
```
- The build stage has completed when you see
```
 => [rest-variantvalidator 10/10] COPY configuration/docker.ini /root/.variantvalidator                                                                                                                                            0.0s
 => [rest-variantvalidator] exporting to image                                                                                                                                                                                     2.3s
 => => exporting layers                                                                                                                                                                                                            2.3s
 => => writing image sha256:097829685d99c7b308563dbee52009bc3dd7d79e85e195d454f3bf602afd5d95                                                                                                                                       0.0s
 => => naming to docker.io/library/rest_variantvalidator-rest-variantvalidator               
```

- Use this command to complete the build and wait for the above messages
```bash
$ docker-compose up -d rv-vvta && \
  docker-compose up -d rv-vdb && \
  docker-compose up -d rv-seqrepo && \
  docker-compose up -d rest-variantvalidator -v '${HOME}/variantvalidator_data/seqdata' -v '${HOME}/variantvalidator_data/logs'
```
- Or for a development and testing build, swap for these commands

- Create directories for sharing resources between your computer and the containers
```bash
$ mkdir -p ~/variantvalidator_data/seqdata && mkdir -p ~/variantvalidator_data/logs
```
*i.e.,* a directory called `variantvalidator_data` in your `home` directory with sub-directories `seqdata` and `logs`

```bash
$ docker-compose up -d rv-vvta && \
  docker-compose up -d rv-vdb && \
  docker-compose up -d rv-seqrepo && \
  docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d dev-mode
```

- The containers are started and running when you see
```bash
Creating rest_variantvalidator_rv-vvta_1 ... done
Creating rest_variantvalidator_rv-vdb_1 ... done
Creating rest_variantvalidator_rv-seqrepo_1 ... done
Creating rest_variantvalidator_rest-variantvalidator_1 ... done
```

### Test the build
```bash
# Run PyTest (all tests should pass)
$ docker exec rest_variantvalidator-rest-variantvalidator-1 pytest
```
Note: Different host Operating Systems name the container using slightly different conventions e.g. underscores instead 
of hyphens. To find your container name run the command

```bash
$ docker ps
*******************************************************************************************************************************************************************************************************************************************************************************
CONTAINER ID   IMAGE                                         COMMAND                  CREATED          STATUS          PORTS                                                                                                      NAMES
75078f429d72   rest_variantvalidator-rest-variantvalidator   "/bin/bash -c 'sleep…"   41 seconds ago   Up 39 seconds   0.0.0.0:5000->5000/tcp, 0.0.0.0:5050->5050/tcp, 0.0.0.0:8000->8000/tcp, 0.0.0.0:9000->9000/tcp, 8080/tcp   rest_variantvalidator-rest-variantvalidator-1
*******************************************************************************************************************************************************************************************************************************************************************************
```
***Note: In Development and testing builds, the container name will be e.g. rest_variantvalidator-dev-mode-1***

# Run the server
```bash
# Start the container in detached mode
$ docker exec -it rest_variantvalidator-rest-variantvalidator-1 gunicorn -b 0.0.0.0:8000 --timeout 600 wsgi:app --threads=5 --chdir ./rest_VariantValidator/
```

Optional: If your docker instance has multiple available cores, you can increase processing power by starting multiple workers e.g.
```bash
docker exec -it rest_variantvalidator-rest-variantvalidator-1 gunicorn -b 0.0.0.0:8000 --workers 3 --timeout 600 wsgi:app --threads=5 --chdir ./rest_VariantValidator/
```

***Note: In Development and testing builds, the container name will be e.g. rest_variantvalidator-dev-mode-1***

In a web browser navigate to
[http://0.0.0.0:8000](http://0.0.0.0:8000)

When you are finished, stop the container
```
ctrl + c
```

***Note: you may need to change :8080 to one of :5000 or :8000 depending on whether you altered the default port above***

### Build errors you may encounter

***If you have MySQL and or Postgres databases already running, you may encounter an error***  

> "ERROR: for vdb  Cannot start service vdb: Ports are not available: listen tcp 0.0.0.0:3306: bind: address already in use" 

If you encounter these issues, stop the build by pressing `ctrl+c`

- Reconfigure the ports used in the `docker-comose.yml` file as shown here
```yml
services:
  vdb:
    build:
      context: .
      dockerfile: vdb_docker.df
    ports:
      # - "33060:3306"
      - "3306:3306"
    expose:
      # - "33060"
      - "3306"
  uta:
    build:
      context: .
      dockerfile: uta_docker.df
    ports:
      - "54320:5432"
    expose:
      - "54320"

``` 
- hash (`#`) the conflicting port and add the new ports as shown above

Once complete, re-build as above

***You may encounter a build error relating to other unavailable ports***  

> "Cannot start service restvv: Ports are not available: listen tcp 0.0.0.0:8000: bind: address already in use" 

If you encounter these issues, stop the build by pressing `ctrl+c`

- Reconfigure the ports used in the `docker-comose.yml` file as shown here

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
      # - "8000:8000"
      - "8080:8080"
    expose:
      - "5000"
      # - "8000"
      - 8080
```

- hash (`#`) the conflicting port and add the new ports as shown above
- Change the command in Dockerfile to reflect the changes e.g. `CMD gunicorn  -b 0.0.0.0:8080 app --threads=5 --chdir ./rest_VariantValidator/`

Once complete, re-build as above

## Accessing the VariantValidator databases externally
It is possible to access both the UTA and Validator databases outside of docker as they expose the
 default PostgreSQL and MySQL ports (5432 and 3306 respectively). You can also access the seqrepo database outside of 
docker. Navigate to ~/variantvalidator_data/seqdata 
 

## Accessing VariantValidator directly through bash and reconfiguring a container post build
The container hosts a full install of VariantValidator. 

To start this version you start the container in detached mode and access it using

```bash
$ docker-compose exec rest_variantvalidator-rest-variantvalidator-1 bash
```

When you are finished exit the container

```bash
$ exit
```

#### Running the VariantValidator shell script

Once installed and running it is possible to run VariantValidator via a bash shell using the running the container

**Example**
```bash
# Note: The variant description must be contained in '' or "". See MANUAL.md for more examples
$ docker exec -it rest_variantvalidator-rest-variantvalidator-1 python bin/variant_validator.py -v 'NC_000017.11:g.50198002C>A' -g GRCh38 -t mane -s individual -f json -m
```

## Developing VariantValidator in Docker
Create the development and testing build and changes you make in the cloned Repo should map into the container

Create a new branch for your developments

```bash
$ git branch name_of_branch
$ git checkout name_of_branch
```

You can then use the containers Python interpreter to run queries, e.g.

```python
import json
import VariantValidator
vval = VariantValidator.Validator()
variant = 'NM_000088.3:c.589G>T'
genome_build = 'GRCh38'
select_transcripts = 'all'
validate = vval.validate(variant, genome_build, select_transcripts)
validation = validate.format_as_dict(with_meta=True)
print(json.dumps(validation, sort_keys=True, indent=4, separators=(',', ': ')))
```

## Developing rest_VariantValidator in Docker
The process for cloning the repo is the same as for VariantValidator

```bash
$ cd ~/share/DevelopmentRepos
$ git clone https://github.com/openvar/rest_variantValidator.git
```

Also, branches are created in the same way 

```bash
$ git checkout develop
$ git pull
$ git branch name_of_branch
$ git checkout name_of_branch
```

Navigating to the Repo is identical

```bash
$ docker-compose exec restvv bash
$ cd /usr/local/share/DevelopmentRepos/rest_variantValidator
```

However, instead of running `pip install -e .`, we can test the install using the Python development server

```bash
python rest_variantValidator/app.py
```

## Updating rest_variantValidator
To update a container, use

```bash
$ docker-compose build --build <service name e.g. rv-vvta> <service name>
```
where <service name> is a service listed in the docker-compose.yml

Once re-built, start all containers as normal

## Deleting rest_variantValidator

```bash
# Remove the specific containers
$ docker-compose rm <service name e.g. rv-vvta> <service name>

# OR Delete all containers on your system
$ docker-compose down
$ docker system prune -a --volumes
```

***If you choose this option, make sure you see the container restvv being re-created and all Python packages being 
reinstalled in the printed logs, otherwise the container may not actually be rebuilt and the contained modules may not
 update***
