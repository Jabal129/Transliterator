# Deployment Instructions for Railway.app

## Prerequisites
- GitHub account (Railway deploys from GitHub)
- Railway account (https://railway.app)
- Your project pushed to a GitHub repository

## Step 1: Push Your Project to GitHub
If you haven't already, initialize a git repository and push to GitHub:

```bash
git init
git add .
git commit -m "Initial commit - ready for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/transliterator.git
git branch -M main
git push -u origin main
```

## Step 2: Create a Railway Project
1. Go to https://railway.app and sign in with GitHub
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select the `transliterator` repository
6. Railway will auto-detect the project and ask where to deploy
7. Keep the default Dockerfile option

## Step 3: Configure Environment Variables
1. In Railway dashboard, go to your project settings
2. Add this environment variable:
   ```
   ALLOWED_ORIGINS=https://your-railway-url.up.railway.app
   ```
   (You'll get the exact URL after the first deploy)

## Step 4: Deploy
Railway will automatically build and deploy when you push to GitHub. The build process will:
1. Build the React frontend (`npm run build`)
2. Install Python dependencies
3. Copy the built frontend to the backend static folder
4. Start the FastAPI server on port 8000

## Step 5: After Deployment
Once deployed:
1. Copy the Railway-provided URL (e.g., `https://transliterator-production.up.railway.app`)
2. Update the `ALLOWED_ORIGINS` environment variable with this exact URL
3. Your app will be accessible at that URL from anywhere!

## Local Development
For local development, continue using:
```bash
npm run dev        # Terminal 1: React frontend on :5173
cd backend && python -m uvicorn main:app --reload  # Terminal 2: Backend on :8000
```

## Troubleshooting
- Check Railway logs: Click "Logs" in your project dashboard
- If build fails, check requirements.txt and package.json
- Make sure mapping.xlsx is committed to git
- CORS issues? Check ALLOWED_ORIGINS variable matches your Railway URL
