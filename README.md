<br />
<p align="center">
  <h1 align="center">Server Connection</h3>
</p>
<br />

## About The Project

Create a SSH and SFTP client with Piwakwaka. The client searches for any local RSA key files and then attempt to use a password if no keys are found. See https://docs.paramiko.org/en/2.4/api/client.html#paramiko.client.SSHClient.connect for more details.

The client has the following functions:
1. ```execute_command``` : Execute a string command in the terminal of the server
2. ```transfer_file``` : Send a sigle file (uncompressed) using SSH to a given path on the server
3. ```transfer_directory``` : Send a whole directory (compressed) using SSH to a given path on the server


## Getting Started

This module requires a version of Python 3.8 or above (tested on 3.9.1) and an environment with the packages listed in ```requirements.txt``` (which can be installed by running ```pip install -r requirements.txt```). 

## Acknowledgements

The class is based upon [Paramiko](https://docs.paramiko.org) version 2.11
