# VariantValidator rest interface Installation

These instructions will allow you to configure the software on Linux and Mac OS X computers.

There are several steps involved in setting up this interface:
* openvar/VariantValidator and openvar/VariantFormatter must be installed, see https://github.com/openvar

## Virtual environment (Python 2.7)

The following packages must be installed to the relevant Python environment (This example uses the VariantValidator environment)
* Note, you may wish to install the necessary VariantFormatter modules into the VVenv (below) so that this tool uses a single Python environment

```
$ conda activate VVenv
$ pip install flask
$ pip install flask-restful
$ pip install flask-restful-swagger
$ pip install flask-log
$ pip install flask-mail
```
The packages required for rest_VaritnaValidator to function are now set up in the environment "VVenv".

## Installing the rest_VariantValidator code

To clone this software from GIT, use:
```
$ git clone https://github.com/openvar/rest_variantValidator.git
```

## Setting the configuration file
in rest_/variantValidator/config, locate the config.ini and fill in the credentials

    [mysql]
    host = 127.0.0.1
    database = validator
    user = vvadmin  
    password = var1ant

    [EntrezID]
    entrezid = <YOUR EMAIL ADDRESS>

    [SeqRepo]
    seqrepo_dir = <PATH TO SEQREPO DIR>

    [UTA]
    uta_url = postgresql://uta_admin:uta_admin@127.0.0.1/uta/<SCHEMA VERSION>

    [Server]
    # For development only, change this to a live server before deployment
    server_url = http/127.0.0.1:5000

    [validatorDB]
    # Note, currently not deployed
    validator_databases = /local/validator_databases

    [pyLiftover]
    # Note, optional
    pyLiftover_dir = /local/pyLiftover/

## Create customised flask_restful_swagger html
Copy the index.html file into /Path/to/Python/site-packages/flask_restful_swagger/static

## Setting up rest_VariantValidator

Configure your server to activate index.wsgi in the same directory as this file

For example, using Apache2 and mod_wsgi

    <IfModule wsgi_module>

	    WSGIPythonPath <PATH TO>lib:<PATH TO>site-packages
	    WSGIDaemonProcess rest_variantValidator user=wwwrun group=www threads=5
	    WSGIScriptAlias / /<PATH TO>/index.wsgi
	    WSGIPythonHome /<PATH TO>/python/2.7.<?>
    	    	
    	<Directory /<PATH TO>/rest_variantValidator/>
        	WSGIProcessGroup rest_variantValidator
         	WSGIApplicationGroup %{GLOBAL}
         	Order deny,allow
         	Allow from all
     	</Directory>

    </IfModule>
