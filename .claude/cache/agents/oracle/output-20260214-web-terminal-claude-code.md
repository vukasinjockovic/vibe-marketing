# Research Report: Serving Claude Code CLI Through a Web Browser

Generated: 2026-02-14

## Summary

The most proven and recommended approach for serving Claude Code's interactive TUI through a web browser is **ttyd + tmux behind an nginx reverse proxy with HTTPS**, optionally combined with **Tailscale** for VPN-level security. Multiple developers have already validated this exact stack for Claude Code specifically. All web terminal tools (ttyd, wetty, gotty) use xterm.js on the frontend, which provides full terminal emulation including colors, cursor positioning, and TUI support -- making Claude Code's Ink/React-based interface work correctly. The ttyd + tmux combination provides session persistence (survive browser tab closes), while Tailscale or Cloudflare Tunnel handles secure remote access without exposing ports.

## Questions Answered

### Q1: Can web terminals run Claude Code's interactive TUI (Ink/React rendering)?
**Answer:** Yes. Claude Code uses Ink (React for terminals) which outputs standard ANSI escape sequences for colors, cursor movement, and layout. All major web terminal tools use xterm.js as their frontend, which is a fully-featured terminal emulator that supports ANSI colors (256 and truecolor), cursor positioning, mouse events, and ncurses-style TUIs. The exact command `ttyd -W claude` has been validated by multiple developers.
**Source:** https://aiengineerguide.com/blog/agentic-cli-browser-ttyd/, https://xtermjs.org/
**Confidence:** High

### Q2: Which tool is the best fit overall?
**Answer:** ttyd is the clear winner for this use case. It is the most actively maintained (8k+ stars, MIT license, written in C for performance), has the simplest setup, includes built-in auth and SSL, and has been specifically validated for Claude Code by multiple developers. Combined with tmux for session persistence, it covers all requirements.
**Source:** https://github.com/tsl0922/ttyd, https://joshualent.com/snippets/claude-phone/
**Confidence:** High

### Q3: How should remote access be secured?
**Answer:** Three tiers of security are recommended (pick based on threat model):
1. **Minimal:** ttyd basic auth + nginx HTTPS reverse proxy + Let's Encrypt (good enough for most)
2. **Better:** Add Cloudflare Tunnel (Zero Trust policies, no exposed ports)
3. **Best:** Tailscale VPN (no public exposure at all, WireGuard encryption, works on mobile)
**Confidence:** High

---

## Detailed Findings

### 1. ttyd -- RECOMMENDED

**Source:** https://github.com/tsl0922/ttyd
**Stars:** ~11,000 | **Language:** C | **License:** MIT

**What it is:** A lightweight command-line tool that shares any terminal command over the web via WebSocket. Uses xterm.js for the browser-side terminal emulator and libwebsockets + libuv on the backend.

**Claude Code compatibility:**
- VERIFIED working. The command `ttyd -W claude` launches Claude Code in writable mode, accessible at `http://localhost:7681`.
- Full TUI support: colors, cursor positioning, input handling all work via xterm.js.
- The `-W` flag is required to enable write mode (input); without it, the terminal is read-only.
- One known limitation: image uploads do not work through the web terminal.
- Multiple developers have documented this exact setup working.

**Mobile browser support:**
- Works on iOS Safari and Android Chrome via xterm.js.
- xterm.js handles touch input natively.
- On-screen keyboard works for input (though typing on a phone keyboard for extended coding sessions is not ideal -- this is more for monitoring and approving prompts).

**Authentication:**
- Built-in HTTP Basic Authentication: `ttyd -W -c username:password claude`
- HTTP header authentication for reverse proxy setups: `-H header_name` flag
- Can be placed behind nginx for more sophisticated auth (OAuth2 proxy, mTLS, etc.)

