# SafeCorridor Deployment Guide

This guide outlines the simplest and most robust strategy for deploying the SafeCorridor ecosystem to the public internet using free-tier cloud services.

Because the system relies on active WebSockets and an in-memory state machine, the backend **cannot** be deployed to serverless environments (like Netlify Functions or Vercel Serverless). It must be hosted on a persistent web service.

### Deployment Strategy
- **Backend (FastAPI + SQLite)** ➔ **Render.com** (Handles WebSockets and persistent Python processes).
- **Frontend (React + Vite)** ➔ **Vercel.com** (Optimized for lightning-fast React hosting).
- **Android App** ➔ Local APK release build.

---

## 1. The Backend (FastAPI) ➔ Deploy to Render

Render provides an excellent free tier for running Python web services.

1. Commit and push your entire codebase to GitHub.
2. Log into [Render.com](https://render.com) and click **New Web Service**.
3. Connect your GitHub account and select your `SafeCorridor` repository.
4. Set the **Root Directory** to: `backend`
5. Set the **Environment** to: `Python 3`
6. Set the **Build Command** to: 
   ```bash
   pip install -r requirements.txt
   ```
7. Set the **Start Command** to:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
8. Click **Create Web Service**. 
9. Once deployed, copy your new backend URL (e.g., `https://safecorridor-backend.onrender.com`).

> [!NOTE]
> **A note on SQLite and Free Tiers:** On Render's free tier, the server will "go to sleep" after 15 minutes of inactivity. When it wakes up, the local SQLite database file is wiped clean. This is perfectly fine for a portfolio demo (every wake-up is a clean slate). If you want production-grade data persistence, navigate to the Render dashboard and click **"Add Volume"** to attach a persistent disk.

---

## 2. The Dashboard (React) ➔ Deploy to Vercel

Vercel is the undisputed king of easy frontend hosting. It's completely free, and deployments take about 30 seconds.

### Step A: Update Environment URLs
Before deploying, you must tell the React dashboard where your new Render backend lives.

1. Open `dashboard/src/App.jsx`.
2. Locate the following constants at the top of the file:
   ```javascript
   const SOCKET_URL = 'http://localhost:3000';
   const API_URL = 'http://localhost:3000/api';
   ```
3. Change them to your new Render URL:
   ```javascript
   const SOCKET_URL = 'https://safecorridor-backend.onrender.com';
   const API_URL = 'https://safecorridor-backend.onrender.com/api';
   ```
4. Commit and push these changes to GitHub.

### Step B: Deploy on Vercel
1. Log into [Vercel.com](https://vercel.com) and click **Add New Project**.
2. Select your GitHub repository.
3. In the project settings, set the **Root Directory** to `dashboard`.
4. Vercel will automatically detect that it's a Vite project and configure the build commands.
5. Click **Deploy**. Your dashboard is now live globally!

---

## 3. The Android App ➔ Build a Release APK

The Android app must also be updated to point to the live Render backend instead of your local machine.

### Step A: Update URLs
1. Open Android Studio.
2. In `TrackerService.kt` and `MainActivity.kt` (or anywhere a network request is made), search for `http://10.0.2.2:3000` or `http://localhost:3000`.
3. Replace them with your live backend URL (e.g., `https://safecorridor-backend.onrender.com/api/ride/...`).

### Step B: Generate the APK
1. In the top menu of Android Studio, go to **Build > Generate Signed Bundle / APK**.
2. Select **APK** and click Next.
3. If you don't have a Keystore, click **Create new...** (A Keystore is simply a password-protected file used to cryptographically sign your app).
4. Fill out the Keystore details, remember your password, and click Next.
5. Select the **release** build variant and click Finish.
6. Android Studio will compile the app. When finished, a popup will appear in the bottom right corner—click **locate** to open the folder containing your `app-release.apk`.

### Step C: Distribution
You can now upload this `app-release.apk` file to Google Drive, attach it to a GitHub Release, or host it on a personal website for anyone to download and install directly on their Android phone.
