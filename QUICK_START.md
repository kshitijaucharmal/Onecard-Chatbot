# Quick Start Guide

## 🚀 Fastest Way to Get Started

### 1. Install Dependencies
```bash
make install
```

### 2. Setup Database
```bash
make setup-db
```

### 3. Start Everything
```bash
./start.sh
```

That's it! Open http://localhost:5173 in your browser.

---

## 📊 Startup Options Comparison

| Method | Command | Best For | Pros | Cons |
|--------|---------|----------|------|------|
| **Shell Script** | `./start.sh` | Linux/Mac users | Simple, logs to files | Not Windows-native |
| **Python Script** | `python3 start.py` | Cross-platform | Works everywhere | Requires Python |
| **Makefile** | `make start-all-in-one` | Developers | Flexible commands | Requires `make` |
| **Docker** | `docker-compose up` | Production-like | Isolated, consistent | Requires Docker |
| **Manual** | 3 terminals | Debugging | Full control | More work |

---

## 🎯 Recommended Workflow

**For Development:**
```bash
# Use shell script for convenience
./start.sh
```

**For Production/Testing:**
```bash
# Use Docker for consistency
docker-compose up
```

**For Debugging:**
```bash
# Use manual method to see all output
# Terminal 1: python3 mock_apis.py
# Terminal 2: python3 backend.py  
# Terminal 3: cd onecard-bot && npm run dev
```

---

## 🛑 Stopping Services

| Method | Stop Command |
|--------|-------------|
| Shell Script | `Ctrl+C` |
| Python Script | `Ctrl+C` |
| Makefile | `make stop` |
| Docker | `docker-compose down` |
| Manual | `Ctrl+C` in each terminal |

---

## 📝 Common Commands

```bash
# View all available commands
make help

# Check logs
make logs

# Clean up
make clean

# Full setup + start
make dev
```

---

## ⚡ Troubleshooting

**Port already in use?**
```bash
# Find and kill processes
make stop
# OR manually:
pkill -f mock_apis.py
pkill -f backend.py
pkill -f vite
```

**Services not starting?**
- Check `logs/` directory for errors
- Verify `.env` file exists with `GOOGLE_API_KEY`
- Ensure Python 3.13+ and Node.js are installed

