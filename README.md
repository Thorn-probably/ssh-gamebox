# ssh-gamebox

A terminal-based mini-arcade thing built with Python served directly over SSH.

Connect directly from your terminal.

```bash
ssh play@thorndev.me
```
# DNS troubleshooting:
If you get errors like "No such host is known." try:

```bash
ssh play@$(dig @1.1.1.1 AAAA thorndev.me +short)
```
This forces ssh to use Cloudflare's DNS servers to resolve thorndev.me .