# Deployment Guide

This guide covers deploying the Cartoon of the Day application to Netlify or Vercel.

## Prerequisites

- GitHub account with the repository pushed
- API keys configured in environment variables

## Environment Configuration

Create `.env.production` with your production API keys:

```
VITE_GEMINI_API_KEY=your_production_api_key
VITE_API_BASE_URL=https://api.production.example.com
VITE_ENV=production
```

## Netlify Deployment

### Option 1: Git-Connected Deployment (Recommended)

1. Push your code to GitHub
2. Go to [Netlify](https://app.netlify.com/)
3. Click "New site from Git"
4. Select GitHub and authorize
5. Choose your repository
6. Confirm build settings (should auto-detect):
   - Build command: `npm run build`
   - Publish directory: `dist`
7. Add environment variables:
   - Click "New variable"
   - Add `VITE_GEMINI_API_KEY` and other secrets
8. Click "Deploy site"

### Option 2: Manual Deployment

1. Build locally:
```bash
npm run build
```

2. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

3. Deploy:
```bash
netlify deploy --prod --dir dist
```

## Vercel Deployment

### Option 1: Git-Connected Deployment (Recommended)

1. Push your code to GitHub
2. Go to [Vercel](https://vercel.com/)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will auto-detect the build settings
6. Add environment variables under Project Settings:
   - Add `VITE_GEMINI_API_KEY` and other secrets
7. Click "Deploy"

### Option 2: Vercel CLI Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel --prod
```

## Environment Variables in Deployment

Both Netlify and Vercel provide ways to set environment variables securely:

### Netlify
- Site settings → Build & deploy → Environment
- Add variables without committing to repository

### Vercel
- Project settings → Environment Variables
- Select which environments (Production, Preview, Development)

## Pre-Deployment Checklist

- [ ] All tests passing: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] No console errors in development
- [ ] API keys configured in deployment platform
- [ ] `.env.local` is in `.gitignore`
- [ ] Production API endpoints configured
- [ ] Tailwind CSS production build optimized

## Post-Deployment Testing

1. **Functional Testing**
   - Test location detection
   - Verify news fetching
   - Test cartoon generation
   - Check image download

2. **Performance Testing**
   - Check Lighthouse scores
   - Monitor bundle sizes
   - Test on slow networks

3. **Security Testing**
   - Verify API keys aren't exposed
   - Check HTTPS is enabled
   - Test CORS configuration

## Monitoring and Logs

### Netlify
- Site overview → Deploy log → Build log
- Real-time monitoring in Analytics

### Vercel
- Project dashboard → Deployments
- Function and Edge logs in Monitoring
- Analytics and Web Vitals

## Rollback Procedures

### Netlify
1. Go to Deployments
2. Find previous successful deployment
3. Click "Publish" on that deployment

### Vercel
1. Go to Deployments
2. Click the three dots on previous deployment
3. Select "Promote to Production"

## Troubleshooting

### Build Fails

**Check:**
- TypeScript compilation: `npm run build` locally
- Node.js version compatibility
- All dependencies installed
- Environment variables set correctly

**Solutions:**
- Clear node_modules and reinstall
- Check Node.js version matches (20+)
- Verify all required env vars are set

### Blank Page on Deploy

**Check:**
- Routing configuration (SPA fallback)
- Asset paths in built files
- Console errors in browser DevTools

**Solutions:**
- Verify `netlify.toml` or `vercel.json` redirects
- Check Tailwind CSS is built correctly
- Verify all imports use correct paths

### API Calls Failing

**Check:**
- API keys are set and valid
- CORS configuration
- API endpoints are reachable
- Environment variables are correct

**Solutions:**
- Verify API key in deployment dashboard
- Check API rate limits
- Review CORS headers from API

### Performance Issues

**Check:**
- Bundle size analysis
- Code splitting is working
- Images are optimized
- Caching headers configured

**Solutions:**
- Run `npm run build` and check sizes
- Enable compression in deployment platform
- Optimize images before deployment

## Cost Optimization

- **Netlify**: Free tier includes 300 minutes/month
- **Vercel**: Free tier includes 100GB bandwidth/month
- Both platforms auto-scale with traffic

## Security Best Practices

1. **API Keys**
   - Never commit to repository
   - Use deployment platform's secret management
   - Rotate keys regularly

2. **HTTPS**
   - Automatically enabled on both platforms
   - Enforce HTTPS redirects

3. **Environment Isolation**
   - Separate development and production keys
   - Use different API endpoints

4. **Rate Limiting**
   - Implement rate limiting on API calls
   - Monitor for unusual activity

## Next Steps

- Set up monitoring and alerts
- Configure custom domain
- Enable analytics
- Set up continuous deployment
