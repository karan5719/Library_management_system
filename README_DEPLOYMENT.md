# Vercel Deployment Instructions

## Prerequisites
- Vercel account
- Git repository (GitHub, GitLab, or Bitbucket)
- Database (Vercel Postgres recommended or external MySQL)

## Step 1: Install Vercel CLI
```bash
npm i -g vercel
```

## Step 2: Login to Vercel
```bash
vercel login
```

## Step 3: Deploy Your Project
```bash
# From your project directory
vercel

# Follow the prompts:
# - Link to existing project? No
# - Project name? (accept default or customize)
# - Directory? (accept default ./)
# - Want to override settings? No
```

## Step 4: Configure Environment Variables
Go to your Vercel dashboard → Project Settings → Environment Variables and add:

```
SECRET_KEY=your_production_secret_key_here
DB_HOST=your_database_host
DB_USER=your_database_user  
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
SECURITY_PASSWORD_SALT=your_production_salt_here
```

## Database Options

### Option 1: Vercel Postgres (Recommended)
1. In Vercel dashboard, go to Storage → Create Database
2. Choose Postgres
3. Add the connection string to your environment variables

### Option 2: External MySQL
1. Use your existing MySQL database
2. Update environment variables with your MySQL credentials
3. Ensure your database allows external connections

## Step 5: Redeploy with Environment Variables
```bash
vercel --prod
```

## Project Structure for Vercel
```
your-project/
├── api/
│   └── index.py          # Vercel serverless entry point
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── app.py               # Main Flask app
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel configuration
└── .env.example         # Environment variables template
```

## Important Notes
- Session management works differently in serverless environments
- Consider using Vercel KV for session storage if needed
- Static files are automatically served from `/static/`
- The app will be available at `https://your-project.vercel.app`

## Troubleshooting
- If you get import errors, check that all files are committed to git
- Database connection issues? Verify environment variables
- Need to debug? Check Vercel function logs in dashboard
