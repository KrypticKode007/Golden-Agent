#!/usr/bin/env python3
"""
Kryptic-Agent: Aligned Weights Encryption Engine
Applies hardware-accelerated AES-256-GCM encryption parameters to tensor vectors
ensuring total alignment with the high-speed native C++ accelerator core.
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class WeightsEncryptionManager:
    def __init__(self, secret_key: bytes = None):
        # Establish structural 256-bit encryption key boundaries
        self.secret_key = secret_key or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.secret_key)

    def pack_and_encrypt_weights(self, weights: list, node_id: str) -> dict:
        """
        Structures the tensor weight arrays, converts to strict binary strings,
        and secures the payload using cryptographically bounded authenticated tags.
        """
        # Formulate explicit payload maps to mirror structural C++ input boundaries
        payload_data = {
            "node_id": node_id,
            "tracking_weights": weights,
            "timestamp_epoch": os.times()[4] if hasattr(os, "times") else 0.0
        }
        
        # Serialize payload cleanly to JSON bytes format
        serialized_payload = json.dumps(payload_data, sort_keys=True).encode('utf-8')
        
        # Nonce generation bounding safety targets
        nonce = os.urandom(12)
        
        # Apply authenticated GCM encryption pipeline
        encrypted_blob = self.aesgcm.encrypt(nonce, serialized_payload, associated_data=None)
        
        # Encode boundaries safely to text characters for secure storage
        return {
            "cipher_text": base64.b64encode(encrypted_blob).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8')
        }

    def decrypt_and_unpack_weights(self, encrypted_manifest: dict) -> list:
        """
        Reverses the isolation barrier, performing tag validation checks
        to extract the matching raw tracking weight configuration vector cleanly.
        """
        try:
            encrypted_blob = base64.b64decode(encrypted_manifest["cipher_text"])
            nonce = base64.b64decode(encrypted_manifest["nonce"])
            
            # Execute hardware decrypted extraction routines
            decrypted_data = self.aesgcm.decrypt(nonce, encrypted_blob, associated_data=None)
            parsed_payload = json.loads(decrypted_data.decode('utf-8'))
            
            return parsed_payload["tracking_weights"]
        except Exception as e:
            raise ValueError(f"Cryptographic boundary breach or parameter mismatch: {str(e)}")

if __name__ == "__main__":
    print("[INFO] Commencing aligned weights encryption processing sequence...")
    
    # Strictly matching the 4-dimension tensor array utilized inside the C++ engine
    target_weights = [0.1523, 0.9942, -0.0431, 0.5512]
    active_node = "KRYPTIC_EDGE_NODE_01"
    
    manager = WeightsEncryptionManager()
    
    # Execute structural packing sequence
    encrypted_packet = manager.pack_and_encrypt_weights(target_weights, node_id=active_node)
    print("[SUCCESS] Tracking weight matrices safely encrypted via AES-256-GCM.")
    
    # Verify parameter loop integrity
    decrypted_weights = manager.decrypt_and_unpack_weights(encrypted_packet)
    print(f"[SUCCESS] Cross-layer validation check complete. Extracted Array: {decrypted_weights}")
      
