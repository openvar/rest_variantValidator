import os
import subprocess
import time
from unittest import TestCase
import requests

class TestInternalServers(TestCase):
    @classmethod
    def setUpClass(cls):
        # Set the PORT environment variable for WSGI server
        os.environ['PORT'] = '8002'

        # Start the WSGI server as a separate process
        cls.wsgi_server_process = subprocess.Popen(['python', 'rest_VariantValidator/wsgi.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(60)

        # Check if the WSGI server started correctly
        if cls.wsgi_server_process.poll() is not None:
            stdout, stderr = cls.wsgi_server_process.communicate()
            print(f"WSGI Server stdout: {stdout}")
            print(f"WSGI Server stderr: {stderr}")
            raise RuntimeError('WSGI server failed to start')

        # Set the PORT environment variable for APP server
        os.environ['PORT'] = '5002'

        # Start the app server as a separate process
        cls.app_server_process = subprocess.Popen(['python', 'rest_VariantValidator/app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(60)

        # Check if the app server started correctly
        if cls.app_server_process.poll() is not None:
            stdout, stderr = cls.app_server_process.communicate()
            print(f"App Server stdout: {stdout}")
            print(f"App Server stderr: {stderr}")
            raise RuntimeError('App server failed to start')

    @classmethod
    def tearDownClass(cls):
        # Terminate the WSGI server process
        cls.wsgi_server_process.terminate()
        cls.wsgi_server_process.wait(timeout=60)
        wsgi_exit_code = cls.wsgi_server_process.poll()
        print(f"WSGI Server Exit Code: {wsgi_exit_code}")

        # Terminate the app server process
        cls.app_server_process.terminate()
        cls.app_server_process.wait(timeout=60)
        app_exit_code = cls.app_server_process.poll()
        print(f"App Server Exit Code: {app_exit_code}")

        if wsgi_exit_code != 0:
            wsgi_pid = cls.wsgi_server_process.pid
            # Forcefully kill all processes listening on port 8002
            subprocess.run(['pkill', '-f', f':{wsgi_pid}'])
            assert wsgi_exit_code == 0, f"WSGI Server termination failed with exit code {wsgi_exit_code}"
        else:
            assert wsgi_exit_code == 0, f"WSGI Server termination failed with exit code {wsgi_exit_code}"
        if app_exit_code != 0:
            app_pid = cls.app_server_process.pid
            # Forcefully kill all processes listening on port 5002
            subprocess.run(['pkill', '-f', f':{app_pid}'])
            assert app_exit_code == 0, f"App Server termination failed with exit code {app_exit_code}"
        else:
            assert app_exit_code == 0, f"App Server termination failed with exit code {app_exit_code}"

    def check_server(self, endpoint, port):
        # http://127.0.0.1:8000/hello/?content-type=application%2Fjson
        response = requests.get(f'http://127.0.0.1:{port}/{endpoint}/?content-type=application%2Fjson')
        assert response.status_code == 200
        assert "status" in response.json().keys()

    def test_wsgi_internal_server(self):
        # Check the WSGI server
        self.check_server('hello', 8002)

    def test_app_server(self):
        # Check the app server
        self.check_server('hello', 5002)