import typer
import time
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from prompt_sealer.sealer import seal_file
from prompt_sealer.vault import init_vault, check_vault,destroy_vault, open_vault
from prompt_sealer.crypto import roll_seed
from prompt_sealer.protocol import authorize, read_sealed
from prompt_sealer.bridge import bridge_session

app = typer.Typer(name="prompt-sealer",help="Seal and manage encrypted prompt files.")

vault_path = Path.home() / ".prompt-sealer" / "vault.dat"
state_path = Path.home() / ".prompt-sealer" / "state.json"

local_model_name = os.getenv("prompt_sealer_model", "gemma3:1b")
local_ollama_url = os.getenv("prompt_sealer_ollama_url", "http://localhost:11434/api/chat")

def default_model(sys_p : str, history : list[dict[str, str]], message : str) -> str:
    message = [{"role" : "system", "content" : sys_p}]
    message.extend(history)
    message.append({"role" : "user", "content" : message})
    payload = json.dumps({
        "model" : local_model_name,
        "messages" : message,
        "stream" : False,
    }).encode("utf-8")
    req = urllib.request.Request(local_ollama_url, data = payload, headers = {"Content-Type" : "application/json"}, method = "POST")
    try:
        with urllib.request.urlopen(req, timeout = 120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data.get("message", {}).get("content", "")
        if not content:
            raise RuntimeError("Empty Response from Model.")
        return content
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        ra

@app.callback()
def main():
    pass

@app.command()
def init():
    try:
        init_vault(vault_path)
        typer.echo("Vault initialized successfully.")
    except FileExistsError:
        typer.echo("Vault already exists.")
        raise typer.Exit(code=1)
    
@app.command()
def check():
    try:
        check_vault(vault_path)
        typer.echo("Vault is valid.")
    except FileNotFoundError:
        typer.echo("Vault does not exist.")
        raise typer.Exit(code=1)
    except ValueError:
        typer.echo("Vault is invalid or cannot be unlocked.")
        raise typer.Exit(code=1)
    
@app.command()
def seal(source : Path = typer.Argument(..., help="Prompt file to seal."), dest : Path = typer.Argument(..., help="Output sealed file.")):
    try:
        hour = typer.prompt("Expire Hours", default=0, type=int)
        minute = typer.prompt("Expire Minutes", default=10, type=int)
        tt = hour * 3600 + minute * 60
        if tt <= 0:
            raise ValueError("Expiration Time must be Greater than 0.")
        sign, machine_secret = open_vault(vault_path)
        file_id = roll_seed()
        challenge = roll_seed()
        expires = int(time.time()) + tt
        seal_file(source, dest, roll_seed(), file_id, expires, challenge, sign, machine_secret)
        typer.echo(f"Prompt sealed : {dest}")
        typer.echo("")
        typer.echo("Share this sealed file with Ai :")
        typer.echo(f"File : {dest.resolve()}")
    except (FileNotFoundError, ValueError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)
    
@app.command()
def authorize_prompt(source : Path = typer.Argument(..., help="Sealed prompt file."), code_a : str = typer.Argument(..., help="Access code A.")):
    try:
        sign, machine_secret = open_vault(vault_path)
        record = read_sealed(source)
        file_id = bytes.fromhex(record["file_id"])
        code_b = authorize(source, code_a, machine_secret, file_id, state_path, sign)
        typer.echo(f"Access Code B : {code_b}")
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)
    
@app.command()
def chat(source : Path = typer.Argument(..., help="Sealed prompt file."), code_b : str = typer.Argument(..., help="Access code B.")):
    try:
        session = bridge_session(source, code_b, state_path, default_model)
        typer.echo("Bridge chat started. Type 'exit' or 'quit' to end." )
        while True:
            if session.is_expired():
                typer.echo("Session has expired.")
                break
            msg = typer.prompt("You")
            if msg.strip().lower() in ("exit", "quit"):
                break
            try:
                reply = session.send(msg)
                typer.echo(f"AI : {reply}")
            except ValueError as err:
                typer.echo(str(err))
            if session.is_expired():
                break
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

@app.command()
def destroy(force : bool = typer.Option(False, "--force", help="Delete the vault without confirmation.")):
    if not force:
        confirmed = typer.confirm("Delete the prompt sealer vault ?")
        if not confirmed:
            typer.echo("Vault was not deleted.")
            raise typer.Exit()
    try:
        destroy_vault(vault_path)
        typer.echo("Vault destroyed.")
    except FileNotFoundError:
        typer.echo("Vault does not exist.")
        raise typer.Exit(code=1)
    
if __name__ == "__main__":
    app()