# 🚀 AI-Driven Customer Feedback Analyzer

A **complete, production-ready**, enterprise-grade customer feedback analysis platform with advanced AI/ML capabilities. Built with FastAPI, React, and powered by state-of-the-art AI models.

> **⚡ Quick Start:** Run `.\start.ps1` and access the app at http://localhost:3000

---

## 🎯 What Is This?

Transform customer feedback into **actionable insights** using AI. This platform automatically:

- 📊 **Analyzes sentiment** (positive/negative/neutral)
- 😊 **Detects emotions** (joy, anger, sadness, etc.)
- 🚨 **Scores urgency** (1-10 scale)
- 🎯 **Prioritizes feedback** (0-100 weighted score)
- 🤖 **Generates AI-powered insights**
- 📈 **Visualizes trends** in real-time
- 🔍 **Identifies patterns** across thousands of feedback items

**Perfect for:** Product teams, Customer Success, Support teams, SaaS companies

---

## 🎯 Features

### Core Capabilities

- **Multi-Format Data Ingestion**: CSV, JSON, Excel, API integrations (Zendesk, Intercom, Freshdesk, HubSpot)
- **Advanced AI Analytics**: Multi-language sentiment analysis, emotion detection, urgency scoring
- **Smart Topic Clustering**: Dynamic topic modeling, custom categories, hierarchical classification
- **Interactive Dashboard**: Real-time analytics, interactive visualizations, export capabilities
- **AI-Powered Insights**: Executive summaries, action items, competitive intelligence
- **Collaborative Workspace**: Team annotations, shared workspaces, role-based access

### Enterprise Features

- Multi-tenant architecture
- White-label capability
- API-first design
- Real-time integrations
- Advanced data science analytics

## 🏗️ Architecture

### Project Structure

```
feedback-analyzer/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality (auth, config, security)
│   │   ├── db/                # Database migrations
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── main.py            # Application entry point
│   ├── tests/                 # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── store/             # Redux store
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── nginx/                      # Nginx configuration
├── docker-compose.yml          # Docker services configuration
├── .env.example               # Environment variables template
├── feedback_sample.csv        # Sample data for testing
└── README.md
```

### System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  FastAPI Backend │────▶│   PostgreSQL    │
│   (Dashboard)   │     │   (REST API)     │     │   (Database)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ├────▶ Redis (Caching)
                               ├────▶ Celery (Background Jobs)
                               └────▶ AI/ML Models (Local/API)
```

## 📦 Tech Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + pgvector
- **Cache**: Redis
- **Task Queue**: Celery
- **AI/ML**: OpenAI, Anthropic, HuggingFace, spaCy

### Frontend

- **Framework**: React 18 + TypeScript
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts + D3.js
- **State Management**: Redux Toolkit

### DevOps

- **Containerization**: Docker + Docker Compose
- **API Documentation**: Swagger/OpenAPI
- **Testing**: Pytest, Jest

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Environment Setup

1. **Clone the repository**

```bash
cd "c:\Users\nani\Desktop\New folder (3)"
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start with Docker Compose**

```bash
docker-compose up -d
```

4. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## 📊 Usage Examples

### Upload Feedback via API

```python
import requests

files = {'file': open('feedback.csv', 'rb')}
response = requests.post('http://localhost:8000/api/v1/feedback/upload', files=files)
```

### Connect to Zendesk

```python
config = {
    "api_key": "your_zendesk_api_key",
    "subdomain": "yourcompany",
    "email": "admin@yourcompany.com"
}
response = requests.post('http://localhost:8000/api/v1/integrations/zendesk/sync', json=config)
```

## 🔧 Configuration

### AI Model Setup

The platform supports both local AI models and API-based models:

**Local Models (Included):**

- Sentiment Analysis: cardiffnlp/twitter-roberta-base-sentiment-latest
- Emotion Detection: j-hartmann/emotion-english-distilroberta-base
- Embeddings: sentence-transformers/all-MiniLM-L6-v2

**API Models (Optional):**

- OpenAI GPT-4 for advanced insights
- Anthropic Claude for analysis
- HuggingFace Inference API

Edit `.env` to configure:

```env
# Optional: For advanced AI features
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
HUGGINGFACE_TOKEN=your-token-here
```

### Database Configuration

Edit `docker-compose.yml` or `.env`:

```env
POSTGRES_DB=feedback_analyzer
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password
```

## 📈 Key Workflows

1. **Feedback Ingestion** → Auto-validation → Storage
2. **AI Analysis** → Sentiment + Emotion + Topics → Embeddings
3. **Clustering** → Group similar feedback → Prioritization
4. **Insights Generation** → Executive summaries → Action items
5. **Alerts** → Slack/Teams notifications → Team collaboration

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting
- Data encryption at rest and in transit
- Multi-tenant data isolation

## 📝 API Documentation

Interactive API documentation available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## 📧 Support

For support, email support@feedbackanalyzer.com or join our Slack channel.

---

**Built with ❤️ for modern product teams**
