# Development & Deployment Workflow

This guide explains how to develop `baby_oclock` on your main MacBook and deploy changes to your dedicated Server MacBook.

## The Concept
1.  **Develop:** Write code and test on your Main Mac.
2.  **Push:** Save changes to GitHub.
3.  **Deploy:** The Server Mac pulls the changes and restarts the app.

---

## Part 1: Developing on Main Mac (This Machine)

### 1. Run the App Locally (Testing Mode)
When you want to work on the app, run it manually here to see your changes instantly.

```bash
# Start the app in debug mode
./start.sh
```
*   Visit: `http://localhost:8080`
*   *Note:* This does NOT affect the live server. It uses your local `feeds.xlsx`.

### 2. Push Changes
When you are happy with your changes:

```bash
# 1. Add changes
git add .

# 2. Commit
git commit -m "Description of what you changed"

# 3. Push to GitHub
git push origin main
```

---

## Part 2: Deploying to Server

**Option A: Manual Pull (Simple)**
SSH into your server (or open its terminal) and run:

```bash
cd ~/Documents/baby_oclock
git pull
# The app might need a restart if you changed python code (not HTML/CSS)
launchctl kickstart -k gui/$(id -u)/com.nicholaskanhai.babyoclock
```

**Option B: One-Command Deployment (Recommended)**
We can create a script on the **SERVER** to do this for you.

1.  **On the Server**, create `deploy.sh`:
    ```bash
    nano ~/Documents/baby_oclock/deploy.sh
    ```

2.  **Paste this code:**
    ```bash
    #!/bin/bash
    cd ~/Documents/baby_oclock
    echo "⬇️ Pulling latest changes..."
    git pull origin main
    
    echo "🔄 Restarting App..."
    # Restart the background service
    launchctl kickstart -k gui/$(id -u)/com.nicholaskanhai.babyoclock
    
    echo "✅ Deployed Successfully!"
    ```

3.  **Make it executable:**
    ```bash
    chmod +x ~/Documents/baby_oclock/deploy.sh
    ```

4.  **To Deploy:**
    Just run `./deploy.sh` on the server whenever you push new code!

---

## Part 3: Syncing Data (Optional)
Remember, the **Server** has the "Real" database (`feeds.xlsx`). Your development machine has a "Test" database.

If you ever want to see the real data on your dev machine:
1.  Copy `feeds.xlsx` from Server -> Dev Machine.
2.  **NEVER** push `feeds.xlsx` to GitHub (it is ignored).
