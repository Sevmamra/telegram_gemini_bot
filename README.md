# telegram_gemini_bot

# 🤖 Gemini Telegram Bot

This is a powerful Telegram bot built with `python-telegram-bot` and powered by Google's Gemini API. It offers conversational AI, a custom start message with rich media and interactive buttons, channel subscription checks, a broadcast messaging feature for admins, and detailed user activity logging to a private channel.

## ✨ Features

* **Gemini AI Integration:** Engage in natural language conversations powered by Google's cutting-edge Gemini Pro model.
* **Custom Start Message:** Greets new users with a personalized message, an image, and multiple inline buttons linking to your resources.
* **Multiple Button Links:** Easily add call-to-action buttons with custom URLs in the start message.
* **User Message Reply:** Replies to all user text messages using Gemini's conversational capabilities.
* **Mandatory Channel Subscription:** (Optional) Requires users to subscribe to a specified Telegram channel before they can use the bot.
* **Admin Broadcast Messaging:** An authorized admin can send messages to all users who have interacted with the bot.
* **User Activity Logging:** Sends detailed logs of user interactions (username, profile link, message content) to a private Telegram channel for monitoring.
* **Docker Support:** Containerized for consistent and portable deployments across various platforms.
* **Deployment Options:** Ready for deployment on Koyeb, Render, and compatible with VS Code for local development.

## 📁 Project Structure

telegram_gemini_bot/
├── main.py                 # Core bot logic, handlers, and Flask webhook server
├── requirements.txt        # Python dependencies
├── Procfile                # Defines how to run the app on platforms like Koyeb/Render (via Gunicorn)
├── Dockerfile              # Instructions to build the Docker image
├── start_image.jpg         # Your custom image for the /start command
├── .env                    # Environment variables for local development (DO NOT COMMIT!)
├── .gitignore              # Specifies files/folders to ignore in Git
└── user_chats.txt          # Stores chat IDs for the broadcast feature (managed by bot)

## 🛠️ Prerequisites

Before you begin, ensure you have the following:

1.  **Telegram Bot Token:**
    * Go to Telegram and search for `@BotFather`.
    * Start a chat, send `/newbot`, and follow the instructions.
    * You will receive an **API Token**. Keep it secure.
