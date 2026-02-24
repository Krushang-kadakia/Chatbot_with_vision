# How to Setup ngrok for Public Access

This guide will walk you through setting up **ngrok** so you can share your local chatbot with friends over the internet.

## Step 1: Create an Account
1.  Go to [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup).
2.  Sign up using your GitHub account or Google account (it's fastest).
3.  Once logged in, you will see your **Dashboard**.

## Step 2: Download ngrok
1.  On the ngrok dashboard, look for the **Download** button for Windows.
2.  Download the ZIP file (e.g., `ngrok-v3-stable-windows-amd64.zip`).
3.  **Extract** the ZIP file:
    - Right-click the file > "Extract All..."
    - Extract it to a folder you can easily find, like `C:\ngrok` or your Desktop.

## Step 3: Connect Your Account
1.  On your [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken), click on **"Your Authtoken"** on the left sidebar.
2.  Copy the token code that looks like `2F...5kL`.
3.  Open a **Command Prompt** (cmd) on your computer.
4.  Navigate to the folder where you extracted ngrok.
    - Example: `cd C:\Users\YourUser\Desktop` (if you put it there).
5.  Run this command (paste your token):
    ```bash
    ngrok config add-authtoken <YOUR_TOKEN_HERE>
    ```
    *You should see a message saying "Authtoken saved".*

## Step 4: Start the Tunnel
1.  Make sure your Chatbot API is running first!
    - Double-click `run_api.bat` in your Chatbot folder.
2.  In the command prompt (where ngrok is), run:
    ```bash
    ngrok http 8000
    ```
3.  You will see a screen turn black with status lines. Look for the **Forwarding** line:
    ```
    Forwarding                    https://a1b2-c3d4.ngrok-free.app -> http://localhost:8000
    ```
4.  Copy that `https://...` URL. This is your **Public URL**.

## Step 5: Share and Test
1.  Send that URL to your friend (e.g., `https://a1b2-c3d4.ngrok-free.app`).
2.  They can now use that URL to access your chatbot API documentation at `https://<YOUR_URL>/docs` (if you want them to see the test page) or use it in their app.

## Important Notes
- **Do not close the ngrok window.** If you close it, the public link stops working.
- **The URL changes every time.** If you restart ngrok, you get a new random URL.
