#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER

# Create app directory
mkdir -p /opt/ghostsec
cd /opt/ghostsec

# Clone repository (replace with your repo URL)
git clone https://github.com/YourUsername/GhostSec.git .

# Create environment file
cp .env.example .env

# Create necessary directories
mkdir -p logs
mkdir -p media
mkdir -p static
mkdir -p backups

# Set permissions
sudo chown -R $USER:$USER /opt/ghostsec
chmod -R 755 /opt/ghostsec

# Create backup script
cat > backup.sh << 'EOL'
#!/bin/bash
BACKUP_DIR="/opt/ghostsec/backups"
DATE=$(date +%Y%m%d)

# Backup database
docker-compose exec -T db pg_dump -U ghostsec ghostsec > $BACKUP_DIR/db_$DATE.sql

# Backup media files
docker cp $(docker-compose ps -q web):/app/media $BACKUP_DIR/media_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_*" -mtime +7 -delete
find $BACKUP_DIR -name "media_*" -mtime +7 -delete
EOL

chmod +x backup.sh

# Add backup cron job
(crontab -l 2>/dev/null; echo "0 0 * * * /opt/ghostsec/backup.sh") | crontab -

# Setup firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable

echo "Setup complete! Next steps:"
echo "1. Edit the .env file with your settings"
echo "2. Run: docker-compose up -d --build"
echo "3. Create superuser: docker-compose exec web python manage.py createsuperuser"
