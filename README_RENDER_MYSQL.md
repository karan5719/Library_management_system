# Render Deployment with External MySQL

## Quick Start

1. **Set up external MySQL database** (see `MYSQL_SETUP.md`)
2. **Update environment variables** in `render.yaml`
3. **Deploy to Render**

## Step 1: Set Up External MySQL

### Recommended: PlanetScale (Free)
1. Go to [planetscale.com](https://planetscale.com)
2. Create database: `library-management-system`
3. Import your schema using `mysql.sql`
4. Get connection details

### Alternative: Railway, AWS RDS, or DigitalOcean
See `MYSQL_SETUP.md` for detailed options.

## Step 2: Update render.yaml

Replace the placeholder values in `render.yaml`:

```yaml
envVars:
  - key: DB_HOST
    value: your-mysql-host.com        # Replace with actual host
  - key: DB_USER
    value: your_mysql_user             # Replace with actual username
  - key: DB_PASSWORD
    value: your_mysql_password         # Replace with actual password
  - key: DB_NAME
    value: librarys_management_system # Or your database name
  - key: DB_PORT
    value: 3306
```

## Step 3: Deploy to Render

### Option A: Using render.yaml (Recommended)
1. Push your code to Git:
   ```bash
   git add .
   git commit -m "Configure for Render with MySQL"
   git push
   ```

2. Deploy on Render:
   - Go to [render.com](https://render.com)
   - "New +" → "Web Service"
   - Connect your repository
   - Render will use `render.yaml` automatically

### Option B: Manual Setup
1. Go to Render Dashboard → "New +" → "Web Service"
2. Connect repository
3. Configure manually:
   - **Name**: library-management-system
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add MySQL connection details

## Step 4: Import Database Schema

### PlanetScale Console
1. Go to your PlanetScale database
2. Click "Console"
3. Copy contents of `mysql.sql`
4. Paste and execute

### Other Providers
Use your provider's MySQL client:
```bash
mysql -h YOUR_HOST -u YOUR_USER -p YOUR_DATABASE < mysql.sql
```

## Environment Variables

Your app needs these variables (set in `render.yaml` or Render dashboard):

```
FLASK_ENV=production
SECRET_KEY=auto_generated_by_render
DB_HOST=your_mysql_host
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=librarys_management_system
DB_PORT=3306
```

## Testing Your Deployment

1. **Deploy completes**: Check Render dashboard for green status
2. **Visit app**: Go to `https://your-service-name.onrender.com`
3. **Test login**: Use credentials from `mysql.sql`:
   - Admin: username `admin`, password `admin123`
   - Member: username `Himanshukumar`, password `himu123`

## Troubleshooting

### Database Connection Errors
- Check environment variables match your MySQL provider
- Verify database allows external connections
- Ensure SSL is configured if required

### Build Failures
- Check `requirements.txt` has correct versions
- Verify all files are committed to Git

### App Not Loading
- Check Render logs in dashboard
- Verify database schema is imported
- Test database connection manually

## Database Providers Comparison

| Provider | Free Tier | Setup Complexity | Best For |
|----------|-----------|------------------|----------|
| PlanetScale | 5GB | Easy | Production |
| Railway | $5/month | Medium | Development |
| AWS RDS | 750h/12mo | Hard | Enterprise |
| DigitalOcean | $200/60d | Medium | General |

## Security Notes

1. **Never commit credentials** to Git
2. **Use SSL connections** when available
3. **Restrict database access** to Render's IP ranges
4. **Use strong passwords**
5. **Monitor database usage** on free tiers

## Production Considerations

- **Backups**: Set up automatic database backups
- **Monitoring**: Monitor database performance
- **Scaling**: Plan for database scaling as user base grows
- **SSL**: Always use SSL in production

## Support

- **Render docs**: [render.com/docs](https://render.com/docs)
- **PlanetScale docs**: [planetscale.com/docs](https://planetscale.com/docs)
- **MySQL connector**: [github.com/mysql/mysql-connector-python](https://github.com/mysql/mysql-connector-python)

Your Flask app is now ready for production deployment on Render with external MySQL!
