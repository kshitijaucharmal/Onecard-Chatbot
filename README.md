# OneCard Bot

An AI-powered credit card assistant with a Python backend and React.js frontend, featuring RAG (Retrieval Augmented Generation) and Google ADK agent capabilities.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python 3.13.x**
* **Node.js & npm**
* **Google API Key** (set in `.env` file as `GOOGLE_API_KEY`)

---

## ⚙️ Installation

### Quick Setup

```bash
# Install all dependencies
make install
# OR manually:
pip install -r requirements.txt
cd onecard-bot && npm install
```

### Database Setup

```bash
# Initialize and seed the database
make setup-db
# OR manually:
python3 setup_database.py
```

---

## 🚀 Running the Application

You have **multiple options** to run the application - choose what works best for you!

### Option 1: Shell Script (Recommended for Linux/Mac)

**Single command to start everything:**

```bash
./start.sh
```

This starts all three services in the background. Press `Ctrl+C` to stop all services.

**Features:**
- ✅ Starts all services automatically
- ✅ Logs saved to `logs/` directory
- ✅ Clean shutdown on Ctrl+C
- ✅ Color-coded output

---

### Option 2: Python Script (Cross-platform)

**Works on Windows, Linux, and Mac:**

```bash
python3 start.py
```

**Features:**
- ✅ Cross-platform compatibility
- ✅ Process management
- ✅ Automatic cleanup on exit

---

### Option 3: Makefile Commands

**Simple commands for common tasks:**

```bash
# Start all services in background
make start-all-in-one

# Start individual services
make start-mock      # Mock API only (Port 5000)
make start-backend   # Backend only (Port 8000)
make start-frontend  # Frontend only (Port 5173)

# View logs
make logs

# Stop all services
make stop

# Clean up logs and cache
make clean

# See all available commands
make help
```

---

### Option 4: Docker Compose (Isolated Environment)

**Run everything in containers:**

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

**Note:** Make sure to create a `.env` file with your `GOOGLE_API_KEY` before running.

---

### Option 5: Manual (Three Terminals) - Original Method

If you prefer to run services manually for debugging:

**Terminal 1 - Mock API:**
```bash
python3 mock_apis.py
```

**Terminal 2 - Backend:**
```bash
python3 backend.py
```

**Terminal 3 - Frontend:**
```bash
cd onecard-bot
npm run dev
```

---

## 🌐 Accessing the Application

Once all services are running:

* **Frontend UI:** http://localhost:5173
* **Backend API:** http://localhost:8000/docs
* **Mock API:** http://localhost:5000/docs

---

## 📁 Project Structure

```
FPL/
├── backend.py              # AI Backend (FastAPI + Google ADK)
├── mock_apis.py            # Mock Banking API Server
├── setup_database.py       # Database initialization
├── requirements.txt        # Python dependencies
├── onecard-bot/           # React frontend
│   ├── src/
│   └── package.json
├── start.sh               # Shell startup script
├── start.py               # Python startup script
├── Makefile               # Make commands
├── docker-compose.yml     # Docker setup
└── logs/                  # Application logs
```

> 💡 **Want a better structure?** See [STRUCTURE_PROPOSAL.md](./STRUCTURE_PROPOSAL.md) for a more organized layout.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Google ADK (Gemini 2.5 Flash Lite)
* **Frontend:** React 19, Vite, Tailwind CSS
* **AI/ML:** RAG with vector embeddings (Google GenAI)
* **Database:** SQLite
* **Tools:** 11 agent tools for banking operations

---

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

## 📝 Features

### User Capabilities
- ✅ Open accounts and check account details
- ✅ Track card delivery status
- ✅ Block/freeze cards
- ✅ View bills and make payments
- ✅ View transactions and convert to EMI
- ✅ Report transaction disputes
- ✅ Check collections/risk status
- ✅ Ask general questions (via RAG knowledge base)

### AI Capabilities
- ✅ Distinguishes general queries vs. user-specific actions
- ✅ Requires `customer_id` for account-specific queries
- ✅ Confirms before money movement actions
- ✅ Empathetic handling for high-risk customers

---

## 🐛 Troubleshooting

### Services won't start
- Check if ports 5000, 8000, and 5173 are available
- Verify Python and Node.js are installed
- Ensure `.env` file exists with `GOOGLE_API_KEY`

### Database errors
- Run `make setup-db` to reinitialize the database
- Check if `onecard.db` exists in the root directory

### Logs
- Check `logs/` directory for service logs
- Use `make logs` to view recent logs
- For Docker: `docker-compose logs -f`

---

## 🤝 Contributing

1. Fork the repository
2. Create a new feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes
4. Push to the branch and open a Pull Request

---

## 📄 License

This project is for demonstration purposes.
