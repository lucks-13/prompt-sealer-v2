import hashlib
import hmac
import json
from pathlib import Path
from prompt_sealer.crypto import seal_text, unseal_text, stamp_note
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

def read_prompt(location : Path) -> bytes:
    if not location.exists():
        raise FileNotFoundError("Prompt file does not exist.")
    return location.read_bytes()

def derive_prompt_key(machine_secret : bytes, file_id : bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=file_id, info=b"prompt-sealer-prompt-key").derive(machine_secret)

def make_code_b(machine_secret : bytes, file_id : bytes) -> str:
    message = b"prompt-sealer-code-b:" + file_id
    return hmac.new(machine_secret, message, hashlib.sha256).hexdigest()[:32].upper()

def derive_code_b(code_b : str, file_id : bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=file_id, info=b"prompt-sealer-code-b-wrap").derive(code_b.strip().upper().encode("utf-8"))

def wrap_p_key(p_key : bytes, code_b : str, file_id : bytes) -> bytes:
    wrap_key = derive_code_b(code_b, file_id)
    nonce, ciphertext = seal_text(p_key, wrap_key, file_id)
    return nonce + ciphertext

def unwrap_p_key(w_key : bytes, code_b : str, file_id : bytes) -> bytes:
    wrap_key = derive_code_b(code_b, file_id)
    return unseal_text(w_key[12:], wrap_key, w_key[:12], file_id)

def make_code_a(challenge : bytes) -> str:
    return hashlib.sha256(b"prompt-sealer-code-a:" + challenge.hex().encode("ascii")).hexdigest()[:32].upper()

def hash_code_a(code_a : str) -> str:
    return hashlib.sha256(code_a.strip().upper().encode("utf-8")).hexdigest()
      
def seal_prompt(prompt : bytes, key : bytes, file_id : bytes, expires : int, challenge : bytes, signing_key, machine_secret : bytes) -> bytes:
    code_a = make_code_a(challenge)
    code_a_h = hash_code_a(code_a)
    code_b = make_code_b(machine_secret, file_id)
    wrapped_key = wrap_p_key(key, code_b, file_id).hex()
    record = {
        "version" : 1,
        "file_id" : file_id.hex(),
        "expires" : expires,
        "challenge" : challenge.hex(),
        "code_a_hash" : code_a_h,
        "wrapped_key" : wrapped_key
    }
    s_data = json.dumps(record, sort_keys=True, separators=(",",":")).encode("utf-8")
    record["signature"] = stamp_note(signing_key, s_data).hex()
    return json.dumps(record, sort_keys=True, separators=(",",":")).encode("utf-8")

def attach_code_b(blob : bytes, p_key : bytes, code_b : str) -> bytes:
    record = json.loads(blob.decode("utf-8"))
    file_id = bytes.fromhex(record["file_id"])
    record["wrapped_key"] = wrap_p_key(p_key, code_b, file_id).hex()
    return json.dumps(record, sort_keys=True, separators=("," ,":")).encode("utf-8")

def unseal_prompt(blob : bytes, key : bytes) -> bytes:
    record = json.loads(blob.decode("utf-8"))
    extra = json.dumps(
        {
            "version" : record["version"],
            "file_id" : record["file_id"],
            "expires" : record["expires"],
            "challenge" : record["challenge"],
            "code_a_hash" : record["code_a_hash"],
            "bootstrap" : record["bootstrap"]
        },
        sort_keys=True,
        separators=(",", ":")
        ).encode("utf-8")    
    return unseal_text(bytes.fromhex(record["ciphertext"]), key, bytes.fromhex(record["nonce"]), extra)

def seal_file(source : Path, dest : Path, key : bytes, file_id : bytes, expires : int, challenge : bytes, signing_key, machine_secret : bytes) -> None:
    sealed = seal_prompt(read_prompt(source), key, file_id, expires, challenge, signing_key, machine_secret)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(sealed)