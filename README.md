# ssh-gamebox

A terminal-based mini-arcade thing built with Python served directly over SSH.

Connect directly from your terminal.

```bash
ssh -p 59444 play@ssh.thorndev.me
```
# DNS troubleshooting:
If you get errors like "No such host is known." try:

```bash
ssh -p 59444 play@$(dig @1.1.1.1 AAAA ssh.thorndev.me +short)
```
This forces ssh to use Cloudflare's DNS servers to resolve thorndev.me .
```
If you still get those errors try :
```bash
ping 2a01:4f9:3080:3192::1966
```