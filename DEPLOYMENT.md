# Deployment Guide

## Backend Deployment (Railway)

### Prerequisites
1. Create a Railway account at https://railway.app
2. Connect your GitHub repository

### Steps
1. Go to Railway Dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub repository: `7USSAM30/data-Saudi-chatbot-personal`
4. Configure the service:
   - **Root Directory**: `back_end` (IMPORTANT: Set this to back_end)
   - **Build Command**: Leave empty (Railway will auto-detect)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Railway will auto-detect Python and use the manual start command

### Environment Variables (Add in Railway Dashboard)
```
OPENAI_API_KEY=your_openai_api_key_here
WEAVIATE_URL=your_weaviate_url_here
WEAVIATE_API_KEY=your_weaviate_api_key_here
```

### After Deployment
- Note down your Railway app URL (e.g., `https://datasaudi-chatbot-backend-production.up.railway.app`)
- This will be used for the frontend API URL

---

## Frontend Deployment (Vercel)

### Prerequisites
1. Create a Vercel account at https://vercel.com
2. Connect your GitHub repository

### Steps
1. Go to Vercel Dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `front_end`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Environment Variables (Add in Vercel Dashboard)
```
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

### After Deployment
- Your frontend will be available at a Vercel URL
- Update the CORS settings in your backend if needed

---

## Testing

1. Test the backend API endpoint: `https://your-railway-app.up.railway.app/api/ask`
2. Test the frontend: Your Vercel URL
3. Verify the chat functionality works end-to-end

## Troubleshooting

### Backend Issues

#### "No start command was found" Error
If you see this error, follow these steps:
1. **Delete the current Railway service** and recreate it
2. **Set Root Directory to `back_end`** in Railway dashboard
3. **Manually set Start Command** to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Leave Build Command empty** (Railway will auto-detect)

#### General Backend Issues
- Check Railway logs for startup errors
- Ensure all environment variables are set
- Verify the Root Directory is set to `back_end`
- Make sure the Start Command is set manually in the dashboard

### Frontend Issues
- Check Vercel build logs
- Ensure NEXT_PUBLIC_API_URL is set correctly
- Verify CORS settings in backend

### CORS Issues
- Update the `allow_origins` in `back_end/main.py` with your Vercel URL
- Redeploy the backend after CORS changes
