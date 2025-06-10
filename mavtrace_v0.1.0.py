MAVTRACE_VERSION = "0.1.0"
HOSTNAME = "Enter the hostname or IP address of the remote machine: "
USERNAME = "Enter your username: "
FILENAME = "Enter the filename to save the pcap trace: "
#TRACER = "sudo timeout 30 tcpdump -i any -w "
#RMV_FILE = "rm -f "

import paramiko
import getpass
import subprocess
import sys
import time

def main():
    """
    Main function that runs the MavTrace tool.
    Connects to a remote machine using SSH and collects pcap traces.
    """
    # Step 1: Show welcome message
    welcome_message()

    # Step 2: Ask the user for connection details
    print("************************************************************")
    print("*  Please enter the details to connect to the remote host. *")
    print("************************************************************\n")
    hostname = input(HOSTNAME)
    username = input(USERNAME)
    password = getpass.getpass("Enter your password: ")  # Password input is hidden
    filename = input(FILENAME)
    print("\n")

    # Step 3: Check if the remote host is reachable using ping
    print("Verifying if the remote host is reachable...")
    if ping_host(hostname):
        print("*********************************")
        print(f"* Host {hostname} is reachable. *")
        print("*********************************")
    else:
        print("******************************************************************************************************")   
        print(f"* Host {hostname} is not reachable. Please check the connectivity and/or credentials. Exiting...    *")
        print("******************************************************************************************************") 
        sys.exit(1)
    
    # Step 4: Try to connect to the remote host using SSH
    ssh_client = ssh_connect(hostname, username, password)
    if ssh_client:
        print("Successfully connected to the remote host.")
        # Placeholder: You can add code here to run commands or collect traces
    else:
        print("Failed to connect to the remote host. Exiting...")
        sys.exit(1) 

    # Step 5: Collecting pcap traces
  
    print("\n")
    print("Collecting pcap traces...")
    collect_pcap_traces(ssh_client, filename, password)
    #print("Pcap traces collected successfully.\n")

    # Step 6: Download the pcap file from the remote host
    print("\n")
    download_pcap_file(ssh_client, filename)

    # Step 7: Delete the pcap file from the remote host after downloading
    print("\n")
    delete_pcap_file(ssh_client, filename)
    #print("Pcap file deleted from the remote host.\n")  

    # Step 8: Close the SSH connection in 30 seconds
    print("\n")
    if ssh_client:
        close_ssh_connection(ssh_client)
    print("Exiting MavTrace. Goodbye!")


#Function-1 welcome_message, This function prints a welcome message with tool information.
def welcome_message():
    """
    Print a welcome message with tool information.
    """
    print("\n")
    print("******************************************************")
    print("*  MavTrace - A tool for collecting pcap traces      *")
    print("*  Author: Venkat Obulum                             *")
    print(f"*  Welcome to MavTrace Version: {MAVTRACE_VERSION}               *")
    print("******************************************************\n")

#Function-2 ping_host, This function pings the remote host to check if it is reachable.
def ping_host(hostname):
    """
    Ping the remote host to check if it is reachable.
    Returns True if reachable, False otherwise.
    """
    # '-c 2' sends 2 ping requests, output is hidden
    return subprocess.call(['ping', '-c', '2', hostname],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0

#Function-3 ssh_connect, This function establishes an SSH connection to the remote host using Paramiko.
def ssh_connect(hostname, username, password):
    """
    Establish an SSH connection to the remote host using Paramiko.
    Returns the SSH client object if successful, or None if the connection fails.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("\n")
    try:
        print("************************************************************")
        print(f"* Connecting to {hostname} as {username}...               *")       
        print("* Please wait, this may take a few seconds...              *")
        ssh_client.connect(hostname, username=username, password=password)
        print("* Connection successful!                                   *")
        print("************************************************************")
        return ssh_client
    except paramiko.SSHException as e:
        print("************************************************************")
        print(f"* Failed to connect to {hostname}: {e}                    *")
        print("************************************************************")
        return None
    except Exception as e:
        print("************************************************************")
        print(f"* Unexpected error: {e}                                   *")
        print("************************************************************")
        return None
#Function-4 close_ssh_connection, This function closes the SSH connection to the remote host.
def close_ssh_connection(ssh_client):
    """
    Close the SSH connection to the remote host.
    """
    if ssh_client:
        ssh_client.close()
        print("SSH connection closed successfully.")

#Function-5 collect_pcap_traces, This function collects pcap traces from the remote host using tcpdump.
def collect_pcap_traces(ssh_client,filename='filename',password=None):
    """
    Collect pcap traces from the remote host using tcpdump.
    Returns True if successful, False otherwise.
    """
    try:
        # Command to run tcpdump on the remote host
        command = f"sudo timeout 30 tcpdump -i any -w {filename}"
        stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
        
        # If password is required for sudo, send it
        if password:
            stdin.write(password + '\n')
            stdin.flush()
        
        # Wait for the command to complete
        exit_status = stdout.channel.recv_exit_status()
      
        if exit_status in (0,124):

            print(f"Successfully collected pcap traces and saved to {filename}.")
            return True
        else:
            print(f"Failed to collect pcap traces. Command exited with status {exit_status}.")
            print(stderr.read().decode())
            return False
    except Exception as e:
        print(f"An error occurred while collecting pcap traces: {e}")
        return False    
    
#Function-6 download_pcap_file, This function downloads the pcap file from the remote host to the local machine.    
def download_pcap_file(ssh_client, filename):
    """
    Download the pcap file from the remote host to the local machine.
    """
    sftp = ssh_client.open_sftp()
    try:
        sftp.get(filename, filename)
        print(f"Successfully downloaded {filename} to the local machine.")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
    finally:
        sftp.close()

#Function-7 delete_pcap_file, This function deletes the pcap file from the remote host after downloading it.
def delete_pcap_file(ssh_client, filename):
    """
    Delete the pcap file from the remote host after downloading it.
    """
    try:
        command = f"rm -f {filename}"
        ssh_client.exec_command(command)
        print(f"Successfully deleted {filename} from the remote host.")
    except Exception as e:
        print(f"Failed to delete {filename} from the remote host: {e}")

if __name__ == "__main__":
    main()
