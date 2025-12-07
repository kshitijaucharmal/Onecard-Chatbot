# OneCard Bot

A web application consisting of a Python backend and a React.js frontend.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

  * **Python 3.13.x**
  * **React.js & npm**

-----

## ⚙️ Installation

### 1\. Backend Setup

Navigate to the root directory of the project and install the required Python dependencies.

```bash
pip install -r requirements.txt
```

### 2\. Frontend Setup

Navigate to the frontend folder and install the Node dependencies.

```bash
cd onecard-bot
npm install
```

-----

## 🚀 Running the Application

To run the full application, you will need to open **three separate terminal windows/tabs** to keep all services running simultaneously.

### Step 1: Start Mock APIs (Terminal 1)

In your first terminal (root directory), start the mock API service:

```bash
python mock_apis.py
```

### Step 2: Start the Backend (Terminal 2)

In your second terminal (root directory), start the main backend server:

```bash
python backend.py
```

### Step 3: Start the Frontend (Terminal 3)

In your third terminal, navigate to the frontend folder and start the React development server:

```bash
cd onecard-bot
npm run dev
```

### Step 4: Access the UI

Once the frontend server is running, your default web browser should open automatically.

If it does not, look at the Terminal 3 output for the `localhost` URL (usually `http://localhost:3000` or `http://localhost:5173` for Vite/React) and open it manually.

-----

## 🛠️ Tech Stack

  * **Backend:** Python
  * **Frontend:** React.js
  * **API:** Mock APIs & Custom Backend using FastAPI
  * **Agent** Google ADK
  * **Database** SQLite DB

-----

## 🤝 Contributing

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes.
4.  Push to the branch and open a Pull Request.
