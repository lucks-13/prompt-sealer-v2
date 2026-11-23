# Prompt Sealer V2

Hello everyone! This project is one of my biggest project where technically this works as i expected but not as i expected. So this this concludes my version 2.

# What my project does.
A python cli tool build with typer which encrypts prompts. so that your personal prompts stays private. A own offline ai model is included

# My Motive

Consider two persons A and B, Person A wants to send a prompt which he use daily to Person B but if he shares it the prompt goes public and anyone can use it. so what my project does is. Person A installs my cli project and encrypts the prompt so it gives a encrypted file, now Person A shares that file to person B, now person B cannot read it coz its encrypted, now person B shares the encrypted file to ai { it could be anything } now ai scans that entire file and gives Access code A, now Person B shares the code to Person A then Person A sends them back to cli everthing is machine embedded so if we delete and reinstall cli even on the same machine the code changes, so after giving them cli gives Access code B, Now the final part the Access code B is shared to the ai and now ai can access the file, all these flow must happen within the time limit else prompt get deleted.

# Now for the future update

Everything works as expected but there is a major vulnerability which is once ai completed scanning the prompt stays inside ai and also if Person B asks to give the prompt easy to copy, then the ai blindly gives entire prompt. Tried all the methods and everything but still fails so on the version 2 i need to improve them rest all works as i expected.

Version 2 update : Theoritically this project is impossible because all the model belongs to a particular company so they are the admin not the person who sends the prompt so we cant prevent the Person B to not view the prompt when we uses prompt injection so what i did to overcome is using a local model and making cli to guard the prompt, this is atmost best i could do maybe on the version 3 i might find the solution to the problem so we hope for the best.

# How to run this project.

```
git clone https://github.com/lucks-13/prompt-sealer.git
cd prompt-sealer
```
After Installing all the dependency to make sure everything works
```
prompt-sealer --help
```

# Availabe commands.

1. Initialize vault

```
prompt-sealer init
```

2. Check vault validity

```
prompt-sealer check
```

3. To seal a prompt

```
prompt-sealer seal prompt.txt sealed_prompt
```

4. Now Share sealed_prompt file to another person

5. Now authorize the sealed prompt using Access Code A to get Access Code B

```
prompt-sealer authorize-prompt sealed_prompt.json <ACCESS_CODE_A>
```

6. Open chat [ guarded session ]

forcing Person B to use local model where it was guaeded so Person B cannot access the original prompt

```
prompt-sealer chat sealed_prompt.json <ACCESS_CODE_B>
```

7. Now to Destroy the Vault so that existing encrypted prompt become undecryptable

```
prompt-sealer destroy
```

# What I learned.

* Encrypting and Decrypting payload with AES-256-GCM, HKDF-SHA256 and HMAC-SHA256.
* Signing the file using Ed25519.
* Protecting local secrets with windows DPADI [ win32crypt ] and updating state files atomically.
* accessing a local model using ollama

# Ai Disclosure

I used AI alot but not for code generation coz this a very complicated project so technically i cannot build them without using ai { here ai means chatgpt, gemini, claude not ai agent like claude code, codex } so i use ai as learning assistant to understand cryptographic concepts, simplify code structure and troubleshoot errors, while building this project most of the code is written by me and with ai helping me to reason through design trade-offs and debug issues when i got struck.