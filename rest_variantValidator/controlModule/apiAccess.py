# Python Modules
from time import sleep
import os
import sys
from datetime import date, datetime, timedelta

# ImportLib
import importlib

# Import connection
# parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# os.sys.path.insert(0,parentdir)
# import variantanalyser
# import variantanalyser.dbControls.dbConnection as dbConnection
import dbConnection
import mysql.connector
from mysql.connector import errorcode

from passlib.apps import custom_app_context as pwd_context

# Error types
class apiAccessException(Exception):
	pass

# Controls the vcf2hgvs modules
class apiAccess:
	_create = """	
	CREATE TABLE IF NOT EXISTS authUsers(
	id INT PRIMARY KEY AUTO_INCREMENT,
	domain VARCHAR(50) NOT NULL,
	password_hash VARCHAR(1000) NOT NULL,
	email VARCHAR(50) NOT NULL,
	added DATE NOT NULL,
	expires DATE NOT NULL,
	termination VARCHAR(5) NOT NULL
	);	
	"""

	_add_user = "INSERT INTO authUsers(domain, password_hash, email, added, expires, termination) VALUES(%s,%s,%s,%s,%s,%s)" 

	_user_defined = "SELECT id FROM authUsers WHERE domain=%s"

	def __init__(self):
		self.data = {}

    # The verify_password() method takes a plain password as argument and returns True if the password is correct or False if not. 
    # This method is called whenever the user provides credentials and they need to be validated.
	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def create(self, username, password):
		try:
			conn = dbConnection.get_connection(username, password).get_connection()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				raise apiAccessException("Incorrect user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				raise apiAccessException("Database does not exist")
			else:
				print(err)
		else:		
			cursor = conn.cursor()
			cursor.execute(self._create)
			cursor.close()
			conn.close()
			return

	def user_defined(self, username, password, domain):
		try:
			conn = dbConnection.get_connection(username, password).get_connection()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				raise apiAccessException("Incorrect user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				raise apiAccessException("Database does not exist")
			else:
				print(err)
		else:		
			cursor = conn.cursor()
			cursor.execute(self._user_defined, (domain,))
			row = []
			row = cursor.fetchone()
			cursor.close()
			conn.close()

	def add_user(self, username, password, domain, keyword, email, duration):		
		try:
			conn = dbConnection.get_connection(username, password).get_connection()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				raise apiAccessException("Incorrect user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				raise apiAccessException("Database does not exist")
			else:
				print(err)
		else:		
			# Get the rest of the required information from stdin
			user_defined = self.user_defined(username, password, domain)
			if user_defined is not None:
				raise apiAccessException('User already exists. Use the /update_user page to extend the license or change password')
			duration = duration.lower()
			warnings = '0'
			# Encrypt the password
			# The hash_password method takes a plain password as argument and stores a hash of it with the user. 
			# This method is called when a new user is registering with the server, or when the user changes the password.
			password_hash = str(keyword)
			password_hash = pwd_context.encrypt(password_hash)
			cursor = conn.cursor()
			added = datetime.now().date()
			try:
				duration_l = duration.split()
				def_time = str(duration_l[1])
				how_long = int(duration_l[0])
				arg_dict = {def_time:how_long}
			except:
				raise apiAccessException('Incorrect format. must be in days e.g. 365 days')
			duration = datetime.now().date() + timedelta(**arg_dict)	 
			# Add data to the table
			cursor.execute(self._add_user, (domain, password_hash, email, added, duration, warnings))
			conn.commit()
			cursor.close()
			conn.close()
			return
