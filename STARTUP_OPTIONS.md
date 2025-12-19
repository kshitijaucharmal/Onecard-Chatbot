# Startup Options Summary

## 🎯 Quick Decision Guide

**Choose based on your needs:**

- **Just want it to work?** → Use `./start.sh` (Linux/Mac) or `python3 start.py` (Windows)
- **Like command-line tools?** → Use `make start-all-in-one`
- **Want isolation?** → Use `docker-compose up`
- **Need to debug?** → Use manual method (3 terminals)

---

## 📋 Detailed Options

### 1. Shell Script (`start.sh`) ⭐ Recommended

**Best for:** Linux/Mac users who want simplicity

```bash
./start.sh
```

**What it does:**
- Starts all 3 services in background
- Saves logs to `logs/` directory
- Handles cleanup on Ctrl+C
- Color-coded output

**Pros:**
- ✅ Simple one command
- ✅ Automatic log management
- ✅ Clean shutdown

**Cons:**
- ❌ Not native Windows support (use WSL/Git Bash)

---

### 2. Python Script (`start.py`)

**Best for:** Cross-platform users

```bash
python3 start.py
```

**What it does:**
- Same as shell script but Python-based
- Works on Windows, Linux, Mac
- Process management with cleanup

**Pros:**
- ✅ Cross-platform
- ✅ No shell dependencies
- ✅ Good error handling

**Cons:**
- ❌ Requires Python installed

---

### 3. Makefile Commands

**Best for:** Developers familiar with `make`

```bash
make start-all-in-one    # Start everything
make start-mock          # Start only mock API
make start-backend       # Start only backend
make start-frontend      # Start only frontend
make stop                # Stop all services
make logs                # View logs
make help                # See all commands
```

**Pros:**
- ✅ Flexible - start individual services
- ✅ Common developer tool
- ✅ Easy to extend

**Cons:**
- ❌ Requires `make` installed
- ❌ Less intuitive for beginners

---

### 4. Docker Compose

**Best for:** Production-like testing, isolation

```bash
docker-compose up --build
```

**What it does:**
- Runs all services in containers
- Isolated environment
- Consistent across machines

**Pros:**
- ✅ Complete isolation
- ✅ Consistent environment
- ✅ Easy to share/reproduce
- ✅ Production-ready setup

**Cons:**
- ❌ Requires Docker installed
- ❌ Slower startup (builds images)
- ❌ More resource intensive

---

### 5. Manual (Original Method)

**Best for:** Debugging, understanding the system

**Terminal 1:**
```bash
python3 mock_apis.py
```

**Terminal 2:**
```bash
python3 backend.py
```

**Terminal 3:**
```bash
cd onecard-bot && npm run dev
```

**Pros:**
- ✅ Full control
- ✅ See all output directly
- ✅ Easy to debug individual services

**Cons:**
- ❌ Requires 3 terminals
- ❌ Manual management
- ❌ More work

---

## 🔄 Comparison Table

| Feature | Shell Script | Python Script | Makefile | Docker | Manual |
|---------|-------------|---------------|----------|--------|--------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Cross-platform** | ❌ | ✅ | ⚠️ | ✅ | ✅ |
| **Log Management** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Individual Control** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Isolation** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Setup Required** | None | Python | make | Docker | None |

---

## 💡 Recommendations

**For Daily Development:**
```bash
./start.sh  # or python3 start.py on Windows
```

**For Testing/CI:**
```bash
docker-compose up
```

**For Debugging:**
Use manual method to see all output

**For Team Collaboration:**
Use Docker Compose for consistency

---

## 🛑 Stopping Services

| Method | Command |
|--------|---------|
| Shell/Python Script | `Ctrl+C` |
| Makefile | `make stop` |
| Docker | `docker-compose down` |
| Manual | `Ctrl+C` in each terminal |

---

## 📝 Notes

- All methods start the same 3 services:
  - Mock API (Port 5000)
  - Backend (Port 8000)
  - Frontend (Port 5173)

- Logs are saved to `logs/` directory (except manual method)

- Make sure `.env` file exists with `GOOGLE_API_KEY` before starting

- Database is auto-initialized on first run

