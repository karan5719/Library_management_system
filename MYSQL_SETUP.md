# External MySQL Database Setup for Render

## Recommended MySQL Providers

### Option 1: PlanetScale (Recommended)
- **Free tier**: 5GB storage, 1 billion row reads/month
- **MySQL-compatible**
- **Serverless** - no connection pooling needed
- **SSL connections** supported

### Option 2: Railway
- **Free tier**: $5 credit/month
- **Managed MySQL**
- **Easy setup**

### Option 3: AWS RDS
- **Free tier**: 750 hours/month for 12 months
- **Production-ready**
- **More complex setup**

### Option 4: DigitalOcean
- **Free tier**: $200 credit for 60 days
- **Managed MySQL**
- **Simple pricing**

## PlanetScale Setup (Recommended)

### Step 1: Create PlanetScale Account
1. Go to [planetscale.com](https://planetscale.com)
2. Sign up for free account
3. Verify your email

### Step 2: Create Database
1. Click "New database" → "Create new database"
2. **Database name**: `library-management-system`
3. **Region**: Choose nearest to your Render app region
4. Click "Create database"

### Step 3: Get Connection Details
1. Go to your database dashboard
2. Click "Connect" → "General" → "@vercel/python" (or "@render/python")
3. Copy the connection details:
   - Host
   - Username
   - Password
   - Database name

### Step 4: Import Your Schema
1. In PlanetScale console, click "Console"
2. Copy and paste the contents of `mysql.sql`
3. Execute to create tables and insert data

### Step 5: Update Render Environment Variables
Go to your Render web service → Settings → Environment Variables:

```
DB_HOST=your-planetscale-host.planetscale.com
DB_USER=your_planetscale_username
DB_PASSWORD=your_planetscale_password
DB_NAME=library-management-system
DB_PORT=3306
```

## Railway Setup Alternative

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Get $5 free credit

### Step 2: Create MySQL Database
1. Click "New Project" → "Provision MySQL"
2. Wait for database to be ready
3. Click on your database → "Connect" tab
4. Copy connection URL

### Step 3: Update Render Environment
Parse the Railway connection URL and add to Render:

```
DB_HOST=your-railway-host.railway.app
DB_USER=your_railway_user
DB_PASSWORD=your_railway_password
DB_NAME=railway
DB_PORT=3306
```

## Connection String Format

If your provider gives you a connection string like:
```
mysql://user:password@host:3306/database
```

Parse it as:
- **DB_HOST**: host
- **DB_USER**: user  
- **DB_PASSWORD**: password
- **DB_NAME**: database
- **DB_PORT**: 3306

## Security Notes

1. **Never commit credentials to git**
2. **Use SSL connections** when available
3. **Restrict database access** to Render's IP ranges
4. **Use strong passwords**
5. **Enable connection pooling** if supported

## Testing Connection

After setting up environment variables, test by visiting your Render app:
- If it loads without database errors → Success!
- If you get database connection errors → Check environment variables

## Cost Comparison

| Provider | Free Tier | Storage | Limitations |
|----------|-----------|---------|-------------|
| PlanetScale | 5GB | 5GB | 1B reads/month |
| Railway | $5/month | 1GB | Limited time |
| AWS RDS | 750h/month | 20GB | 12 months only |
| DigitalOcean | $200 credit | 25GB | 60 days only |

PlanetScale offers the best long-term free option for MySQL hosting.
