# Manual

## Operation

To run rest_variantValidator

### Python

```bash
$ python rest_variantValidator/wsgi.py
```

You will be provided with a link which will open rest_variantValidator in your web browser. 


## Swagger documented functions
The rest_variantValidator functions have swagger documentation to help you generate URLs to make direct API calls utilising human readable text-input boxes. 

Once the documented page opens in your web-browser, click the variantvalidator link and the documented functions will appear. 

A web-hosted version of this rest API can be found at [https://rest.variantvalidator.org](https://rest.variantvalidator.org)  

## Direct request
Direct URL calls can be made to the rest-API. The easiest way to create these URLs is to use the swagger documented functions

## In a Docker container

## Apache web-server and mod_wsgi
Mounting rest_variantValidator to an Apache web server requires [mod_wsgi](https://pypi.org/project/mod-wsgi/)

Example [Apache configuration](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html)

```apacheconf
<IfModule wsgi_module>

	WSGIPythonPath <PATH/TO/python>/lib:<PATH/TO/python>/site-packages
	WSGIDaemonProcess rest_variantValidator user=wwwrun group=www threads=5
	WSGIScriptAlias / <PATH/TO>/rest_variantValidator/wsgi.py
	WSGIPythonHome <PATH/TO/python>
    	    	
    	<Directory <PATH/TO>/rest_variantValidator/>
        	WSGIProcessGroup rest_variantValidator
         	WSGIApplicationGroup %{GLOBAL}
         	Order deny,allow
         	Allow from all
     	</Directory>

</IfModule>

CustomLog /local/apache2/log/access_log for_pound

```

## Run in dev mode
To run rest_variantValidator on a dev server

```bash
$ python rest_variantValidator/app.py
```

In a web-browser navkgate to `0.0.0.0:5000`

Exit the app by holding `ctrl + c`

## Additional resources
We are compiling a number of jupyter notebook user guides for rest_variantValidator in [rest_variantValidator_manuals](https://github.com/openvar/rest_variantValidator_manuals)