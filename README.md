# ssh-gamebox

A terminal-based mini-arcade thing built with Python served directly over SSH.

Connect directly from your terminal.

```bash
ssh -p 59444 play@ssh.thorndev.me
```
# DNS troubleshooting:
**"No such host is known."** try:

Linux/MacOS:
```bash
ssh -p 59444 play@$(dig @1.1.1.1 AAAA ssh.thorndev.me +short | tail -n1)
```
or 
```bash
ssh -p 59444 play@$(dig @1.1.1.1 A ssh.thorndev.me +short | tail -n1)
```
Windows:
```
nslookup ssh.thorndev.me 1.1.1.1
ssh -p 59444 play@<address from above>
```

This forces ssh to use Cloudflare's DNS servers to resolve ssh.thorndev.me .

**"REMOTE HOST IDENTIFICATION HAS CHANGED"**

The server's key was regenerated. Remove the old one and reconnect:
```bash
ssh-keygen -R "[ssh.thorndev.me]:59444"
```
**Garbled colors or boxes**
Use a modern terminal with 256-color support, or run `export TERM=xterm-256color` first.
