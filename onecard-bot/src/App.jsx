import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import {
  Mic,
  Send,
  LogOut,
  CreditCard,
  PieChart,
  Shield,
  Volume2,
  StopCircle,
  Plus,
  Search,
  MoreHorizontal,
  Folder,
  MessageSquare,
  Image as ImageIcon,
  FileText,
  Languages,
  LayoutGrid,
  Settings,
  ChevronDown,
  Bookmark,
  Monitor,
  Music,
  Video,
  Sun,
  Moon,
  Clock,
  CheckCircle2,
  Sparkles,
  ArrowRight,
} from "lucide-react";

// --- CONFIGURATION ---
const API_URL = "http://localhost:8000/chat";
// Removed external API dependency for audio to ensure it works natively

// --- MOCK DATA ---
const FOLDERS = [
  { name: "Support Tickets", count: 3 },
  { name: "Transaction Disputes", count: 12 },
  { name: "EMI Plans", count: 5 },
  { name: "Reward Points", count: 2 },
];

const HISTORY_ITEMS = [
  { title: "Northern lights trip budget", date: "2 mins ago", type: "Plan" },
  { title: "Loyalty program analysis", date: "1 hour ago", type: "Work" },
  { title: "Gift ideas for client", date: "Yesterday", type: "Personal" },
  { title: "Quarterly spend report", date: "2 days ago", type: "Finance" },
  { title: "Credit limit increase", date: "Last week", type: "Request" },
];

const SUGGESTED_ACTIONS = [
  { title: "Create welcome form", sub: "Write code for a simple..." },
  { title: "Analyze Spending", sub: "How to organize your expenses?" },
  { title: "Credit Score Tips", sub: "Tips to improve credit health" },
];

function App() {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState("light"); // 'light' or 'dark'

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  if (!user) {
    return <LoginScreen onLogin={setUser} />;
  }

  return (
    <MainLayout
      user={user}
      onLogout={() => setUser(null)}
      theme={theme}
      setTheme={setTheme}
    />
  );
}

