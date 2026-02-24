# How to Use the Chatbot API in Your Apps

Once you have your API URL (either local `http://...` or public `https://...ngrok-free.app`), you can use it in any application that can make HTTP requests.

## 1. API Endpoint Details
- **URL**: `<YOUR_BASE_URL>/chat`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`

## 2. request Body Format
You must send a JSON object with a `messages` list.
```json
{
  "messages": [
    {
      "role": "user", 
      "content": "Hello, how are you?"
    }
  ],
  "model": "qwen2.5vl:7b" // Optional, defaults to this
}
```

## 3. Response Format
The API returns a JSON object with the assistant's reply.
```json
{
  "role": "assistant",
  "content": "I am doing well, thank you! How can I help you?"
}
```

---

## 4. Using the ngrok Public URL
 When you run `ngrok http 8000`, you get a forwarding URL like `https://a1b2-c3d4.ngrok-free.app`.

 **To use this remotely:**
 1.  Copy the ngrok URL (do NOT include `http://localhost`).
 2.  Add `/chat` to the end.
 3.  Use this new URL in your code.

 **Example:**
 - **Local:** `http://localhost:8000/chat`
 - **Public:** `https://a1b2-c3d4.ngrok-free.app/chat`

 ---

 ## 5. Code Examples


### A. Python (using `requests`)
Perfect for backend scripts or other Python apps.

```python
import requests

# REPLACE THIS LINE with your public ngrok URL if accessing from another machine
# API_URL = "https://your-ngrok-url.ngrok-free.app/chat"
API_URL = "http://localhost:8000/chat" 

payload = {
    "messages": [
        {"role": "user", "content": "Explain quantum physics in 1 sentence."}
    ]
}

try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status() # Raise error for bad status
    
    result = response.json()
    print("Bot says:", result["content"])
    
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

### B. JavaScript / Node.js (using `fetch`)
Perfect for websites, React apps, or mobile apps (React Native).

```javascript
const API_URL = "http://localhost:8000/chat"; // Or your ngrok URL

async function sendMessage(text) {
  const payload = {
    messages: [
      { role: "user", content: text }
    ]
  };

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Bot says:", data.content);
    return data.content;
    
  } catch (error) {
    console.error("Could not talk to bot:", error);
  }
}

// Usage
sendMessage("Hello from JavaScript!");
```

### C. Terminal Commands

**1. Command Prompt (cmd.exe)**
```cmd
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d "{\"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}"
```

**2. PowerShell**
*PowerShell uses different syntax. Copy this exactly:*
```powershell
$body = @{
    messages = @(
        @{ role = "user"; content = "Hello!" }
    )
    model = "qwen2.5vl:7b"
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body $body
```

### D. Sending Images (cURL)
**Note:** Identify that Base64 strings are too long for the command line. You must use a file.

1.  **Create a file** named `payload.json` with your Base64 image:
    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "What is this?",
          "images": ["<YOUR_BASE64_STRING_HERE>"]
        }
      ]
    }
    ```
2.  **Run cURL** pointing to that file:
    ```cmd
    curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d @payload.json
    ```

### E. Sending Images (Python)
The API expects images as **Base64 encoded strings** inside the JSON payload.

```python
import requests
import base64

# 1. Load and encode the image
image_path = "C:/Users/IT Common/Desktop/Chatbot/Test1.png"

with open(image_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

# 2. Prepare payload
API_URL = "http://localhost:8000/chat"
payload = {
    "messages": [
        {
            "role": "user", 
            "content": "What is in this image?",
            "images": [base64_image]  # List of base64 strings
        }
    ]
}

# 3. Send request
try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    print("Bot says:", response.json()["content"])
except Exception as e:
    print(f"Error: {e}")
```

### E. Sending Images (JavaScript)
```javascript
const API_URL = "http://localhost:8000/chat";

// Helper to convert File object to Base64
const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]); // Remove header
    reader.onerror = error => reject(error);
});

async function analyzeImage(fileInput) {
    const file = fileInput.files[0];
    const base64Image = await toBase64(file);

    const payload = {
        messages: [{
            role: "user",
            content: "Describe this image.",
            images: [base64Image]
        }]
    };

    const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    
    const data = await response.json();
    console.log("Bot:", data.content);
}
```