**HTTPS/WSS:**
- Built-in OpenSSL support: `ttyd --ssl --ssl-cert cert.pem --ssl-key key.pem -W claude`
- Or terminate SSL at nginx reverse proxy (recommended for Let's Encrypt).

**Session persistence:**
- ttyd itself does NOT persist sessions across browser disconnects. When you close the tab, the underlying process terminates.
- SOLUTION: Combine with tmux. Run `ttyd -W tmux new-session -A -s claude` which attaches to an existing tmux session or creates one. When you close the browser, tmux keeps the session alive. Reopen the browser, and you reconnect to the same session with all state preserved.
- ttyd has auto-reconnect (default 10 seconds) for temporary network drops.

**Resource usage:**
- Extremely lightweight. The C binary is small, libwebsockets is efficient.
- Minimal CPU/memory overhead beyond the actual Claude Code process.

**Ubuntu setup:**
```bash
# Install
sudo apt install ttyd
# Or latest from GitHub releases for newer features

# Basic usage (writable, with auth)
ttyd -W -c user:pass claude

# With tmux persistence
ttyd -W -c user:pass tmux new-session -A -s claude-session

# As systemd service
# /etc/systemd/system/ttyd-claude.service
[Unit]
Description=ttyd Claude Code
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/bin/ttyd -W -c user:pass -p 7681 tmux new-session -A -s claude
Restart=always

[Install]
WantedBy=multi-user.target
```

**Nginx reverse proxy config (for HTTPS subdomain):**
```nginx
server {
    listen 443 ssl;
    server_name terminal.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/terminal.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/terminal.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:7681;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 2. GoTTY -- NOT RECOMMENDED

**Source:** https://github.com/yudai/gotty (original), https://github.com/sorenisanerd/gotty (maintained fork)
**Language:** Go | **License:** MIT

**What it is:** The original web terminal sharing tool that inspired ttyd and others. Allows turning any CLI tool into a web application.

**Current state:**
- The original repository (yudai/gotty) is essentially abandoned -- last meaningful update was years ago.
- A maintained fork exists at sorenisanerd/gotty, but it has far less community support than ttyd.
- ttyd was specifically created as a better alternative to GoTTY.

**Claude Code compatibility:**
- Would technically work (uses xterm.js), but no one has validated it specifically.
- Missing features that ttyd has (better WebSocket implementation, more client options).

**Recommendation:** Skip GoTTY entirely. Use ttyd instead -- it was built as GoTTY's successor and is superior in every way.

---

### 3. WeTTY (Web + tty)

**Source:** https://github.com/butlerx/wetty
**Language:** Node.js/TypeScript | **License:** MIT | **npm:** wetty v2.7.0

**What it is:** A Node.js-based web terminal that creates an SSH connection from the web server to the target machine (or localhost). Uses xterm.js on the frontend and WebSocket for communication.

**Claude Code compatibility:**
- Uses xterm.js, so TUI rendering should work.
- Has been tested with htop, tmux, vim, and similar TUI applications.
- However, WeTTY works by opening an SSH connection, so it adds an SSH layer between the web and the terminal. You would need SSH configured even for localhost access.

**Mobile browser support:**
- Includes an on-screen keyboard for mobile/touch devices (advantage over ttyd).
- Works on iOS Safari and Android Chrome.

**Authentication:**
- Relies on SSH authentication (password or key-based).
- Can be placed behind nginx for additional auth.
- No built-in HTTP basic auth like ttyd.

**HTTPS/WSS:**
- Supports HTTPS natively with certificate configuration.
- Can be terminated at reverse proxy.

**Session persistence:**
- Similar to ttyd -- needs tmux/screen for persistence.
- SSH sessions themselves don't survive browser disconnects.

**Resource usage:**
- Heavier than ttyd due to Node.js runtime.
- Requires Node.js 14+ installed.
- SSH overhead (even for localhost) adds latency.

**Maintenance status:**
- Last npm publish was ~2 years ago (v2.7.0).
- Less actively maintained than ttyd.

**Ubuntu setup:**
```bash
# Install
npm install -g wetty
# or
yarn global add wetty

# Run
wetty --port 3000 --host 0.0.0.0

# With specific command (requires SSH)
wetty --ssh-host localhost --ssh-user youruser
```

**Verdict:** WeTTY is a solid tool but the SSH requirement adds unnecessary complexity when you just want to serve a local CLI. The mobile keyboard support is nice but not worth the tradeoffs vs ttyd.

---

### 4. xterm.js + node-pty (Custom Build)

**Source:** https://github.com/xtermjs/xterm.js, https://www.npmjs.com/package/node-pty

**What it is:** Build your own web terminal from scratch using the same components that ttyd/wetty use internally.

**Architecture:**
```
Browser (xterm.js) <--WebSocket--> Node.js server (node-pty) <--PTY--> Claude Code
```

**What's involved:**
1. Frontend: xterm.js terminal component + WebSocket client + fit addon (for resize)
2. Backend: Express/Fastify server + ws (WebSocket) + node-pty (pseudo-terminal fork)
3. Wire them together: node-pty spawns `claude`, pipes stdout to WebSocket, pipes WebSocket input to stdin
4. Add authentication middleware
5. Add SSL/TLS
6. Handle resize events (SIGWINCH)
7. Handle disconnection/reconnection logic

**Claude Code compatibility:**
- Full control over the terminal emulation means you can optimize for Claude Code's specific needs.
- xterm.js is what VS Code uses for its integrated terminal, and Claude Code's desktop GUI (claude-code-gui) uses xterm.js for its terminal.

**Effort estimate:**
- Minimum viable: ~200-400 lines of code + dependencies
- Production-ready with auth, persistence, reconnection: ~1000+ lines
- You'd essentially be rebuilding ttyd in JavaScript.

**When this makes sense:**
- You want deep customization (custom UI around the terminal, multiple sessions, dashboard)
- You want to integrate with an existing web application
- You need features no existing tool provides

**When this does NOT make sense:**
- You just want to access Claude Code from your phone. Use ttyd.

**Verdict:** Overkill for this use case. ttyd already does this with a single binary.

---

### 5. code-server (VS Code in Browser)

**Source:** https://github.com/coder/code-server

**What it is:** VS Code running in the browser, including its integrated terminal.

**Claude Code compatibility:**
- VS Code's integrated terminal uses xterm.js, so Claude Code's TUI works.
- You can also install the Claude Code VS Code extension for a native integrated experience.
- However, you're running an entire IDE just to access a terminal -- massive overhead.

**Mobile browser support:**
- Works on mobile browsers but the VS Code UI is designed for desktop screens.
- The terminal panel on a phone screen is very small and hard to use.
- Not a good mobile experience for terminal-focused work.

**Authentication:**
- Built-in password authentication.
- Can use `--auth none` for no auth (dangerous).
- Supports proxy authentication.

**HTTPS/WSS:**
- Supports `--cert` and `--cert-key` for HTTPS.
- Or terminate at reverse proxy.

**Session persistence:**
- VS Code sessions persist naturally (terminal state survives refresh).
- The integrated terminal in VS Code does maintain state across page reloads.

**Resource usage:**
- HEAVY. VS Code is an Electron app; code-server requires significant RAM (500MB-1GB+).
- Way more than needed for just terminal access.

**Ubuntu setup:**
```bash
curl -fsSL https://code-server.dev/install.sh | sh
sudo systemctl enable --now code-server@$USER
# Edit ~/.config/code-server/config.yaml for password/port
```

**Verdict:** Works but is extreme overkill. You're running an entire IDE for a terminal. On mobile, the UI is cramped. If you already use code-server for development, using its terminal as a "side door" to Claude Code is reasonable. But don't set up code-server just for terminal access.

---

### 6. Cloudflare Tunnel / ngrok (Secure Exposure)

**These are not terminal tools** -- they are secure tunneling solutions that expose your local ttyd/wetty to the internet.

#### Cloudflare Tunnel (Zero Trust)

**Source:** https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/

**How it works:**
- Install `cloudflared` daemon on your server.
- It creates outbound-only encrypted tunnels to Cloudflare's edge.
- No inbound ports needed on your firewall.
- Map a public hostname (e.g., `terminal.yourdomain.com`) to `localhost:7681` (ttyd).

**Authentication:**
- Cloudflare Zero Trust Access policies: SSO (Google, GitHub, OneTimePin email), device posture checks, geo-restrictions.
- Far more sophisticated than basic auth.

**Browser-based SSH:**
- Cloudflare has its own browser-rendered SSH terminal (using xterm.js internally).
- However, it requires SSH protocol. For Claude Code, using ttyd behind a Cloudflare Tunnel is better.

**Pricing:** Free tier available (generous for personal use).

**Setup:**
```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/

# Quick tunnel (temporary, for testing)
cloudflared tunnel --url http://localhost:7681

# Named tunnel (permanent, with custom domain)
cloudflared tunnel create claude-terminal
cloudflared tunnel route dns claude-terminal terminal.yourdomain.com
# Configure in ~/.cloudflared/config.yml
cloudflared tunnel run claude-terminal
```

**shell-now tool:** A Go CLI that combines ttyd + Cloudflare Quick Tunnel in one command for instant web terminal sharing. Great for testing.

#### ngrok

- Similar concept but commercial-focused.
- Free tier has limitations (random URLs, connection limits).
- Less suitable for persistent access vs Cloudflare Tunnel.
- Use Cloudflare Tunnel instead for this use case.

---

### 7. WireGuard / Tailscale VPN

**These provide network-level access** -- you connect your phone to your server's network via VPN, then access ttyd on its local address.

#### Tailscale (RECOMMENDED for security-conscious users)

**Source:** https://tailscale.com/

**What it is:** A zero-config WireGuard-based mesh VPN. Creates a private network between all your devices.

**How it works:**
1. Install Tailscale on your server and your phone.
2. Both devices get a Tailscale IP (e.g., `100.x.y.z`).
3. Access ttyd at `http://100.x.y.z:7681` from your phone -- no port forwarding, no public exposure.

**Mobile support:**
- Official iOS and Android apps.
- Works perfectly on cellular networks (handles NAT traversal, CGNAT, hotel WiFi).
- Just toggle VPN on, open browser, navigate to the URL.

**Authentication:**
- Uses your identity provider (Google, Microsoft, GitHub) for device authentication.
- ACLs control which devices can access which services.
- MFA through your identity provider.

**Security:**
- WireGuard encryption (state-of-the-art).
- No ports exposed to the public internet.
- No attack surface -- service is invisible to the outside world.

**Session persistence:**
- VPN stays connected even when switching between WiFi and cellular.
- Combined with tmux, provides fully persistent sessions.

**Pricing:** Free for personal use (up to 100 devices).

**Setup:**
```bash
# Server (Ubuntu)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Phone
# Install Tailscale app from App Store / Play Store
# Sign in with same account

# Now access ttyd from phone browser
# http://100.x.y.z:7681
```

#### Raw WireGuard

- More control, no third-party dependency.
- Significantly harder to set up (generate keys, configure peers, handle NAT traversal yourself).
- No mobile app convenience -- must configure WireGuard client manually.
- Use Tailscale unless you have specific reasons not to.

---

## Comparison Matrix

| Approach | Claude Code TUI | Mobile UX | Auth Options | Session Persist | Setup Effort | Resource Usage | Security |
|----------|----------------|-----------|--------------|-----------------|-------------|----------------|----------|
| **ttyd + tmux** | Excellent | Good | Basic auth, reverse proxy | Yes (via tmux) | Very Low | Very Low | Medium |
| **GoTTY** | Likely works | Untested | Basic auth | No (abandoned) | Low | Low | Low |
| **WeTTY** | Good | Good (on-screen kbd) | SSH auth | Yes (via tmux) | Medium | Medium (Node.js) | Medium |
| **xterm.js custom** | Excellent | Configurable | Custom | Custom | Very High | Medium | Custom |
| **code-server** | Excellent | Poor (desktop UI) | Password, proxy | Yes (built-in) | Low | Very High (1GB+) | Medium |
| **CF Tunnel + ttyd** | Excellent | Good | Zero Trust SSO | Yes (via tmux) | Medium | Low | Very High |
| **Tailscale + ttyd** | Excellent | Good | Device-level VPN | Yes (via tmux) | Low | Very Low | Very High |

## Recommendations

### For This Use Case (Phone Access While Traveling)

**Recommended Stack: ttyd + tmux + Tailscale**

This is the optimal combination because:

1. **ttyd** handles the web terminal with minimal overhead and proven Claude Code support.
2. **tmux** provides session persistence -- close the browser, come back later, everything is still there.
3. **Tailscale** provides secure access without any public exposure. No subdomain to protect, no ports to open, no SSL certificates to manage. Just toggle VPN on your phone and go.

**Setup steps on Ubuntu:**
```bash
# 1. Install ttyd
sudo apt install ttyd

# 2. Install tmux (likely already installed)
sudo apt install tmux

# 3. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# 4. Create a systemd service
sudo tee /etc/systemd/system/ttyd-claude.service << 'EOF'
[Unit]
Description=ttyd Claude Code Web Terminal
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/var/www/vibe-marketing
Environment=HOME=/home/youruser
ExecStart=/usr/bin/ttyd -W -p 7681 -t fontSize=14 -t fontFamily="monospace" tmux new-session -A -s claude
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now ttyd-claude

# 5. Install Tailscale on phone, access http://100.x.y.z:7681
```

### Alternative: ttyd + tmux + Cloudflare Tunnel (if you want URL-based access)

If you prefer accessing via a URL like `terminal.yourdomain.com` rather than a VPN:

```bash
# Same ttyd + tmux setup as above, then:
cloudflared tunnel create claude-terminal
cloudflared tunnel route dns claude-terminal terminal.yourdomain.com

# Create config
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <tunnel-id>
credentials-file: /home/youruser/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: terminal.yourdomain.com
    service: http://localhost:7681
  - service: http_status:404
EOF

# Run as service
sudo cloudflared service install
```

Then configure Cloudflare Zero Trust Access policies to gate access (email OTP, Google SSO, etc.).

### Implementation Notes

1. **Font size matters on mobile.** Use `ttyd -t fontSize=16` or larger for phone screens.
2. **tmux prefix key.** The default Ctrl+B prefix can be awkward on mobile keyboards. Consider rebinding to something easier.
3. **Claude Code's `--dangerously-skip-permissions` flag** is often used with ttyd to avoid permission prompts that are hard to interact with on mobile.
4. **Image features do not work.** Image uploads/pastes through the web terminal are not supported. Text-only interaction.
5. **Bandwidth.** xterm.js + WebSocket is very efficient. Claude Code sessions use minimal bandwidth -- works fine on cellular.
6. **Multiple sessions.** You can run ttyd on different ports for different projects, or use tmux windows within a single session.
7. **Monitoring only.** For just monitoring Claude Code (not typing), ttyd without `-W` gives a read-only view. You could have a writable session on one port and a read-only monitoring view on another.

### Dedicated Mobile Claude Code Apps

Worth noting: several purpose-built tools have emerged specifically for this use case:

- **Claude Remote (clauderc.com):** Native Mac + iOS app that wraps tmux sessions with push notifications for Claude Code completions. Mac-only server side.
- **CodeRemote (coderemote.dev):** Mobile chat interface for Claude CLI.
- **Happy (happy.engineering):** Claude Code mobile client.
- **shell-now:** One-command `ttyd + Cloudflare Quick Tunnel` for instant sharing.

These may be worth evaluating if you want a more polished mobile experience than a raw web terminal.

## Sources

1. [ttyd - Share your terminal over the web (GitHub)](https://github.com/tsl0922/ttyd) - Primary web terminal tool, 11k stars
2. [How to use Agentic CLI like Claude Code in Your Browser via ttyd](https://aiengineerguide.com/blog/agentic-cli-browser-ttyd/) - Validated Claude Code + ttyd setup guide
3. [Setup Claude Code on a VPS (Joshua Lent)](https://joshualent.com/snippets/claude-phone/) - VPS setup with ttyd + tmux for phone access
4. [shell-now (GitHub)](https://github.com/STRRL/shell-now) - One-command ttyd + Cloudflare tunnel for iPad Claude Code
5. [GoTTY maintained fork (GitHub)](https://github.com/sorenisanerd/gotty) - Maintained GoTTY fork
6. [WeTTY (GitHub)](https://github.com/butlerx/wetty) - Node.js web terminal with SSH
7. [xterm.js](https://xtermjs.org/) - Terminal emulator library used by all web terminal tools
8. [Claude Code Internals: Terminal UI](https://kotrotsos.medium.com/claude-code-internals-part-11-terminal-ui-542fe17db016) - How Claude Code uses Ink/React for TUI
9. [Cloudflare Tunnel SSH browser rendering](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-browser-rendering/) - Cloudflare's browser SSH terminal
10. [Cloudflare Zero Trust browser terminal](https://blog.cloudflare.com/browser-ssh-terminal-with-auditing/) - Zero Trust terminal architecture
11. [Tailscale](https://tailscale.com/) - WireGuard-based mesh VPN
12. [Tailscale vs WireGuard comparison](https://www.kitecyber.com/tailscale-vs-wireguard/) - Feature comparison
13. [ttyd nginx reverse proxy wiki](https://github.com/tsl0922/ttyd/wiki/Nginx-reverse-proxy) - Official nginx config guide
14. [Claude Remote](https://www.clauderc.com/docs/) - Dedicated Mac/iOS Claude Code remote app
15. [Harper Reed: Claude Code on your phone](https://harper.blog/2026/01/05/claude-code-is-better-on-your-phone/) - Developer experience report
16. [code-server](https://github.com/coder/code-server) - VS Code in browser
17. [ttyd session persistence issue](https://github.com/tsl0922/ttyd/issues/840) - Discussion on tmux integration for persistence

## Open Questions

- How well does Claude Code's Ink/React TUI handle xterm.js resize events when rotating a phone between portrait and landscape? (Likely works but untested in this research.)
- Does Claude Code's checkpoint/rewind feature work correctly through a web terminal? (Should work since it is server-side, but worth validating.)
- Performance of Claude Code's streaming output on high-latency cellular connections (3G/4G edge cases).
