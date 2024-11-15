# GhostSec Platform Deployment Guide

This guide will help you deploy the GhostSec platform on any server with Docker installed.

## Prerequisites

1. A server with Docker and Docker Compose installed
2. A domain name pointing to your server's IP address
3. Basic knowledge of terminal/command line
4. At least 2GB of RAM on your server

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/GhostSec.git
cd GhostSec
```

2. Create and configure environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file with your settings:
- Generate a new Django secret key
- Set your domain name
- Configure database credentials
- Set up email settings
- Add your email for Let's Encrypt certificates

3. Build and start the containers:
```bash
docker-compose up -d --build
```

4. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Visit your domain (https://yourdomain.com) and log in!

## Detailed Setup

### Domain Configuration

1. Point your domain to your server's IP address using an A record
2. Make sure ports 80 and 443 are open on your server
3. Update the DOMAIN and ACME_EMAIL variables in your .env file

### Database Setup

The database will be automatically initialized when you first run the containers. Your data will persist in a Docker volume.

To backup your database:
```bash
docker-compose exec db pg_dump -U ghostsec ghostsec > backup.sql
```

To restore from backup:
```bash
docker-compose exec -T db psql -U ghostsec ghostsec < backup.sql
```

### Email Configuration

1. For Gmail:
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password in your .env file

2. For other providers:
   - Update EMAIL_HOST and EMAIL_PORT accordingly
   - Use appropriate credentials

### SSL Certificates

Traefik will automatically obtain and renew SSL certificates from Let's Encrypt.

### Security Considerations

1. Change default passwords in .env file
2. Keep your system and Docker up to date
3. Regularly backup your data
4. Monitor your logs for suspicious activity

## Maintenance

### Updating the Platform

1. Pull the latest changes:
```bash
git pull origin main
```

2. Rebuild and restart containers:
```bash
docker-compose down
docker-compose up -d --build
```

### Monitoring

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Troubleshooting

1. If the site is not accessible:
   - Check if containers are running: `docker-compose ps`
   - Check logs: `docker-compose logs`
   - Verify domain DNS settings

2. If SSL certificates are not working:
   - Verify your domain points to the server
   - Check Traefik logs: `docker-compose logs traefik`

3. Database connection issues:
   - Verify database credentials in .env
   - Check if database container is running
   - Check database logs: `docker-compose logs db`

## Sharing with Friends

To share your GhostSec instance with friends:

1. Ensure your server has enough resources for multiple users
2. Share your domain name with them
3. Create accounts for them through the admin interface
4. Consider setting up monitoring for resource usage

## Resource Requirements

Minimum recommended specifications:
- 2 CPU cores
- 4GB RAM
- 20GB storage
- 10Mbps network connection

## Support

For issues and support:
1. Check the logs using `docker-compose logs`
2. Review the troubleshooting section
3. Create an issue on the GitHub repository

## Backup Strategy

1. Database:
```bash
# Backup
docker-compose exec db pg_dump -U ghostsec ghostsec > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U ghostsec ghostsec < backup_20230101.sql
```

2. Media files:
```bash
# Backup
docker cp $(docker-compose ps -q web):/app/media ./media_backup

# Restore
docker cp ./media_backup/. $(docker-compose ps -q web):/app/media/
```

3. Automated backup script (create as backup.sh):
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)

# Backup database
docker-compose exec -T db pg_dump -U ghostsec ghostsec > $BACKUP_DIR/db_$DATE.sql

# Backup media files
docker cp $(docker-compose ps -q web):/app/media $BACKUP_DIR/media_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_*" -mtime +7 -delete
find $BACKUP_DIR -name "media_*" -mtime +7 -delete
```

Make it executable:
```bash
chmod +x backup.sh
```

Add to crontab to run daily:
```bash
0 0 * * * /path/to/backup.sh
```
