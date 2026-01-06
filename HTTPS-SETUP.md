# HTTPS Setup Guide - Server Monitor Dashboard v4.0

This guide explains how to configure HTTPS for the Server Monitor Dashboard using a reverse proxy.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option A: Nginx + Let's Encrypt](#option-a-nginx--letsencrypt)
3. [Option B: Caddy (Automatic HTTPS)](#option-b-caddy-automatic-https)
4. [Option C: Custom SSL Certificates](#option-c-custom-ssl-certificates)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before setting up HTTPS, ensure you have:
- A domain name pointing to your server (DNS A record)
- Server Monitor Dashboard running on `http://localhost:9081` (or your configured port)
- Root or sudo access to your server
- Port 80 and 443 accessible from the internet (for Let's Encrypt validation)

---

## Option A: Nginx + Let's Encrypt

### Step 1: Install Nginx and Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install -y nginx certbot python3-certbot-nginx
```

### Step 2: Create Nginx Configuration

Create a new configuration file for Server Monitor:

```bash
sudo nano /etc/nginx/sites-available/server-monitor
```

Add the following configuration (replace `monitor.example.com` with your domain):

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name monitor.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name monitor.example.com;

    # SSL certificates (will be created by Certbot)
    ssl_certificate /etc/letsencrypt/live/monitor.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor.example.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy settings
    location / {
        proxy_pass http://localhost:9081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Frontend static assets
    location ~ ^/(assets|frontend)/ {
        proxy_pass http://localhost:9081;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Step 3: Enable Nginx Configuration

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/server-monitor /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl restart nginx
```

### Step 4: Get SSL Certificate from Let's Encrypt

```bash
# Option A: Certbot with Nginx plugin (automatic)
sudo certbot --nginx -d monitor.example.com

# Option B: Manual standalone (stop Nginx first)
sudo systemctl stop nginx
sudo certbot certonly --standalone -d monitor.example.com
sudo systemctl start nginx
```

Follow the prompts to agree to the Let's Encrypt terms and enter your email.

### Step 5: Set Up Automatic Renewal

Let's Encrypt certificates expire every 90 days. Certbot automatically sets up renewal:

```bash
# Test renewal process
sudo certbot renew --dry-run

# Enable renewal timer (automatic)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal status
sudo systemctl status certbot.timer
```

---

## Option B: Caddy (Automatic HTTPS)

Caddy is easier than Nginx - it automatically manages HTTPS!

### Step 1: Install Caddy

```bash
# Using snap (easiest)
sudo apt install -y snapd
sudo snap install --classic caddy

# Or download binary from https://caddyserver.com/download
```

### Step 2: Create Caddy Configuration

Create configuration file:

```bash
sudo mkdir -p /etc/caddy
sudo nano /etc/caddy/Caddyfile
```

Add the following (replace `monitor.example.com` with your domain):

```caddyfile
monitor.example.com {
    # Automatic HTTPS - Let's Encrypt
    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }

    # Reverse proxy to Server Monitor
    reverse_proxy localhost:9081 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up X-Real-IP {remote_host}
        websocket
    }

    # Security headers
    header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    header X-Frame-Options "SAMEORIGIN"
    header X-Content-Type-Options "nosniff"
    header X-XSS-Protection "1; mode=block"
    header Referrer-Policy "no-referrer-when-downgrade"

    # Logging
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

### Step 3: Start Caddy

```bash
# Create log directory
sudo mkdir -p /var/log/caddy
sudo chown -R caddy:caddy /var/log/caddy

# Start Caddy service
sudo systemctl start snap.caddy.caddy
sudo systemctl enable snap.caddy.caddy

# Check status
sudo systemctl status snap.caddy.caddy
```

That's it! Caddy automatically:
- Requests Let's Encrypt certificate
- Renews every 60 days
- Configures HTTPS
- Handles redirects

---

## Option C: Custom SSL Certificates

If you have your own SSL certificates:

### Step 1: Prepare Certificates

Place your certificate and key files:

```bash
# Certificate file
/etc/ssl/certs/monitor.example.com.crt

# Private key file
/etc/ssl/private/monitor.example.com.key

# Set proper permissions
sudo chmod 600 /etc/ssl/private/monitor.example.com.key
sudo chmod 644 /etc/ssl/certs/monitor.example.com.crt
```

### Step 2: Configure Server Monitor

Go to **Admin → Domain & SSL Settings** and:
1. Select "Custom Certificate"
2. Enter certificate path: `/etc/ssl/certs/monitor.example.com.crt`
3. Enter private key path: `/etc/ssl/private/monitor.example.com.key`
4. Click "Save Settings"

### Step 3: Update Nginx/Caddy Configuration

Use the paths you saved in step 2 in your Nginx/Caddy configuration:

```nginx
# Nginx example
ssl_certificate /etc/ssl/certs/monitor.example.com.crt;
ssl_certificate_key /etc/ssl/private/monitor.example.com.key;
```

---

## Verification

### Test Your HTTPS Setup

```bash
# Test SSL certificate
curl -v https://monitor.example.com

# Check certificate details
openssl s_client -connect monitor.example.com:443

# Test with SSL Labs (https://www.ssllabs.com/)
# Provides detailed SSL analysis
```

### In Browser

1. Visit `https://monitor.example.com`
2. Check browser shows green lock icon
3. Click lock icon to view certificate details
4. Verify certificate matches your domain name

### Monitor Dashboard Access

1. Go to Settings → Domain & SSL
2. Verify domain name is saved
3. Check SSL type is set correctly
4. Confirm auto-renewal is enabled (if using Let's Encrypt)

---

## Troubleshooting

### Certificate Not Found

```bash
# Check if certificate exists
sudo ls -la /etc/letsencrypt/live/monitor.example.com/

# If not found, run certbot again
sudo certbot certonly --standalone -d monitor.example.com
```

### DNS Not Resolving

```bash
# Check DNS resolution
nslookup monitor.example.com
dig monitor.example.com

# If not working, update your domain's A record to point to your server's IP
```

### Certificate Renewal Failed

```bash
# Check renewal logs
sudo certbot renew --verbose

# Manually renew
sudo certbot renew --force-renewal

# Check certbot service
sudo systemctl status certbot.timer
```

### Port 80/443 Already in Use

```bash
# Check what's using the ports
sudo lsof -i :80
sudo lsof -i :443

# Change Server Monitor port if needed
# Edit .env or configuration file
# Then update Nginx/Caddy to proxy to new port
```

### Nginx/Caddy Not Starting

```bash
# Test configuration
sudo nginx -t      # for Nginx
# Caddy logs available via: sudo journalctl -u snap.caddy.caddy -f

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### Self-Signed Certificate

For testing without a real domain:

```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/server-monitor.key \
    -out /etc/ssl/certs/server-monitor.crt
```

---

## Security Recommendations

1. **Always use HTTPS** in production
2. **Keep certificates renewed** - automate with Certbot or Caddy
3. **Use strong SSL ciphers** - TLS 1.2 or higher
4. **Enable HSTS headers** - force HTTPS redirects
5. **Regular updates** - keep Nginx/Caddy and OpenSSL updated
6. **Firewall rules** - restrict access to admin pages
7. **Monitor logs** - check for certificate expiry warnings

---

## Let's Encrypt Rate Limits

Be aware of Let's Encrypt rate limits:
- **50 certificates per domain per week**
- **5 duplicate certificates per week**

During testing, use the staging environment:

```bash
sudo certbot --staging -d monitor.example.com
```

---

## References

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [OWASP SSL Configuration Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review certificate logs: `sudo certbot logs`
3. Check reverse proxy logs
4. Visit [Server Monitor GitHub Issues](https://github.com/minhtuancn/server-monitor/issues)