2.  **Google Gemini API Key:**
    * Go to [Google AI Studio](https://aistudio.google.com/).
    * Create a new project or select an existing one.
    * Generate an **API Key** for Gemini.
3.  **Required Channel ID (Optional):**
    * If you want to enforce channel subscription, add your bot as an administrator to the Telegram channel.
    * Forward any message from that channel to `@JsonDumpBot` or `@RawDataBot`.
    * Copy the `chat.id` (it will be a negative number, e.g., `-1001234567890`).
4.  **Admin User ID:**
    * Your own Telegram User ID (numeric) to authorize the `/broadcast` command. Find it using `@userinfobot` in Telegram.
5.  **Log Channel ID (Optional):**
    * Create a **private** Telegram channel.
    * Add your bot as an **administrator** to this channel.
    * Forward any message from that channel to `@JsonDumpBot` or `@RawDataBot`.
    * Copy the `chat.id` (negative number, e.g., `-1001234567891`).
6.  **`start_image.jpg`:** Place your desired custom image in the project root named `start_image.jpg` (or adjust the filename in `main.py`).

## ⚙️ Local Development with VS Code

This section guides you on running and testing the bot on your local machine using VS Code.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/telegram-gemini-bot.git](https://github.com/your-username/telegram-gemini-bot.git)
    cd telegram-gemini-bot
    ```
2.  **Set up Python Virtual Environment:**
    ```bash
    python -m venv venv
    # Activate the virtual environment
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create `.env` file:** In the root of your project, create a file named `.env` and populate it with your API keys and IDs. **Do NOT commit this file to Git.**
    ```dotenv
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    REQUIRED_CHANNEL_ID="-1001234567890" # Optional: your channel ID
    WEBHOOK_URL="YOUR_NGROK_PUBLIC_URL/webhook" # This will be the URL ngrok provides
    PORT="8080"
    ADMIN_USER_ID="YOUR_TELEGRAM_USER_ID"
    LOG_CHANNEL_ID="-1001234567891" # Optional: your log channel ID
    ```
5.  **Install & Run `ngrok` (for webhook tunneling):**
    * Download `ngrok` from [ngrok.com/download](https://ngrok.com/download).
    * Open a new terminal and run: `ngrok http 8080`
    * `ngrok` will provide a public HTTPS URL (e.g., `https://abcdef123456.ngrok-free.app`). Copy this URL and update the `WEBHOOK_URL` in your `.env` file (remember to append `/webhook`).
6.  **Run the Bot:**
    * Open the project folder in VS Code.
    * Open `main.py`.
    * Go to the "Run and Debug" view (Ctrl+Shift+D / Cmd+Shift+D) and click "Run Python File".
    * Alternatively, in your activated terminal, run: `python main.py`
    * The Flask server will start on `http://0.0.0.0:8080`.
7.  **Set Telegram Webhook (Locally):**
    * Once your bot is running locally and `ngrok` is active, send the `/setwebhook` command to your bot in Telegram. This instructs Telegram to send updates to your `ngrok` tunnel.
8.  **Interact & Debug:** Chat with your bot in Telegram. You can set breakpoints in VS Code to debug your code.

## 🐳 Docker Deployment

Docker allows you to package your bot and its dependencies into a consistent, portable unit, making deployment reliable across environments.

1.  **Install Docker:** Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed.
2.  **Build the Docker Image:**
    * Navigate to your project root in the terminal (where `Dockerfile` is located).
    * Run:
        ```bash
        docker build -t telegram-gemini-bot .
        ```
        This builds the image and tags it `telegram-gemini-bot`.
3.  **Run the Docker Container (Locally):**
    * Replace placeholder values with your actual API keys and IDs.
    * For `WEBHOOK_URL` here, use your `ngrok` URL if testing locally, or your deployed service URL if deploying to a cloud VM.
    ```bash
    docker run -d -p 8080:8080 \
      --name my-telegram-bot-instance \
      -e TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN" \
      -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY" \
      -e REQUIRED_CHANNEL_ID="-1001234567890" \
      -e WEBHOOK_URL="YOUR_NGROK_PUBLIC_URL/webhook" \
      -e ADMIN_USER_ID="YOUR_TELEGRAM_USER_ID" \
      -e LOG_CHANNEL_ID="-1001234567891" \
      telegram-gemini-bot
    ```
4.  **Set Telegram Webhook:** After the Docker container is running and exposed (e.g., via `ngrok` if local), send `/setwebhook` to your bot.

## 🚀 Cloud Deployment

The bot is designed for easy deployment on platforms that support Git-driven deployments or Docker containers.

**Important:** For cloud deployment, you will set environment variables directly in the platform's dashboard, **NOT** in the `.env` file (which should remain local and not committed to Git).

### 1. Deploying on Koyeb

Koyeb offers seamless Git-driven or Docker deployments.

1.  **Push to Git:** Ensure your code (excluding `.env` and `user_chats.txt`) is pushed to a GitHub, GitLab, or Bitbucket repository.
2.  **Create App on Koyeb:**
    * Sign up/Log in to [koyeb.com](https://www.koyeb.com/).
    * Click "Create App".
    * Choose "Git" (recommended for simplicity) or "Docker" (if you want to push your image to a registry like Docker Hub).
3.  **Configure Service:**
    * **Repository:** Select your bot's repository.
    * **Branch:** Choose the branch to deploy.
    * **Build Type:** Python (auto-detected).
    * **Run Command:** `gunicorn -w 4 --bind 0.0.0.0:$PORT main:app` (This will be auto-detected from `Procfile`).
    * **Environment Variables:** Add all your required variables:
        * `TELEGRAM_BOT_TOKEN`
        * `GEMINI_API_KEY`
        * `REQUIRED_CHANNEL_ID` (Optional)
        * `ADMIN_USER_ID`
        * `LOG_CHANNEL_ID` (Optional)
        * `WEBHOOK_URL`: This will be `https://<YOUR_KOYEB_APP_NAME>.koyeb.app/webhook`. You can get your app's URL after the first deploy and then update this variable.
        * `PORT`: Koyeb manages this internally; no need to set it.
4.  **Deploy & Set Webhook:** After deployment, copy your app's public URL from Koyeb dashboard, append `/webhook`, and send the `/setwebhook` command to your bot in Telegram.

### 2. Deploying on Render

Render provides a similar smooth deployment experience.

1.  **Push to Git:** Ensure your code is pushed to a Git repository.
2.  **Create Web Service on Render:**
    * Sign up/Log in to [render.com](https://render.com/).
    * Click "New" -> "Web Service".
    * Connect your Git repository.
3.  **Configure Service:**
    * **Name:** Give your service a unique name.
    * **Region:** Choose a region.
    * **Branch:** Select your deployment branch.
    * **Runtime:** Python 3.
    * **Build Command:** `pip install -r requirements.txt`
    * **Start Command:** `gunicorn -w 4 --bind 0.0.0.0:$PORT main:app`
    * **Environment Variables (Advanced Section):** Add all your required variables:
        * `TELEGRAM_BOT_TOKEN`
        * `GEMINI_API_KEY`
        * `REQUIRED_CHANNEL_ID` (Optional)
        * `ADMIN_USER_ID`
        * `LOG_CHANNEL_ID` (Optional)
        * `WEBHOOK_URL`: This will be `https://<YOUR_RENDER_SERVICE_NAME>.onrender.com/webhook`.
        * `PORT`: Render manages this automatically; no need to set.
    * **Instance Type:** Consider a paid instance for consistent 24/7 uptime.
4.  **Deploy & Set Webhook:** After deployment, copy your service's public URL from Render dashboard, append `/webhook`, and send the `/setwebhook` command to your bot in Telegram.

### 3. Cloudflare (Advanced - Not Recommended for Direct Deployment)

While Cloudflare is powerful, directly deploying a `python-telegram-bot` application as a traditional web server (using Flask/Gunicorn) on Cloudflare Workers is **not straightforward** and generally not the intended use case. Cloudflare Workers are serverless functions optimized for edge computing, and our current bot structure (which relies on a persistent Flask app to handle webhooks) isn't a native fit.

**Challenges:**

* Requires significant refactoring of the bot's architecture to fit the Cloudflare Worker model.
* The concept of `PORT` (like 8080) is not applicable in Cloudflare Workers.
* Persistence for `user_chats.txt` would require using Cloudflare KV storage.

**Recommendation:** For this project setup, **Koyeb or Render are the highly recommended deployment platforms.** If Cloudflare is a strict requirement, be prepared for a more advanced development effort to adapt the bot to their serverless function paradigm.

## 🤝 Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to add new features, please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
