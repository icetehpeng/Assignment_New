# Deployment Guide

## Quick Deployment

### Development
```bash
./start_all_services.bat
```

### Production
See sections below for server setup, systemd services, and monitoring.

## Pre-Deployment Checklist

- [ ] Python 3.8+, MySQL 5.7+, Node.js 14+
- [ ] `.env` file configured
- [ ] Database setup complete
- [ ] Node-RED flows imported
- [ ] Telegram bot token set
- [ ] Fall detection tested
- [ ] All alerts working

## Production Server Setup

### 1. System Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip mysql-server nodejs npm -y
```

### 2. Application Setup
```bash
sudo mkdir -p /opt/elderly-care
cd /opt/elderly-care
git clone <repo> .
pip install -r requirements.txt
npm install -g node-red node-red-node-mysql node-red-contrib-telegrambot
```

### 3. Systemd Services

**Streamlit** (`/etc/systemd/system/elderly-care.service`):
```ini
[Unit]
Description=Elderly Care System
After=network.target

[Service]
Type=simple
User=elderly-care
WorkingDirectory=/opt/elderly-care
ExecStart=/usr/bin/python3 -m streamlit run main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Node-RED** (`/etc/systemd/system/node-red.service`):
```ini
[Unit]
Description=Node-RED
After=network.target

[Service]
Type=simple
User=node-red
ExecStart=/usr/bin/node-red
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable elderly-care node-red
sudo systemctl start elderly-care node-red
```

### 4. Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
    }
}
```

### 5. SSL Certificate
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

## Monitoring

### Service Status
```bash
sudo systemctl status elderly-care
sudo systemctl status node-red
sudo journalctl -u elderly-care -f
```

### Database Health
```bash
# Check size
SELECT table_schema, ROUND(SUM(data_length+index_length)/1024/1024,2) AS size_mb
FROM information_schema.tables
WHERE table_schema='elderly_care_system';

# Check connections
SHOW PROCESSLIST;
```

### Application Logs
```bash
tail -f logs/app_errors.log
```

## Backup

### Daily Backup
```bash
mysqldump -u root -p elderly_care_system > backup_$(date +%Y%m%d).sql
tar -czf elderly-care-backup-$(date +%Y%m%d).tar.gz /opt/elderly-care
```

### Restore
```bash
mysql -u root -p elderly_care_system < backup_20260212.sql
tar -xzf elderly-care-backup-20260212.tar.gz -C /opt/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Service won't start | Check logs: `sudo journalctl -u elderly-care -n 50` |
| Port already in use | `sudo lsof -i :8501` and kill process |
| Database connection failed | Verify MySQL running, check credentials |
| No video stream | Check camera permissions: `sudo usermod -a -G video $USER` |
| Alerts not sending | Verify Node-RED running, check Telegram token |

## Performance Tuning

### Database
```sql
CREATE INDEX idx_timestamp ON fall_detection_alerts(timestamp);
CREATE INDEX idx_user_id ON vital_signs(user_id);
OPTIMIZE TABLE fall_detection_alerts;
```

### System
```bash
ulimit -n 65536
sysctl -w net.core.somaxconn=65535
```

## Security

### Firewall
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Database User
```sql
CREATE USER 'elderly_care'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON elderly_care_system.* TO 'elderly_care'@'localhost';
```

## Status

✅ **Production Ready**
