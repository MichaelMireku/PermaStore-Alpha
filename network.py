import requests
import os
import logging
import time
from typing import Set, Dict, Any, Optional
import hashlib

# Configure logging
logger = logging.getLogger("network")

class Network:
    def __init__(self, peer_file: str = "peers.txt", retry_limit: int = 3):
        self.peers: Set[str] = set()
        self.peer_file = peer_file
        self.retry_limit = retry_limit
        
        # Load existing peers
        self._load_peers()
    
    def add_peer(self, peer_url: str) -> bool:
        """Add a peer to the network"""
        if not peer_url.startswith(('http://', 'https://')):
            peer_url = f"http://{peer_url}"
            
        # Validate peer before adding
        if self._validate_peer(peer_url):
            self.peers.add(peer_url)
            self._save_peers()
            logger.info(f"Added peer: {peer_url}")
            return True
        return False
    
    def remove_peer(self, peer_url: str) -> None:
        """Remove a peer from the network"""
        if peer_url in self.peers:
            self.peers.remove(peer_url)
            self._save_peers()
            logger.info(f"Removed peer: {peer_url}")
    
    def broadcast_file(self, file_path: str) -> Dict[str, Any]:
        """Broadcast a file to all peers"""
        results = {"success": [], "failed": []}
        
        for peer in self.peers:
            success = False
            
            for attempt in range(self.retry_limit):
                try:
                    with open(file_path, "rb") as f:
                        files = {"file": f}
                        response = requests.post(
                            f"{peer}/upload", 
                            files=files, 
                            timeout=30
                        )
                        
                    if response.status_code == 200:
                        results["success"].append(peer)
                        success = True
                        logger.info(f"File broadcast successful to {peer}")
                        break
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Attempt {attempt+1} failed to send file to {peer}: {str(e)}")
                    time.sleep(2)  # Wait before retry
            
            if not success:
                results["failed"].append(peer)
                logger.error(f"Failed to broadcast file to {peer} after {self.retry_limit} attempts")
        
        return results
    
    def sync_files(self) -> Dict[str, Any]:
        """Sync files with all peers"""
        results = {"synced": 0, "failed": 0, "peers": {}}
        
        for peer in self.peers:
            peer_result = {"status": "failed", "files": 0}
            
            try:
                response = requests.get(f"{peer}/status", timeout=10)
                if response.status_code == 200:
                    last_block = response.json().get("last_block", {})
                    transactions = last_block.get("transactions", [])
                    
                    for tx in transactions:
                        file_hash = tx.get("data", {}).get("hash")
                        if file_hash:
                            if self._download_file(peer, file_hash):
                                peer_result["files"] += 1
                    
                    peer_result["status"] = "success"
                    results["synced"] += peer_result["files"]
                    logger.info(f"Successfully synced with {peer}, got {peer_result['files']} files")
                    
                else:
                    results["failed"] += 1
                    logger.warning(f"Failed to sync with {peer}: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                results["failed"] += 1
                logger.error(f"Failed to sync with {peer}: {str(e)}")
            
            results["peers"][peer] = peer_result
        
        return results
    
    def _download_file(self, peer: str, file_hash: str) -> bool:
        """Download a file from a peer"""
        file_path = os.path.join("uploads", file_hash)
        
        # Skip if file already exists
        if os.path.exists(file_path):
            return True
            
        try:
            response = requests.get(
                f"{peer}/retrieve/{file_hash}", 
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Verify hash
                with open(file_path, "rb") as f:
                    content = f.read()
                    computed_hash = hashlib.sha256(content).hexdigest()
                
                if computed_hash != file_hash:
                    logger.warning(f"Hash mismatch for file {file_hash} from {peer}")
                    os.remove(file_path)
                    return False
                
                logger.info(f"Downloaded {file_hash} from {peer}")
                return True
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {file_hash} from {peer}: {str(e)}")
        
        return False
    
    def _validate_peer(self, peer_url: str) -> bool:
        """Validate a peer URL by checking its status endpoint"""
        try:
            response = requests.get(f"{peer_url}/status", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _save_peers(self) -> None:
        """Save peers to disk"""
        try:
            with open(self.peer_file, 'w') as f:
                for peer in self.peers:
                    f.write(f"{peer}\n")
        except Exception as e:
            logger.error(f"Failed to save peers: {str(e)}")
    
    def _load_peers(self) -> None:
        """Load peers from disk"""
        if os.path.exists(self.peer_file):
            try:
                with open(self.peer_file, 'r') as f:
                    for line in f:
                        peer = line.strip()
                        if peer:
                            self.peers.add(peer)
                logger.info(f"Loaded {len(self.peers)} peers")
            except Exception as e:
                logger.error(f"Failed to load peers: {str(e)}")