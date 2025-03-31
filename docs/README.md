# PermastoreIt (Alpha) Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Standard Installation](#standard-installation)
   - [Docker Installation](#docker-installation)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
   - [File Operations](#file-operations)
   - [Peer Management](#peer-management)
   - [System Status](#system-status)
6. [Core Components](#core-components)
   - [Server](#server)
   - [P2P Node](#p2p-node)
   - [Blockchain](#blockchain)
   - [Network](#network)
7. [Storage Structure](#storage-structure)
8. [Security Considerations](#security-considerations)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)
11. [Development Guide](#development-guide)
12. [Best Practices](#best-practices)

## Introduction

PermastoreIt is a decentralized file storage protocol that uses blockchain technology to track file transactions and peer-to-peer networking for file distribution. It provides a reliable way to store and retrieve files across a network of nodes, ensuring data persistence and availability.

Key features:
- Content-addressed storage (files are identified by their hash)
- Blockchain-based transaction ledger
- Peer-to-peer file distribution
- Automatic file synchronization between nodes
- Simple HTTP API for file operations

## Architecture Overview

PermastoreIt follows a modular architecture with four main components:

1. **Server**: Provides the HTTP API for interacting with the system
2. **P2P Node**: Orchestrates file storage and blockchain operations
3. **Blockchain**: Maintains a ledger of file transactions
4. **Network**: Handles communication between peers

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│            │     │            │     │            │
│  Client    │────▶│  Server    │────▶│  P2P Node  │
│            │     │            │     │            │
└────────────┘     └────────────┘     └────────────┘
                                           │
                                           │
                                           ▼
                    ┌────────────┐     ┌────────────┐
                    │            │     │            │
                    │  Network   │◀───▶│ Blockchain │
                    │            │     │            │
                    └────────────┘     └────────────┘
```

Files flow through the system as follows:
1. A client uploads a file to a PermastoreIt node via the HTTP API
2. The file is stored locally and its hash is recorded in the blockchain
3. The file is broadcasted to peer nodes in the network
4. Files can be retrieved by their hash from any node in the network

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Optional: Docker and Docker Compose for containerized deployment

### Standard Installation

1. Clone the repository or copy the project files to your server:

```bash
git clone https://github.com/PermstoreIT/PermstoreIt-Alpha.git
cd PERMASTOREIT-ALPHA
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Create necessary directories and files:

```bash
mkdir -p uploads
touch blockchain.json peers.txt permastore_it.log
```

4. Start the server:

```bash
python server.py
```

The server will be available at http://localhost:5000 (or the port specified in your config).

### Docker Installation

1. Ensure Docker and Docker Compose are installed on your system.

2. Clone the repository or copy the project files:

```bash
git clone https://github.com/PermstoreIT/PermstoreIt-Alpha.git
cd PERMASTOREIT-ALPHA
```

3. Build and start the Docker container:

```bash
docker-compose up -d
```

This will build the Docker image and start the container in detached mode. The server will be available at http://localhost:5000.

## Configuration

PermastoreIt is configured via the `config.json` file. Here are the available options:

```json
{
  "upload_dir": "uploads",         // Directory where files are stored
  "max_file_size": 104857600,      // Maximum file size in bytes (100MB)
  "host": "0.0.0.0",               // Host to bind the server to
  "port": 5000,                    // Port to listen on
  "debug": false,                  // Enable debug mode
  "allowed_file_types": [          // Allowed MIME types for file uploads
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
    "application/json",
    "application/octet-stream"
  ],
  "blockchain": {
    "storage_file": "blockchain.json",  // File to store blockchain data
    "min_transactions_per_block": 1     // Minimum transactions per block
  },
  "network": {
    "retry_limit": 3,              // Number of retries for network operations
    "request_timeout": 30,         // Timeout for network requests (seconds)
    "sync_interval": 3600          // Interval for file synchronization (seconds)
  },
  "logging": {
    "level": "INFO",               // Logging level
    "file": "permastore_it.log",   // Log file
    "max_size": 10485760,          // Maximum log file size (10MB)
    "backup_count": 5              // Number of log file backups
  }
}
```

## API Reference

PermastoreIt provides a RESTful API for interacting with the system. All API endpoints return JSON responses.

### File Operations

#### Upload a File

```
POST /upload
```

Upload a file to the PermastoreIt network.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Form data with a "file" field containing the file to upload

**Response:**
```json
{
  "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "message": "File uploaded successfully"
}
```

**Status Codes:**
- 200: File uploaded successfully
- 400: Invalid request (missing file, etc.)
- 413: File too large
- 500: Internal server error

#### Download a File

```
GET /download/{file_hash}
```

Download a file from the PermastoreIt network by its hash.

**Request:**
- Method: GET
- URL Parameters: file_hash - The hash of the file to download

**Response:**
- The file content with appropriate Content-Type and Content-Disposition headers

**Status Codes:**
- 200: File found and returned
- 404: File not found
- 500: Internal server error

### Peer Management

#### Add a Peer

```
POST /peers
```

Add a peer to the PermastoreIt network.

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
```json
{
  "url": "http://peer-host:5000"
}
```

**Response:**
```json
{
  "message": "Peer added: http://peer-host:5000"
}
```

**Status Codes:**
- 200: Peer added successfully
- 400: Invalid peer URL or unable to connect to peer
- 500: Internal server error

#### Remove a Peer

```
DELETE /peers/{peer_url}
```

Remove a peer from the PermastoreIt network.

**Request:**
- Method: DELETE
- URL Parameters: peer_url - The URL of the peer to remove

**Response:**
```json
{
  "message": "Peer removed: http://peer-host:5000"
}
```

**Status Codes:**
- 200: Peer removed successfully
- 500: Internal server error

#### List Peers

```
GET /peers
```

Get a list of all peers in the PermastoreIt network.

**Request:**
- Method: GET

**Response:**
```json
{
  "peers": [
    "http://peer1:5000",
    "http://peer2:5000"
  ]
}
```

**Status Codes:**
- 200: Peers retrieved successfully
- 500: Internal server error

#### Synchronize Files

```
POST /sync
```

Synchronize files with peers in the network.

**Request:**
- Method: POST

**Response:**
```json
{
  "synced": 3,
  "failed": 1,
  "peers": {
    "http://peer1:5000": {
      "status": "success",
      "files": 2
    },
    "http://peer2:5000": {
      "status": "success",
      "files": 1
    },
    "http://peer3:5000": {
      "status": "failed",
      "files": 0
    }
  }
}
```

**Status Codes:**
- 200: Synchronization completed
- 500: Internal server error

### System Status

#### Get Status

```
GET /status
```

Get status information about the node.

**Request:**
- Method: GET

**Response:**
```json
{
  "blockchain_length": 10,
  "peers": [
    "http://peer1:5000",
    "http://peer2:5000"
  ],
  "last_block": {
    "index": 10,
    "timestamp": 1648500000,
    "transactions": [
      {
        "data": {
          "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "filename": "example.txt",
          "content_type": "text/plain",
          "size": 1024
        },
        "timestamp": 1648499900
      }
    ],
    "previous_hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
  }
}
```

**Status Codes:**
- 200: Status retrieved successfully
- 500: Internal server error

#### Health Check

```
GET /health
```

Check if the node is healthy.

**Request:**
- Method: GET

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- 200: Node is healthy
- 500: Node is unhealthy

## Core Components

### Server

The server component (implemented in `server.py`) provides the HTTP API for interacting with the PermastoreIt network. It handles incoming requests, routes them to the appropriate components, and returns responses to clients.

Key responsibilities:
- Expose RESTful API endpoints
- Handle CORS and other HTTP-related concerns
- Parse and validate requests
- Format and send responses
- Handle errors and exceptions

### P2P Node

The P2P Node component (implemented in `p2p_node.py`) orchestrates file storage and blockchain operations. It serves as a bridge between the server, blockchain, and network components.

Key responsibilities:
- Store and retrieve files from the local filesystem
- Calculate file hashes
- Record file transactions in the blockchain
- Broadcast files to peers via the network component

### Blockchain

The blockchain component (implemented in `blockchain.py`) maintains a ledger of file transactions. It uses a simple blockchain structure where each block contains a list of transactions, a timestamp, and a reference to the previous block.

Key responsibilities:
- Create new blocks in the blockchain
- Add transactions to the current block
- Calculate block hashes
- Persist blockchain data to disk
- Load blockchain data from disk

### Network

The network component (implemented in `network.py`) handles communication between peers in the PermaStore network. It is responsible for sending and receiving files, and maintaining a list of known peers.

Key responsibilities:
- Maintain a list of peers
- Add and remove peers
- Broadcast files to peers
- Synchronize files with peers
- Validate peers

## Storage Structure

PermastoreIt uses a content-addressed storage system, where files are identified by their hash. The storage directory structure is as follows:

```
uploads/
├── e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
├── 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
└── ...
```

Each file is stored with its hash as the filename, making it easy to locate and retrieve files by their hash.

The blockchain data is stored in the `blockchain.json` file, which contains the complete blockchain including all transactions. The list of known peers is stored in the `peers.txt` file, with one peer URL per line.

## Security Considerations

PermastoreIt includes several security features to ensure the integrity and availability of stored files:

1. **Content Addressing**: Files are identified by their hash, making it easy to verify file integrity
2. **Hash Verification**: When downloading files from peers, the hash is verified to ensure the file hasn't been tampered with
3. **File Size Limits**: Maximum file size is enforced to prevent denial-of-service attacks
4. **MIME Type Validation**: Only allowed file types can be uploaded
5. **Retry Mechanism**: Failed network operations are retried to ensure reliability

For production deployments, consider the following additional security measures:

1. **HTTPS**: Use a reverse proxy (like Nginx) to terminate SSL/TLS
2. **Authentication**: Implement an authentication mechanism to control access to the API
3. **Rate Limiting**: Limit the number of requests per IP address to prevent abuse
4. **Input Validation**: Validate all input parameters to prevent injection attacks
5. **Logging and Monitoring**: Monitor logs for suspicious activity

## Monitoring and Maintenance

PermastoreIt includes logging and monitoring features to help you keep track of system health and performance.

### Logging

Logs are written to the `permastore_it.log` file by default. The logging level and other options can be configured in the `config.json` file.

Example log output:
```
2025-03-30 12:34:56,789 - p2p_node - INFO - File stored successfully: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
2025-03-30 12:34:56,890 - network - INFO - File broadcast successful to http://peer1:5000
2025-03-30 12:34:56,901 - network - WARNING - Attempt 1 failed to send file to http://peer2:5000: Connection refused
```

### Health Checks

The `/health` endpoint can be used to check if the node is healthy. This endpoint returns a 200 OK response if the node is healthy, and a 500 Internal Server Error response if the node is unhealthy.

You can use a monitoring tool like Prometheus or Nagios to periodically check this endpoint and alert you if the node becomes unhealthy.

### Backup and Recovery

To backup PermastoreIt data, you should regularly backup the following files:

1. `blockchain.json`: Contains the blockchain data
2. `peers.txt`: Contains the list of known peers
3. `uploads/` directory: Contains the stored files

For Docker deployments, these files are mounted as volumes, so they persist even if the container is removed. For standard deployments, you can use any backup tool to regularly backup these files.

## Troubleshooting

### Common Issues

1. **File Not Found**: If a file cannot be found when trying to download it, check if the file exists in the `uploads` directory. If not, try synchronizing with peers using the `/sync` endpoint.

2. **Peer Connection Failed**: If you're unable to connect to a peer, check if the peer is running and accessible from your network. Try adding the peer again using the `/peers` endpoint.

3. **Server Won't Start**: If the server won't start, check the logs for error messages. Common issues include port conflicts, missing dependencies, or configuration errors.

### Diagnostic Steps

1. **Check Logs**: The first step in troubleshooting is to check the logs in the `permastore.log` file. Look for ERROR or WARNING messages that might indicate the source of the problem.

2. **Check Status**: Use the `/status` endpoint to check the current status of the node. This can provide information about the blockchain and peers.

3. **Check Health**: Use the `/health` endpoint to check if the node is healthy. If this endpoint returns a 500 error, the node is unhealthy.

4. **Check Configuration**: Verify that the `config.json` file is correctly formatted and contains valid values.

5. **Check Network**: Verify that the node can connect to peers by trying to access the peer URLs directly.

## Development Guide

### Project Structure

```
PERMASTOREIT-ALPHA/
│
├── server.py                # Main entry point and API routes
├── p2p_node.py              # P2P node implementation
├── blockchain.py            # Blockchain implementation
├── network.py               # Network communication
├── config.json              # Configuration file
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Docker Compose setup
│
├── uploads/                 # Directory for stored files
├── blockchain.json          # Persistent blockchain storage
├── peers.txt                # List of known peers
└── permastore_it.log           # Application logs
```

### Adding New Features

When adding new features to PermaStore, follow these guidelines:

1. **Modular Design**: Keep components separate and focused on specific responsibilities
2. **Error Handling**: Always handle errors and exceptions gracefully
3. **Logging**: Add appropriate logging statements to help with debugging
4. **Testing**: Write tests for new features
5. **Documentation**: Update this documentation to reflect the new features

### Extending the API

To add a new API endpoint:

1. Add a new route handler function in `server.py`:

```python
@app.get("/new-endpoint")
async def new_endpoint():
    # Implement the endpoint logic
    return {"message": "New endpoint"}
```

2. Update the API documentation in this document

### Extending the Blockchain

To add new transaction types or blockchain features, modify the `blockchain.py` file. For example, to add a new transaction type:

1. Update the `add_transaction` method to handle the new transaction type
2. Update the blockchain data structure if necessary
3. Update the `_save_chain` and `_load_chain` methods if necessary

## Best Practices

### Deployment

1. **Use Docker**: Docker simplifies deployment and ensures consistency across environments
2. **Use a Reverse Proxy**: A reverse proxy like Nginx can handle SSL/TLS, load balancing, and other concerns
3. **Configure Firewalls**: Ensure that only necessary ports are exposed
4. **Use Environment-Specific Configuration**: Use different configuration files for development, testing, and production
5. **Set Up Monitoring**: Use a monitoring tool to keep track of system health

### Network Configuration

1. **Peer Discovery**: Implement a peer discovery mechanism to automatically find peers
2. **NAT Traversal**: Consider using a technique like NAT traversal to allow nodes behind NATs to communicate
3. **Connection Pooling**: Implement connection pooling to reduce the overhead of establishing new connections
4. **Backup Peers**: Maintain a list of backup peers in case primary peers are unavailable
5. **Geographic Distribution**: Distribute peers geographically to improve resilience

### File Management

1. **Content Deduplication**: Avoid storing duplicate files by checking if a file with the same hash already exists
2. **Garbage Collection**: Implement a garbage collection mechanism to remove unused files
3. **File Validation**: Validate files before storing them to ensure they meet requirements
4. **Incremental Backups**: Implement incremental backups to reduce backup size
5. **File Versioning**: Consider implementing file versioning to track changes over time
