# MavTrace-v0.1.0
MavTrace is a pcap capture tool. This tool logs into a remote host machine captures trace for 30 seconds and downloads the trace to local machine and deletes the trace from host.
MavTrace uses paramiko for ssh and sftp functions. 
MavTrace accepts ssh password authentication by user input and currently does not support public key based authentication.
