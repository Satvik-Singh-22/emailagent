# 📧 Email Agent with AI Memory System

An intelligent email agent powered by LangGraph and Gemini, with episodic memory using Supabase vector embeddings.

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Gmail account
- Google Cloud Project with Gmail API enabled
- Gemini API key
- (Optional) Supabase account for memory features

### 2. Installation

```bash
# Clone the repository
cd emailagent

# Install dependencies
pip install -r requirements.txt
```

### 3. Gmail Setup

1. **Get Gmail API Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json` and place in project root

2. **Configure credentials:**
   - Make sure `credentials.json` exists in the project root
   - On first run, you'll be prompted to authenticate via browser

### 4. Environment Configuration

```bash
# Copy .env.example to .env
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_ENABLED=true

# Optional: Enable Supabase for memory features
SUPABASE_ENABLED=false
```

Get Gemini API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 5. (Optional) Supabase Setup for Memory Features

For full episodic memory and context-aware responses, set up Supabase:

**📖 Follow the detailed guide: [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)**

Quick steps:
1. Create Supabase project
2. Run `supabase_setup.sql` in SQL Editor
3. Update `.env` with your credentials
4. Set `SUPABASE_ENABLED=true`
5. Test with `python test_supabase.py`

### 6. Run the Agent

```bash
python main.py
```

---

## 📋 Features

✅ **Smart Email Classification**
- Priority detection (HIGH/MEDIUM/LOW)
- Category classification (ACTION/FYI/LEGAL/etc.)
- Intent recognition (REPLY/SCHEDULE/ESCALATE/etc.)

✅ **Email Composition**
- AI-powered draft generation
- Context-aware responses
- Tone and style customization

✅ **Memory System** (with Supabase)
- Remembers past interactions
- Learns your preferences
- Context-aware suggestions

✅ **Gmail Integration**
- Fetch recent emails
- Send emails
- Thread management

---

## 🧪 Testing

### Test Supabase Connection

```bash
python test_supabase.py
```

This verifies:
- Environment variables
- Supabase connection
- Database schema
- RPC functions
- Embedding generation

### Test Basic Functionality

```bash
python test.py
```

---

## 📁 Project Structure

```
emailagent/
├── app/
│   ├── classification/    # Email classification logic
│   ├── config/           # Configuration
│   ├── gmail/            # Gmail API integration
│   ├── graph/            # LangGraph workflow
│   ├── guardrails/       # Safety checks
│   ├── llm/              # LLM integrations (Gemini/Ollama)
│   ├── memory/           # Episodic memory system
│   ├── nodes/            # Graph nodes
│   ├── policy/           # Business rules
│   └── utils/            # Utilities
├── credentials.json      # Gmail OAuth credentials
├── .env                  # Environment variables
├── main.py              # Entry point
├── requirements.txt      # Dependencies
├── supabase_setup.sql   # Database schema
└── SUPABASE_SETUP_GUIDE.md  # Detailed Supabase guide
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `GEMINI_ENABLED` | Enable Gemini LLM | Yes |
| `SUPABASE_URL` | Supabase project URL | No* |
| `SUPABASE_KEY` | Supabase anon key | No* |
| `SUPABASE_ENABLED` | Enable memory features | No* |

\* Required only for memory features

---

## 💡 Usage Examples

### Check Inbox
```
You: show me last 10 mails
```

### Compose Email
```
You: compose an email to john@example.com about the meeting tomorrow
```

### Reply to Email
```
You: reply to the last email from Sarah
```

---

## 🐛 Troubleshooting

### ❌ `Error: [Errno 2] No such file or directory: 'credentials.json'`

**Solution:** Make sure `credentials.json` exists in the project root. Download it from Google Cloud Console.

### ❌ `Memory retrieval RPC failed: [Errno 11001] getaddrinfo failed`

**Solution:** This means Supabase isn't configured. Either:
- Set up Supabase following [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)
- Or set `SUPABASE_ENABLED=false` in `.env` (agent will work without memory)

### ❌ `relation "episodic_memory" does not exist`

**Solution:** Run the SQL schema from `supabase_setup.sql` in your Supabase SQL Editor.

### ❌ Gmail authentication issues

**Solution:** 
1. Delete `token.pickle` if it exists
2. Run `python main.py` again
3. Complete browser authentication flow

---

## 🔐 Security Notes

- Never commit `.env` or `credentials.json` to version control
- Use environment variables for all secrets
- Enable RLS (Row Level Security) in Supabase for production
- Keep your Gemini API key secure

---

## 📚 Documentation

- [Supabase Setup Guide](SUPABASE_SETUP_GUIDE.md) - Complete Supabase setup
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/) - Workflow framework
- [Gmail API Docs](https://developers.google.com/gmail/api) - Gmail integration
- [Gemini API Docs](https://ai.google.dev/docs) - LLM and embeddings

---

## 🛠️ Development

### Run with debugging
```bash
python main.py
```

### Test Supabase connection
```bash
python test_supabase.py
```

### View logs
The agent prints detailed logs to console for debugging.

---

## 📊 Memory System

When enabled, the agent stores:
- User intents and outcomes
- Email metadata
- Conversation context
- User preferences (tone, style, etc.)

This enables:
- Context-aware responses
- Personalized email composition
- Learning from past interactions
- Smart suggestions

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - feel free to use for personal or commercial projects

---

## 🆘 Need Help?

1. Check [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) for Supabase issues
2. Run `python test_supabase.py` to diagnose problems
3. Check console logs for detailed error messages
4. Ensure all environment variables are set correctly

---

**Happy emailing! 📧🤖**