from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import os
import logging
import json
from typing import List, Dict, Any, Optional
import hashlib

from p2p_node import P2PNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='permastore.log'
)
logger = logging.getLogger("permastore_server")

# Create FastAPI application
app = FastAPI(
    title="PermaStore API",
    description="Decentralized file storage using blockchain",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration
        config = {
            "upload_dir": "uploads",
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        return config

config = load_config()

# Initialize P2P node
node = P2PNode(
    upload_dir=config["upload_dir"],
    max_file_size=config["max_file_size"]
)

# Request models
class PeerModel(BaseModel):
    url: str = Field(..., description="Peer URL to add to the network")

# Response models
class FileResponse(BaseModel):
    hash: str
    message: str = "File uploaded successfully"

class StatusResponse(BaseModel):
    blockchain_length: int
    peers: List[str]
    last_block: Dict[str, Any]

# API routes
@app.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the PermaStore network"""
    try:
        result = await node.store_file(file)
        return {"hash": result["hash"], "message": "File uploaded successfully"}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_hash}")
async def download_file(file_hash: str):
    """Download a file from the PermaStore network"""
    file_path = node.retrieve_file(file_hash)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=file_hash)

@app.post("/peers")
async def add_peer(peer: PeerModel):
    """Add a peer to the PermaStore network"""
    if node.network.add_peer(peer.url):
        return {"message": f"Peer added: {peer.url}"}
    raise HTTPException(status_code=400, detail="Failed to add peer")

@app.delete("/peers/{peer_url}")
async def remove_peer(peer_url: str):
    """Remove a peer from the PermaStore network"""
    node.network.remove_peer(peer_url)
    return {"message": f"Peer removed: {peer_url}"}

@app.get("/peers")
async def get_peers():
    """Get all peers in the PermaStore network"""
    return {"peers": list(node.network.peers)}

@app.post("/sync")
async def sync_files():
    """Synchronize files with peers"""
    result = node.network.sync_files()
    return result

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get status information about the node"""
    return {
        "blockchain_length": len(node.blockchain.chain),
        "peers": list(node.network.peers),
        "last_block": node.blockchain.get_last_block()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

# Main entry point
if __name__ == "__main__":
    logger.info(f"Starting PermaStore server on {config['host']}:{config['port']}")
    uvicorn.run(
        "server:app", 
        host=config["host"], 
        port=config["port"], 
        reload=config["debug"]
    )