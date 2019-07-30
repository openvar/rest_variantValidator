# Docker

To install rest_variantValidator via Docker, first ensure you have both docker and docker-compose installed. 
See their [documentation](https://docs.docker.com/compose/install/) for information.

Then, clone the repository and move into that directory.

```bash
$ git clone https://github.com/openvar/rest_variantValidator
cd rest_variantValidator/
``` 

You can then launch the docker containers and run them using

```bash
docker-compose up
```

Note, the first time this is run it will download each of the databases including the pre-populated
validator database and could take up to 30 minutes depending on your connection. We do not recommend
running this in the background as you need to see the logs and therefore when the databases are
ready to be used.

Once installed and running ... 
 
