from tempfile import TemporaryDirectory
from tqdm import tqdm
from warnings import warn
from zipfile import ZipFile, ZIP_DEFLATED
import os
import paramiko

class Piwakawaka(object):
    """
    A SSH and SFTP client that can execute commands on Piwakwaka and send files.
    """
    def __init__(self, hostname="167.99.90.75", password=None) -> None:
        """
        Create a SSH and SFTP client with Piwakwaka. The client searches for any local RSA key files and then attempt to use a password if no keys are found. See https://docs.paramiko.org/en/2.4/api/client.html#paramiko.client.SSHClient.connect for more details.
        """
        client = paramiko.SSHClient()
        # Set it to automatically add the host to known hosts
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Try connecting as any of the admin users
        acceptable_usernames = {"sar":"Sam", "mja":"Mitch", "dsw":"Dean", "tml":"Tom", "jst":"Josh"}
        for acceptable_username in acceptable_usernames:
            try:
                client.connect(hostname=hostname, username=acceptable_username, password=password)
                username = acceptable_username
                print(f"Welcome {acceptable_usernames[username]}!")
                break
            except:
                continue
        
        if not username:
            warn("Unfortunately, your identity could not be verified though an SSH key or password with any of the admin usernames on Piwakawaka")
            return

        self.client = client
        self.sftp_client = client.open_sftp()
    
    def close(self) -> None:
        """
        Close the SSH connection with Piwakwaka
        """
        self.client.close()
        self.sftp_client.close()

    def execute_command(self, command:str, show_output=True) -> None:
        """
        Execute a command on Pikwakwawaka
        """
        # Execute the command
        _, ssh_stdout, ssh_stderr = self.client.exec_command(command)
        # Display the output
        output = ''
        for line in ssh_stdout.readlines():
            output += line
        if output and show_output:
            print(output)

        error = ''
        for line in ssh_stderr.readlines():
            error += line
        if error:
            warn(f"The command: {command} could not be executed due to: \n{error}")
    
    def transfer_file(self, localpath:str, remotepath:str, show_progress=True) -> None:
        """
        Upload a local file to the given remote filepath on Piwakawaka
        """
        def printTotals(transferred, toBeTransferred):
            transferred = transferred/1e6 # in MB now
            toBeTransferred = toBeTransferred/1e6 # in MB now
            # Keep the progress bar if the transfer has finished by not overwriting it!
            if transferred/toBeTransferred == 1:
                end="\n"
            else:
                end="\r"
            print(f"Progress: {100*transferred/toBeTransferred:.2f}%\t Transferred: {transferred:.2f} / {toBeTransferred:.2f} MB", end=end)
            
        if show_progress:
            callback=printTotals
        else:
            callback=None
        
        _ = self.sftp_client.put(localpath, remotepath, callback=callback, confirm=True)
        

    def transfer_directory(self, local_directory:str, remote_directory:str, show_progress=True, zip_compression=ZIP_DEFLATED) -> None:
        """
        Zip a whole diretory and then send it to the remote filepath on Piwakawaka and uncompress
        """    
        # Check the directory specified exists
        if not os.path.exists(local_directory):
            warn(f"The local directory {local_directory} does not exists.")
            return
        
        # Complete the walk through the top 3 nested subdirectories to add files
        all_files = []
        for root, subdirs, files in os.walk(local_directory):
            for file in files:
                all_files.append((os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(local_directory, '..'))))

            for subdir in subdirs:
                for root, subdirs, files in os.walk(subdir):
                    for file in files:
                        all_files.append((os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(local_directory, '..'))))

                    for subdir in subdirs:
                        for root, subdirs, files in os.walk(subdir):
                            for file in files:
                                all_files.append((os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(local_directory, '..'))))
        
        if len(all_files) == 0:
            warn(f"No files were found in the top 3 subdirectories of {local_directory}. Please extend this, otherwise the zip file has been skipped.")
            return
        
        # Make the zip file
        temp_dir = TemporaryDirectory()
        local_path = os.path.join(temp_dir.name, "zipped_dir.zip")
        with ZipFile(local_path, "w", compression=zip_compression) as zip:
            for filepath, filename in tqdm(all_files, "Creating ZIP file", total=len(all_files), leave=False, dynamic_ncols=True):
                zip.write(filepath, arcname=filename)

        # Upload the zip file
        remote_path = "{}zipped_dir.zip".format(remote_directory if remote_directory.endswith("/") else remote_directory + "/")
        self.transfer_file(local_path, remote_path, show_progress)
        # Unzip and overwrite on the server
        self.execute_command(f"unzip -o {remote_path} -d {remote_directory}..")
        # Delete the zip files on the server and local path
        self.execute_command(f"rm {remote_path}")
        temp_dir.cleanup()

