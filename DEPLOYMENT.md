# Deployment Guide

## Backend Deployment (Render)

### Prerequisites
1. Create a Render account at https://render.com
2. Connect your GitHub repository

### Steps
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `datasaudi-chatbot-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r back_end/requirements.txt`
   - **Start Command**: `cd back_end && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: Leave empty (uses repository root)

### Environment Variables (Add in Render Dashboard)
```
OPENAI_API_KEY=your_openai_api_key_here
WEAVIATE_URL=your_weaviate_url_here
WEAVIATE_API_KEY=your_weaviate_api_key_here
```

### After Deployment
- Note down your Render app URL (e.g., `https://datasaudi-chatbot-backend.onrender.com`)
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
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
```

### After Deployment
- Your frontend will be available at a Vercel URL
- Update the CORS settings in your backend if needed

---

## Testing

1. Test the backend API endpoint: `https://your-render-app.onrender.com/api/ask`
2. Test the frontend: Your Vercel URL
3. Verify the chat functionality works end-to-end

## Troubleshooting

### Backend Issues
- Check Render logs for startup errors
- Ensure all environment variables are set
- Verify the Procfile is correct

### Frontend Issues
- Check Vercel build logs
- Ensure NEXT_PUBLIC_API_URL is set correctly
- Verify CORS settings in backend

### CORS Issues
- Update the `allow_origins` in `back_end/main.py` with your Vercel URL
- Redeploy the backend after CORS changes
