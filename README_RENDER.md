# Render Deployment Instructions

## Prerequisites
- Render account (free tier available)
- Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Prepare Your Repository
Make sure all files are committed to git:
```bash
git add .
git commit -m "Configure for Render deployment"
git push
```

## Step 2: Deploy via Render Dashboard

### Option A: Automatic Deployment (Recommended)
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Render will automatically detect your Python application
5. Configure the service:
   - **Name**: library-management-system
   - **Region**: Choose nearest region
   - **Branch**: main (or your default branch)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Option B: Using render.yaml (Infrastructure as Code)
1. Push your code with `render.yaml` to your repository
2. Go to Render Dashboard → "New +" → "Web Service"
3. Connect your repository
4. Render will automatically use your `render.yaml` configuration

## Step 3: Database Setup

### Automatic Database (Recommended)
If using `render.yaml`, a PostgreSQL database is automatically created and connected.

### Manual Database Setup
1. In Render Dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: library-db
   - **Database Name**: librarys_management_system
   - **User**: library_user
3. Copy the connection details to your web service environment variables

## Step 4: Environment Variables
Go to your web service → Settings → Environment Variables and add:

```
FLASK_ENV=production
SECRET_KEY=your_production_secret_key_here
SECURITY_PASSWORD_SALT=your_production_salt_here
```

Database variables are automatically set if using `render.yaml`.

## Step 5: Deploy
- **Automatic**: Your app will deploy automatically on every push to your repository
- **Manual**: Click "Manual Deploy" in your service dashboard

## Project Structure for Render
```
your-project/
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── app.py               # Main Flask app
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── render.yaml          # Render configuration (optional)
├── .env.production      # Production environment template
└── README_RENDER.md     # This file
```

## Important Notes

### Database Considerations
- Render provides free PostgreSQL databases
- Your current app uses MySQL, so you may need to:
  1. Update database connection code to use PostgreSQL (recommended)
  2. Or bring your own MySQL database

### Session Management
- Render uses standard HTTP sessions
- No special configuration needed for basic sessions

### Static Files
- Static files in `/static/` are served automatically
- Make sure all CSS, JS, and images are in the static folder

### Domain
- Your app will be available at: `https://your-service-name.onrender.com`
- You can add custom domains in the service settings

## Troubleshooting

### Common Issues
1. **Build fails**: Check `requirements.txt` for correct versions
2. **Database connection**: Verify environment variables
3. **Static files not loading**: Ensure files are in `/static/` folder
4. **500 errors**: Check Render logs in dashboard

### Logs
- View real-time logs in your service dashboard
- Check build logs for dependency issues
- Application logs show runtime errors

### Database Migration
If switching from MySQL to PostgreSQL:
1. Export your MySQL data
2. Create the same schema in PostgreSQL
3. Import your data
4. Update `mysql-connector-python` to `psycopg2-binary` in requirements.txt

## Production vs Development
- Production uses PostgreSQL (Render's free database)
- Development can continue using MySQL locally
- Environment variables handle the difference automatically
