# 🤖 Gemini Telegram Bot

This is a powerful Telegram bot built with `python-telegram-bot` and powered by Google's Gemini API. It offers conversational AI, a custom start message with rich media and interactive buttons, channel subscription checks, a broadcast messaging feature for admins, and detailed user activity logging to a private channel.

## ✨ Features

* **Gemini AI Integration:** Engage in natural language conversations powered by Google's cutting-edge Gemini Pro model.
* **Custom Start Message:** Greets new users with a personalized message, an image, and multiple inline buttons linking to your resources.
* **Multiple Button Links:** Easily add call-to-action buttons with custom URLs in the start message.
* **User Message Reply:** Replies to all user text messages using Gemini's conversational capabilities (toggleable).
* **Mandatory Channel Subscription:** (Optional) Requires users to subscribe to a specified Telegram channel before they can use the bot (toggleable).
* **Admin Broadcast Messaging:** An authorized admin can send messages to all users who have interacted with the bot (toggleable).
* **User Activity Logging:** Sends detailed logs of user interactions (user ID, name, username, profile link, message content, timestamp) to a private Telegram channel for monitoring (toggleable).
* **Docker Support:** Containerized for consistent and portable deployments across various platforms.
* **Deployment Options:** Ready for deployment on Koyeb, Render, and compatible with VS Code for local development.

## 📁 Project Structure
telegram_gemini_bot/
├── main.py                 # Core bot logic, handlers, and Flask webhook server
├── config.py               # Stores all configurations: IDs, messages, feature toggles, etc.
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
    * You will receive an **API Token**.
