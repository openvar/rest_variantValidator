================
variantValidator
================

variantValidator is a web interface for the hgvs python library. The hgvs library is used
for Accurate validation, mapping and formatting of sequence variants using HGVS 
nomenclature. variantValidator provides a user friendly interface along with additional
functionality and recommendations that assist users ti correctly adhere to HGVS mutation
nomenclature recommendations  


Python requirements
===================

Python 2.7 (VV was built using 2.7.9)


Apache configuration example
============================

<IfModule wsgi_module>

	<VirtualHost *:80>
    	ServerName www.variantvalidator.org
    	ServerAlias variantvalidator.org

   		WSGIScriptAlias / /local/www/htdocs/variantValidator/index.wsgi
    	
    	<Directory /local/www/htdocs/variantValidator/>
        	Order deny,allow
        	Allow from all
    	</Directory>

	</VirtualHost>

 </IfModule>


VariantValidator.org
====================

<https://www.variantvalidator.org>`_.