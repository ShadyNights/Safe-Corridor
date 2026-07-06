# Safe Corridor - Comprehensive Local Setup Guide

This document is the single source of truth for setting up, building, and running the Safe Corridor environment locally. It covers the Python Backend, React Dashboard, and Android Kotlin App.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
1. **Python 3.10+** (For the backend)
2. **Node.js 18+ and npm** (For the dashboard)
3. **Android Studio** (For building the Android app, which comes bundled with Java 17)

---

## 🖥️ 1. Backend Setup (FastAPI)

The backend handles telemetry ingestion, geometric risk calculations, and real-time WebSocket broadcasting.

### Step-by-Step
1. Open a new terminal and navigate to the backend directory:
   ```bash
   cd "d:/Safe Corridor/backend"
   ```
2. (Optional but recommended) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   Create a `.env` file in the `backend/` directory with your secrets:
   ```ini
   API_KEY=your_super_secure_api_key_here
   CORS_ORIGINS=http://localhost:5173
   DATABASE_URL=safecorridor.db
   ```
5. Run the server:
   ```bash
   python main.py
   ```
6. The backend will start on `http://localhost:3000`. You should see `Database Initialized (WAL mode enabled)` in the terminal.

---

## 🌐 2. Dashboard Setup (React + Vite)

The dashboard provides real-time visualization of active rides and risk levels.

### Step-by-Step
1. Open a second terminal and navigate to the dashboard directory:
   ```bash
   cd "d:/Safe Corridor/dashboard"
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. The dashboard will automatically open or be available at `http://localhost:5173`.
5. *Note: Ensure the backend is running so the dashboard can connect via WebSocket (you'll see a green "Connected" dot in the sidebar).*

---

## 📱 3. Android App Setup (Kotlin)

The Android app acts as the sensor array, utilizing a Foreground Service to collect GPS telemetry and buffer it using a local Room DB during network drops.

### Addressing the Java Version Mismatch
The app requires **Java 17** to compile, but standard terminal environments often default to Java 8. **Do not run `./gradlew` in a standalone terminal unless your `JAVA_HOME` is explicitly set to Java 17.**

### Step-by-Step (Using Android Studio)
1. Open **Android Studio**.
2. Go to **File > Open**.
3. Select this EXACT folder: `d:\Safe Corridor\android-app\SafeCorridorTracker`.
4. Wait for the initial Gradle Sync to complete (watch the bottom status bar). Android Studio will automatically use its internal bundled Java 17.

### Configuration
1. Open the `local.properties` file in the root of the Android project (`android-app/SafeCorridorTracker/local.properties`).
2. Add your API key so it matches the backend `.env`:
   ```properties
   api.key=your_super_secure_api_key_here
   ```
3. Sync the project with Gradle files again if prompted.

### Running on an Emulator or Device
1. Select your target device/emulator from the device dropdown in the top toolbar.
2. Click the **Run** button (the green Play icon) or press `Shift + F10`.
3. The app will install and open.
4. **Important:** When prompted, you MUST grant the app "Allow all the time" location permissions to ensure the foreground service works correctly when the screen is off.

### Building an APK manually
If you just want an APK to transfer to a physical phone:
1. In Android Studio, go to the top menu: **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
2. When finished, a notification popup will appear in the bottom right corner. Click **"locate"** to open the output folder containing your `app-debug.apk`.

---

## 🧪 Quick Test Flow

1. Start the Backend.
2. Start the Dashboard (Ensure it shows "Connected").
3. Launch the Android App on an emulator.
4. Click **"Start Ride"** on the Android app.
5. The Dashboard should instantly reflect a new active session and begin plotting the GPS vectors.
6. Click **"End Ride"** on the Android app to gracefully terminate the session and trigger the privacy hard-delete on the backend.