2.  **Google Gemini API Key:**
    * Go to [Google AI Studio](https://aistudio.google.com/).
    * Create a new project or select an existing one.
    * Generate an **API Key** for Gemini.
3.  **Required Channel ID (Optional for subscription check):**
    * If you want to enforce channel subscription, add your bot as an administrator to the Telegram channel.
    * Forward any message from that channel to `@JsonDumpBot` or `@RawDataBot`.
    * Copy the `chat.id` (it will be a negative number, e.g., `-1001234567890`). This ID goes into `config.py`.
4.  **Admin User ID (Optional for broadcast):**
    * Your own Telegram User ID (numeric) to authorize the `/broadcast` command. Find it using `@userinfobot` in Telegram. This ID goes into `config.py`.
5.  **Log Channel ID (Optional for activity logging):**
    * Create a **private** Telegram channel.
    * Add your bot as an **administrator** to this channel.
    * Forward any message from that channel to `@JsonDumpBot` or `@RawDataBot`.
    * Copy the `chat.id` (negative number, e.g., `-1001234567891`). This ID goes into `config.py`.
6.  **`start_image.jpg`:** Place your desired custom image (recommended size around 500x500 pixels) in the project root named `start_image.jpg`.

## ⚙️ Local Development with VS Code

This section guides you on running and testing the bot on your local machine using VS Code.

1.  **Install Prerequisites:**
    * Install [VS Code](https://code.visualstudio.com/).
    * Install the Python extension by Microsoft in VS Code.
    * Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (if you plan to use Docker locally).
    * Download and configure `ngrok` from [ngrok.com/download](https://ngrok.com/download).
2.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/telegram-gemini-bot.git](https://github.com/your-username/telegram-gemini-bot.git)
    cd telegram-gemini-bot
    ```
3.  **Set up Python Virtual Environment:**
    ```bash
    python -m venv venv
    # Activate the virtual environment
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure `config.py`:** Open `config.py` and set your `REQUIRED_CHANNEL_ID`, `ADMIN_USER_ID`, `LOG_CHANNEL_ID`, `START_MESSAGE_BUTTONS`, and enable/disable features using `ENABLE_USER_MESSAGE_REPLY`, `ENABLE_CHANNEL_SUBSCRIPTION_CHECK`, `ENABLE_BROADCAST`, `ENABLE_USER_LOG_CHANNEL`. **Crucially, fill in `TELEGRAM_BOT_TOKEN` and `GEMINI_API_KEY` placeholders here for local testing if you don't use `.env` overrides.**
6.  **Create `.env` file (Optional for overrides):** If you prefer to keep sensitive keys out of `config.py` even locally, create a `.env` file in the project root. Variables set here will override those in `config.py`. **Do NOT commit this file to Git.**
    ```dotenv
    # .env
    TELEGRAM_BOT_TOKEN="YOUR_ACTUAL_BOT_TOKEN"
    GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
    # WEBHOOK_URL="YOUR_NGROK_PUBLIC_URL_WITH_WEBHOOK_PATH" # e.g., [https://abcdef123456.ngrok-free.app/webhook](https://abcdef123456.ngrok-free.app/webhook)
    # You can also override IDs here if needed for local testing
    # REQUIRED_CHANNEL_ID="-1001234567890"
    # ADMIN_USER_ID="1234567890"
    # LOG_CHANNEL_ID="-1001234567891"
    ```
7.  **Start `ngrok` (for webhook tunneling):**
    * Open a new terminal (separate from your VS Code terminal).
    * Run: `ngrok http 8080`
    * `ngrok` will provide a public HTTPS URL (e.g., `https://abcdef123456.ngrok-free.app`). Copy this URL and ensure it's either set as `WEBHOOK_URL` in your `.env` file (preferred for local testing) or update `config.py`'s `WEBHOOK_URL_DEFAULT` (less ideal as it's a configuration file). Remember to append `/webhook` to the URL. Keep this `ngrok` terminal open while testing.
8.  **Run the Bot:**
    * Open the project folder in VS Code.
    * Open `main.py`.
    * Go to the "Run and Debug" view (Ctrl+Shift+D / Cmd+Shift+D) and click "Run Python File".
    * Alternatively, in your activated terminal within VS Code, run: `python main.py`
    * The Flask server will start and listen on `http://0.0.0.0:8080`.
9.  **Set Telegram Webhook (Locally):**
    * Once your bot is running locally and `ngrok` is active, send the `/setwebhook` command to your bot in Telegram. This instructs Telegram to send updates to your `ngrok` tunnel.
10. **Interact & Debug:** Chat with your bot in Telegram. You can set breakpoints in VS Code to debug your code.

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
3.  **Run the Docker Container (Locally or on a VM):**
    * Replace placeholder values with your actual API keys and IDs. These are passed as environment variables to the container, overriding any values in `config.py`.
    * For `WEBHOOK_URL` here, use your `ngrok` URL if testing locally, or your deployed service URL if deploying to a cloud VM.
    ```bash
    docker run -d -p 8080:8080 \
      --name my-telegram-bot-instance \
      -e TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN" \
      -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY" \
      -e REQUIRED_CHANNEL_ID="-1001234567890" \
      -e ADMIN_USER_ID="1234567890" \
      -e LOG_CHANNEL_ID="-1001234567891" \
      -e WEBHOOK_URL="YOUR_PUBLIC_DEPLOYMENT_URL/webhook" \
      telegram-gemini-bot
    ```
4.  **Set Telegram Webhook:** After the Docker container is running and exposed (e.g., via `ngrok` if local, or directly if on a publicly accessible VM), send `/setwebhook` to your bot.

## 🚀 Cloud Deployment

The bot is designed for easy deployment on platforms that support Git-driven deployments or Docker containers.

**Important:** For cloud deployment, you will set sensitive environment variables directly in the platform's dashboard, **NOT** in the `.env` file (which should remain local and not committed to Git). Non-sensitive configurations from `config.py` will be included in the deployed code.

### 1. Deploying on Koyeb

Koyeb offers seamless Git-driven or Docker deployments.

1.  **Push to Git:** Ensure your code (including `config.py`, but excluding `.env` and `user_chats.txt`) is pushed to a GitHub, GitLab, or Bitbucket repository.
2.  **Create App on Koyeb:**
    * Sign up/Log in to [koyeb.com](https://www.koyeb.com/).
    * Click "Create App".
    * Choose "Git" (recommended for simplicity, Koyeb will use your `Procfile` and `Dockerfile` if present) or "Docker" (if you've pushed your image to a registry like Docker Hub).
3.  **Configure Service:**
    * **Repository:** Select your bot's repository.
    * **Branch:** Choose the branch to deploy.
    * **Build Type:** Python (auto-detected).
    * **Run Command:** `gunicorn -w 4 --bind 0.0.0.0:$PORT main:app` (This will be auto-detected from `Procfile` or `Dockerfile`).
    * **Environment Variables:** Add your required variables in the Koyeb dashboard:
        * `TELEGRAM_BOT_TOKEN` (Crucial for bot to function)
        * `GEMINI_API_KEY` (Crucial for AI to function)
        * `REQUIRED_CHANNEL_ID` (If `ENABLE_CHANNEL_SUBSCRIPTION_CHECK` is `True` in `config.py` and you want to override `config.py` value)
        * `ADMIN_USER_ID` (If `ENABLE_BROADCAST` is `True` in `config.py` and you want to override `config.py` value)
        * `LOG_CHANNEL_ID` (If `ENABLE_USER_LOG_CHANNEL` is `True` in `config.py` and you want to override `config.py` value)
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
    * **Environment Variables (Advanced Section):** Add your required variables in the Render dashboard:
        * `TELEGRAM_BOT_TOKEN`
        * `GEMINI_API_KEY`
        * *(Optional - if you want to override `config.py` values)*: `REQUIRED_CHANNEL_ID`, `ADMIN_USER_ID`, `LOG_CHANNEL_ID`.
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

## 📚 Learn More

* **`python-telegram-bot` Documentation:** [https://python-telegram-bot.org/](https://python-telegram-bot.org/)
* **Google Gemini API Documentation:** [https://ai.google.dev/](https://ai.google.dev/)
* **Flask Documentation:** [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
* **Gunicorn Documentation:** [https://gunicorn.org/](https://gunicorn.org/)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **Koyeb Documentation:** [https://www.koyeb.com/docs](https://www.koyeb.com/docs)
* **Render Documentation:** [https://render.com/docs](https://render.com/docs)
* **`ngrok` Documentation:** [https://ngrok.com/docs](https://ngrok.com/docs)

## 🤝 Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to add new features, please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