// --- LOGIN SCREEN ---
const LoginScreen = ({ onLogin }) => {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === "1234") {
      onLogin({ id: userId || "User" });
    } else {
      setError("Invalid credentials. Password is 1234.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#1e1f2b] text-white w-full font-sans selection:bg-orange-500 selection:text-white">
      <div className="w-full max-w-md p-8 bg-[#2b2c3d] rounded-3xl border border-[#3e3f54] shadow-2xl relative overflow-hidden">
        {/* Decorative gradient blob */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-orange-500 rounded-full blur-[60px] opacity-20"></div>

        <div className="text-center mb-8 relative z-10">
          <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-orange-500/20">
            <CreditCard className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">PrismPay AI</h1>
          <p className="text-gray-400 mt-2 text-sm">MindMerge Theme Edition</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-5 relative z-10">
          <div>
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5 block">
              User ID
            </label>
            <input
              type="text"
              className="w-full bg-[#1e1f2b] border border-[#3e3f54] rounded-xl p-3.5 text-white focus:border-orange-500 focus:ring-1 focus:ring-orange-500 outline-none transition-all placeholder-gray-600"
              placeholder="e.g. cust_919d"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5 block">
              Password
            </label>
            <input
              type="password"
              className="w-full bg-[#1e1f2b] border border-[#3e3f54] rounded-xl p-3.5 text-white focus:border-orange-500 focus:ring-1 focus:ring-orange-500 outline-none transition-all placeholder-gray-600"
              placeholder="1234"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
          <button className="w-full bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-400 hover:to-pink-400 text-white font-bold py-3.5 rounded-xl transition-all active:scale-[0.98] shadow-lg shadow-orange-500/25">
            Access Dashboard
          </button>
        </form>
      </div>
    </div>
  );
};

// --- MAIN LAYOUT ---
const MainLayout = ({ user, onLogout, theme, setTheme }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null); // Ref to store recognition instance

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async (textOverride) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;

    const newMessages = [...messages, { role: "user", content: textToSend }];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post(API_URL, {
        user_id: user.id,
        query: textToSend,
      });

      const botResponse = response.data.response;
      setMessages([...newMessages, { role: "bot", content: botResponse }]);
      handleTextToSpeech(botResponse);
    } catch (error) {
      setMessages([
        ...newMessages,
        {
          role: "bot",
          content:
            "⚠️ **Connection Error**: I couldn't reach the PrismPay server. Is it running on port 8000?",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextToSpeech = (text) => {
    // Switch to Browser Native TTS for reliability without API Key
    const cleanText = text.replace(/[*#_]/g, "");

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel(); // Stop any previous speech
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1;
      utterance.pitch = 1;
      // Optional: attempt to pick a better voice if available, otherwise default
      const voices = window.speechSynthesis.getVoices();
      if (voices.length > 0) {
        const preferred = voices.find((v) => v.lang.includes("en"));
        if (preferred) utterance.voice = preferred;
      }
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn("Text-to-speech not supported in this browser.");
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      // Stop recording
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition; // Store in ref
      recognition.lang = "en-US";
      recognition.start();
      setIsRecording(true);

      recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setInput((prev) => (prev ? prev + " " + transcript : transcript)); // Append to existing text
        setIsRecording(false);
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };
    } else {
      alert("Speech recognition not supported in this browser.");
    }
  };

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <div
      className={`flex w-full h-screen font-sans overflow-hidden transition-colors duration-300 ${theme === "dark" ? "bg-[#09090b]" : "bg-[#f3f4f6]"}`}
    >
      {/* LEFT SIDEBAR (Always Dark as per reference image style) */}
      <aside className="w-[280px] flex flex-col bg-[#1e1f2b] text-gray-400 p-5 hidden md:flex shrink-0 z-20 shadow-xl">
        {/* Logo Area */}
        <div className="flex items-center gap-3 mb-10 px-2">
          <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/20">
            <Sparkles size={20} className="text-white" />
          </div>
          <span className="font-bold text-xl text-white tracking-tight">
            PrismPay AI
          </span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-6 overflow-y-auto no-scrollbar">
          <div>
            <div className="px-3 py-2 bg-[#2b2c3d] text-white rounded-lg flex items-center gap-3 mb-4 cursor-pointer border-l-4 border-orange-500 shadow-md">
              <MessageSquare size={18} className="text-orange-500" />
              <span className="font-medium text-sm">AI Chat Helper</span>
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#2b2c3d] cursor-pointer group transition text-gray-400 hover:text-white">
              <div className="flex items-center gap-3">
                <FileText size={18} />
                <span className="font-medium text-sm">Templates</span>
              </div>
              <span className="text-[10px] font-bold bg-orange-500/20 text-orange-400 px-1.5 py-0.5 rounded">
                PRO
              </span>
            </div>
            <div className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#2b2c3d] cursor-pointer group transition text-gray-400 hover:text-white">
              <div className="flex items-center gap-3">
                <LayoutGrid size={18} />
                <span className="font-medium text-sm">My Projects</span>
              </div>
              <span className="text-[10px] font-bold bg-orange-500/20 text-orange-400 px-1.5 py-0.5 rounded">
                PRO
              </span>
            </div>
            <div className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#2b2c3d] cursor-pointer group transition text-gray-400 hover:text-white">
              <div className="flex items-center gap-3">
                <PieChart size={18} />
                <span className="font-medium text-sm">Statistics</span>
              </div>
              <span className="text-[10px] font-bold bg-orange-500/20 text-orange-400 px-1.5 py-0.5 rounded">
                PRO
              </span>
            </div>
            <div className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#2b2c3d] cursor-pointer group transition text-gray-400 hover:text-white">
              <div className="flex items-center gap-3">
                <Settings size={18} />
                <span className="font-medium text-sm">Settings</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#2b2c3d]">
            <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 px-3">
              Folders
            </div>
            <div className="space-y-1">
              {FOLDERS.map((folder, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#2b2c3d] cursor-pointer group transition"
                >
                  <div className="flex items-center gap-3 group-hover:text-white">
                    <Folder size={16} />
                    <span className="text-sm">{folder.name}</span>
                  </div>
                  <span className="text-xs text-gray-600">{folder.count}</span>
                </div>
              ))}
            </div>
          </div>
        </nav>

        {/* Pro Plan Card (Bottom Left) */}
        <div className="mt-6 p-4 rounded-2xl bg-gradient-to-br from-orange-500 to-pink-600 relative overflow-hidden text-white shadow-lg">
          <div className="absolute top-0 right-0 w-24 h-24 bg-white opacity-10 rounded-full -mr-10 -mt-10 blur-xl"></div>
          <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center mb-3">
            <Sparkles size={20} className="text-white" />
          </div>
          <h3 className="font-bold text-lg leading-tight mb-1">Metal Plan</h3>
          <p className="text-xs text-white/80 mb-3 leading-snug">
            Get premium AI insights for your portfolio.
          </p>
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold">
              $10 <span className="text-xs font-normal text-white/70">/mo</span>
            </span>
            <button className="bg-white text-orange-600 text-xs font-bold px-3 py-1.5 rounded-full hover:bg-gray-100 transition">
              Get
            </button>
          </div>
        </div>

        {/* Logout */}
        <div className="mt-4 flex items-center justify-between px-2 pt-4 border-t border-[#2b2c3d]">
          <div
            className="flex items-center gap-2 text-sm font-medium hover:text-white cursor-pointer"
            onClick={onLogout}
          >
            <LogOut size={16} />
            <span>Log out</span>
          </div>
          <ArrowRight size={16} />
        </div>
      </aside>

      {/* CENTER MAIN CONTENT */}
      <main
        className={`flex-1 flex flex-col relative transition-colors duration-300 ${theme === "dark" ? "bg-[#0f1016]" : "bg-[#f8f9fa]"} `}
      >
        {/* Header */}
        <header
          className={`h-20 flex items-center px-8 justify-between shrink-0 z-10 transition-colors duration-300 ${theme === "dark" ? "bg-[#0f1016] border-b border-[#1e1f2b]" : "bg-white border-b border-gray-100"}`}
        >
          <div className="flex items-center gap-4">
            <h2
              className={`text-xl font-bold ${theme === "dark" ? "text-white" : "text-gray-800"}`}
            >
              AI Chat Helper
            </h2>
          </div>

          <div className="flex items-center gap-4">
            {/* Search Bar */}
            <div
              className={`hidden md:flex items-center px-4 py-2.5 rounded-xl border ${theme === "dark" ? "bg-[#1e1f2b] border-[#2b2c3d] text-white" : "bg-gray-50 border-gray-200 text-gray-700"} w-64 transition-colors duration-300`}
            >
              <Search size={16} className="text-gray-400 mr-2" />
              <input
                type="text"
                placeholder="Search"
                className="bg-transparent border-none outline-none text-sm w-full placeholder-gray-400"
              />
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className={`p-2.5 rounded-xl border transition-all ${theme === "dark" ? "bg-[#1e1f2b] border-[#2b2c3d] text-yellow-400 hover:text-yellow-300" : "bg-white border-gray-200 text-gray-500 hover:text-orange-500 shadow-sm"}`}
            >
              {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Notifications */}
            <button
              className={`p-2.5 rounded-xl border transition-all relative ${theme === "dark" ? "bg-[#1e1f2b] border-[#2b2c3d] text-gray-400" : "bg-white border-gray-200 text-gray-500 shadow-sm"}`}
            >
              <div className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-[#1e1f2b]"></div>
              <Monitor size={20} />
            </button>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-hidden flex flex-col relative">
          {messages.length === 0 ? (
            // --- EMPTY STATE ---
            <div className="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto">
              <div
                className={`text-center max-w-2xl w-full ${theme === "dark" ? "text-white" : "text-gray-800"}`}
              >
                <div className="w-20 h-20 bg-gradient-to-tr from-orange-400 to-pink-500 rounded-3xl mx-auto mb-8 flex items-center justify-center shadow-xl shadow-orange-500/30">
                  <CreditCard size={40} className="text-white" />
                </div>
                <h1 className="text-4xl font-bold mb-4 tracking-tight">
                  How can I help you?
                </h1>
                <p
                  className={`text-lg mb-10 max-w-lg mx-auto leading-relaxed ${theme === "dark" ? "text-gray-400" : "text-gray-500"}`}
                >
                  I can help you analyze your PrismPay spending, manage your
                  limits, or clarify transaction details.
                </p>

                {/* Suggestion Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-8">
                  {[
                    "Check Credit Limit",
                    "Analyze Expenses",
                    "Report an Issue",
                  ].map((item, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(item)}
                      className={`p-6 rounded-2xl border text-left transition-all hover:-translate-y-1 hover:shadow-lg group ${theme === "dark" ? "bg-[#1e1f2b] border-[#2b2c3d] hover:border-orange-500/50" : "bg-white border-gray-200 shadow-sm hover:border-orange-300"}`}
                    >
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center mb-4 transition-colors ${theme === "dark" ? "bg-[#2b2c3d] text-orange-500 group-hover:bg-orange-500 group-hover:text-white" : "bg-orange-50 text-orange-500 group-hover:bg-orange-500 group-hover:text-white"}`}
                      >
                        {i === 0 ? (
                          <Shield size={20} />
                        ) : i === 1 ? (
                          <PieChart size={20} />
                        ) : (
                          <Video size={20} />
                        )}
                      </div>
                      <h3
                        className={`font-bold mb-1 ${theme === "dark" ? "text-white" : "text-gray-800"}`}
                      >
                        {item}
                      </h3>
                      <p
                        className={`text-xs ${theme === "dark" ? "text-gray-500" : "text-gray-400"}`}
                      >
                        Get instant details.
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            // --- CHAT MESSAGES ---
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth pb-32">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex gap-4 max-w-[85%] items-end ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold shadow-md ${msg.role === "user" ? "bg-gray-200 text-gray-700" : "bg-gradient-to-br from-orange-400 to-pink-500 text-white"}`}
                    >
                      {msg.role === "user" ? "ME" : "AI"}
                    </div>

                    {/* Bubble & Actions */}
                    <div
                      className={`flex flex-col gap-2 max-w-full ${msg.role === "user" ? "items-end" : "items-start"}`}
                    >
                      <div
                        className={`p-5 rounded-2xl text-sm leading-relaxed shadow-sm relative ${
                          msg.role === "user"
                            ? "bg-orange-500 text-white rounded-tr-sm"
                            : theme === "dark"
                              ? "bg-[#1e1f2b] text-gray-200 border border-[#2b2c3d]"
                              : "bg-white text-gray-700 border border-gray-100 rounded-tl-sm"
                        }`}
                      >
                        {msg.role === "bot" ? (
                          <ReactMarkdown
                            components={{
                              strong: ({ node, ...props }) => (
                                <span
                                  className={`font-bold ${theme === "dark" ? "text-white" : "text-gray-900"}`}
                                  {...props}
                                />
                              ),
                              ul: ({ node, ...props }) => (
                                <ul
                                  className="list-disc ml-4 space-y-2 my-2"
                                  {...props}
                                />
                              ),
                              li: ({ node, ...props }) => (
                                <li className="" {...props} />
                              ),
                              p: ({ node, ...props }) => (
                                <p className="mb-2 last:mb-0" {...props} />
                              ),
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        ) : (
                          msg.content
                        )}
                      </div>

                      {/* Read Aloud Button */}
                      <button
                        onClick={() => handleTextToSpeech(msg.content)}
                        className={`p-1.5 rounded-full transition-colors flex items-center gap-1.5 text-[10px] font-medium opacity-60 hover:opacity-100 ${theme === "dark" ? "hover:bg-white/10 text-gray-400" : "hover:bg-black/5 text-gray-500"}`}
                        title="Read aloud"
                      >
                        <Volume2 size={14} />
                        <span>Read</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start w-full pl-14">
                  <div
                    className={`px-4 py-3 rounded-2xl flex items-center gap-2 ${theme === "dark" ? "bg-[#1e1f2b]" : "bg-white"}`}
                  >
                    <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce"></span>
                    <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce delay-75"></span>
                    <span className="w-2 h-2 bg-orange-400 rounded-full animate-bounce delay-150"></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Input Area (Bottom) */}
          <div
            className={`p-6 z-20 transition-colors duration-300 ${theme === "dark" ? "bg-[#0f1016]" : "bg-[#f8f9fa]"}`}
          >
            <div
              className={`relative max-w-4xl mx-auto flex items-center p-2 rounded-2xl shadow-lg border transition-all focus-within:ring-2 focus-within:ring-orange-500/50 ${theme === "dark" ? "bg-[#1e1f2b] border-[#2b2c3d]" : "bg-white border-gray-200"}`}
            >
              <button className="p-3 text-gray-400 hover:text-orange-500 transition">
                <Plus size={20} />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Type your message..."
                className={`flex-1 bg-transparent border-none outline-none px-2 ${theme === "dark" ? "text-white placeholder-gray-500" : "text-gray-800 placeholder-gray-400"}`}
              />
              <div className="flex items-center gap-2 pr-2">
                <button
                  onClick={toggleRecording}
                  className={`p-2 rounded-xl transition ${isRecording ? "text-red-500 bg-red-500/10 animate-pulse" : "text-gray-400 hover:bg-gray-100 dark:hover:bg-[#2b2c3d]"}`}
                  title="Hold to record"
                >
                  {isRecording ? <StopCircle size={20} /> : <Mic size={20} />}
                </button>
                <button
                  onClick={() => sendMessage()}
                  disabled={!input.trim()}
                  className="bg-orange-500 hover:bg-orange-600 text-white p-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-orange-500/20"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
            <div className="text-center mt-3">
              <p className="text-[10px] text-gray-400">
                Free Research Preview. PrismPay AI may produce inaccurate
                information.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* RIGHT SIDEBAR (History/Suggestions) */}
      <aside
        className={`w-[300px] hidden xl:flex flex-col border-l p-6 overflow-y-auto transition-colors duration-300 ${theme === "dark" ? "bg-[#0f1016] border-[#1e1f2b]" : "bg-white border-gray-100"}`}
      >
        <div className="flex items-center justify-between mb-6">
          <h3
            className={`font-bold ${theme === "dark" ? "text-white" : "text-gray-800"}`}
          >
            History
          </h3>
          <span className="text-xs text-gray-400 bg-gray-100 dark:bg-[#1e1f2b] px-2 py-1 rounded-full">
            6/50
          </span>
        </div>

        <div className="space-y-4 mb-8">
          {SUGGESTED_ACTIONS.map((action, i) => (
            <div
              key={i}
              className={`p-4 rounded-xl border cursor-pointer transition-all hover:shadow-md group ${theme === "dark" ? "bg-[#1e1f2b] border-[#2b2c3d] hover:border-orange-500/50" : "bg-white border-gray-200 hover:border-orange-300"}`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`mt-1 w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${theme === "dark" ? "border-gray-600" : "border-gray-300"}`}
                ></div>
                <div>
                  <h4
                    className={`text-sm font-bold mb-1 ${theme === "dark" ? "text-gray-200 group-hover:text-white" : "text-gray-700 group-hover:text-black"}`}
                  >
                    {action.title}
                  </h4>
                  <p className="text-xs text-gray-500 leading-snug">
                    {action.sub}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mb-4">
          <h3
            className={`font-bold mb-4 ${theme === "dark" ? "text-white" : "text-gray-800"}`}
          >
            Recent Chats
          </h3>
          <div className="space-y-0">
            {HISTORY_ITEMS.map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-4 py-3 border-b border-dashed border-gray-200 dark:border-[#1e1f2b] last:border-0"
              >
                <div className="mt-1 text-gray-300 dark:text-gray-600">
                  <Clock size={14} />
                </div>
                <div>
                  <h5
                    className={`text-xs font-bold mb-0.5 ${theme === "dark" ? "text-gray-300" : "text-gray-700"}`}
                  >
                    {item.title}
                  </h5>
                  <p className="text-[10px] text-gray-500">
                    {item.date} • {item.type}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-auto">
          <button
            className={`w-full py-3 rounded-xl border flex items-center justify-center gap-2 text-sm font-medium transition-all ${theme === "dark" ? "border-[#2b2c3d] text-gray-400 hover:text-white hover:bg-[#1e1f2b]" : "border-gray-200 text-gray-500 hover:text-gray-800 hover:bg-gray-50"}`}
          >
            <LogOut size={16} />
            <span>Clear history</span>
          </button>
        </div>
      </aside>
    </div>
  );
};

export default App;
