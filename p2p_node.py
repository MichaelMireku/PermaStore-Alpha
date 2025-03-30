from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import hashlib
import os
import logging
from typing import Dict, Any, Optional
from blockchain import Blockchain
from network import Network

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='permastore_it.log'
)
logger = logging.getLogger("p2p_node")

class P2PNode:
    def __init__(self, upload_dir: str = "uploads", max_file_size: int = 100 * 1024 * 1024):
        self.blockchain = Blockchain()
        self.network = Network()
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size  # 100MB default
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
    async def store_file(self, file: UploadFile) -> Dict[str, Any]:
        """Store a file in the local filesystem and add it to the blockchain"""
        try:
            # Check file size
            file_content = await file.read()
            if len(file_content) > self.max_file_size:
                raise HTTPException(status_code=413, detail="File too large")
                
            # Hash the file content
            file_hash = hashlib.sha256(file_content).hexdigest()
            file_path = os.path.join(self.upload_dir, file_hash)
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Add to blockchain
            self.blockchain.add_transaction({
                "hash": file_hash, 
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(file_content)
            })
            
            # Broadcast to peers
            self.network.broadcast_file(file_path)
            
            logger.info(f"File stored successfully: {file_hash}")
            return {"hash": file_hash}
            
        except Exception as e:
            logger.error(f"Error storing file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error storing file: {str(e)}")
    
    def retrieve_file(self, file_hash: str) -> Optional[str]:
        """Retrieve a file from the local filesystem by its hash"""
        file_path = os.path.join(self.upload_dir, file_hash)
        if os.path.exists(file_path):
            logger.info(f"File retrieved: {file_hash}")
            return file_path
        
        logger.warning(f"File not found: {file_hash}")
        return None

# Create FastAPI application
app = FastAPI(title="PermastoreIt P2P Node", version="1.0.0")
node = P2PNode()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the P2P network"""
    return await node.store_file(file)

@app.get("/retrieve/{file_hash}")
async def retrieve_file(file_hash: str):
    """Retrieve a file from the P2P network by its hash"""
    file_path = node.retrieve_file(file_hash)
    if file_path:
        return FileResponse(file_path, filename=file_hash)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/status")
async def get_status():
    """Get status information about the node"""
    return {
        "blockchain_length": len(node.blockchain.chain),
        "peers": list(node.network.peers),
        "last_block": node.blockchain.get_last_block()
    }