import hashlib
import json
import time
import os
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger("blockchain")

class Blockchain:
    def __init__(self, storage_file: str = "blockchain.json"):
        self.storage_file = storage_file
        self.chain = []
        self.current_transactions = []
        
        # Try to load existing blockchain
        self._load_chain()
        
        # Create genesis block if chain is empty
        if not self.chain:
            logger.info("Creating genesis block")
            self.create_block(previous_hash="1")
            self._save_chain()
    
    def create_block(self, previous_hash: str) -> Dict[str, Any]:
        """Create a new block in the blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash,
        }
        
        # Clear current transactions and add block to chain
        self.current_transactions = []
        self.chain.append(block)
        
        # Save chain to disk
        self._save_chain()
        
        logger.info(f"Created block {block['index']}")
        return block
    
    def add_transaction(self, transaction: Dict[str, Any]) -> int:
        """Add a new transaction to the list of transactions"""
        self.current_transactions.append({
            'data': transaction,
            'timestamp': time.time()
        })
        
        # Create a new block if there are transactions
        if len(self.current_transactions) >= 1:
            last_block = self.chain[-1]
            self.create_block(self.hash(last_block))
        
        logger.info(f"Added transaction: {transaction.get('hash', '')}")
        return self.get_last_block()['index'] if self.chain else None
    
    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """Create a SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def get_last_block(self) -> Optional[Dict[str, Any]]:
        """Get the last block in the blockchain"""
        return self.chain[-1] if self.chain else None
    
    def _save_chain(self) -> None:
        """Save the blockchain to disk"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.chain, f)
        except Exception as e:
            logger.error(f"Failed to save blockchain: {str(e)}")
    
    def _load_chain(self) -> None:
        """Load the blockchain from disk"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.chain = json.load(f)
                logger.info(f"Loaded blockchain with {len(self.chain)} blocks")
            except Exception as e:
                logger.error(f"Failed to load blockchain: {str(e)}")
                self.chain = []