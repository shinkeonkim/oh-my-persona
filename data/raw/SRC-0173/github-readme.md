# Port Killer

A simple bash script to kill processes using specific ports.

## Installation

### Option 1: Using the install script
```bash
sudo ./install.sh
```

### Option 2: Using Make
```bash
sudo make install
```

### Option 3: Manual installation
```bash
sudo cp kill-port.sh /usr/local/bin/kill-port
sudo chmod +x /usr/local/bin/kill-port
```

## Usage

After installation, you can use the `kill-port` command from anywhere:

```bash
kill-port 3000
kill-port 8080
```

## Uninstall

### Using Make
```bash
sudo make uninstall
```

### Manual removal
```bash
sudo rm /usr/local/bin/kill-port
```

## What it does

The script:
1. Takes a port number as an argument
2. **Checks for Docker containers using the port and stops them gracefully**
3. Finds any remaining process ID (PID) using that port
4. Kills the process using `kill -9`
5. Provides feedback on success or failure

## Features

- **Docker support**: Automatically detects and stops Docker containers using the specified port
- **Graceful shutdown**: Tries `docker stop` first, then `docker kill` if needed
- **Port validation**: Ensures valid port numbers (1-65535)
- **Error handling**: Comprehensive error checking and user feedback
- **Dependency checking**: Verifies required tools are available