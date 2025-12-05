# 🚀 AI Co-Director - Quick Start Guide

Get up and running with AI Co-Director in 5 minutes!

## ⚡ Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API Key (for AI features)
- FFmpeg (for video processing)

## 📋 Step-by-Step Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/attrisandeep/AI-Co-Director-A-Multimodal-AI-System.git
cd AI-Co-Director-A-Multimodal-AI-System
```

### 2️⃣ Start Frontend (Terminal 1)
```bash
cd frontend
npm install
npm start
```
✅ Frontend running at: **http://localhost:3000**

### 3️⃣ Start Script Writer API (Terminal 2)
```bash
cd backend/script-writer-api
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key-here" > .env
python api.py
```
✅ API running at: **http://localhost:7860**

### 4️⃣ Start Emotion Analysis API (Terminal 3)
```bash
cd backend/multimodal-emotion-backend
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key-here" > .env
python main.py
```
✅ API running at: **http://localhost:8000**

## 🎬 Using the Application

### Script Transformation
1. Open http://localhost:3000
2. Navigate to "Script Transformer"
3. Select genre and paste/upload script
4. Click "Generate" and download result

### Emotion Analysis
1. Navigate to "Video Analyzer"
2. Upload your acting video
3. Enter intended emotion
4. Get AI analysis and recommendations

## 🐳 Quick Docker Setup

```bash
# Build all services
docker-compose up -d

# Or individually:
cd backend/script-writer-api
docker build -t script-writer .
docker run -p 7860:7860 script-writer

cd ../multimodal-emotion-backend
docker build -t emotion-backend .
docker run -p 8000:8000 emotion-backend
```

## 🔑 API Keys Setup

Get your OpenAI API key from: https://platform.openai.com/api-keys

Create `.env` files:

**backend/script-writer-api/.env**:
```
OPENAI_API_KEY=sk-your-key-here
```

**backend/multimodal-emotion-backend/.env**:
```
OPENAI_API_KEY=sk-your-key-here
```

## ⚠️ Troubleshooting

### Port Already in Use
```bash
# Change ports in:
# - frontend/package.json (PORT=3001)
# - backend/*/main.py or api.py
```

### FFmpeg Not Found
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

### Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### CUDA/GPU Issues
```bash
# Force CPU mode
export CUDA_VISIBLE_DEVICES=""
```

## 📖 Full Documentation

For detailed setup, architecture, and API documentation, see [README.md](README.md)

## 🆘 Need Help?

- **Issues**: https://github.com/attrisandeep/AI-Co-Director-A-Multimodal-AI-System/issues
- **Email**: attrisandeep030@gmail.com
- **LinkedIn**: [sandeep-attri-b39669252](https://linkedin.com/in/sandeep-attri-b39669252)

---

**Happy Creating! 🎬✨**
