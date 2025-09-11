# DataSaudi Chatbot

A bilingual (Arabic/English) AI-powered chatbot that provides insights and answers about Saudi Arabia's economic and statistical data. The system uses advanced language models, vector search, and real-time data processing to deliver accurate, source-cited responses.

## 🌟 Features

- **Bilingual Support**: Seamlessly handles questions in both Arabic and English
- **Real-time Data**: Processes and answers questions about Saudi Arabia's latest economic indicators
- **Source Citation**: Always provides sources for information transparency
- **Modern UI**: Beautiful, responsive chat interface with glassmorphism design
- **Rich Formatting**: Markdown-rendered responses with bold numbers, bullet points, and organized data
- **Vector Search**: Advanced semantic search using Weaviate Cloud vector database
- **Multi-source Data**: Integrates data from multiple Saudi government sources (GASTAT, SAMA, MOF, PMI)
- **Cloud-First Architecture**: All data stored in Weaviate Cloud for scalability and reliability

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Vector DB     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Weaviate)    │
│                 │    │                 │    │                 │
│ • React UI      │    │ • Answer Agent  │    │ • Embeddings    │
│ • TypeScript    │    │ • Data Pipeline │    │ • Chunk Storage │
│ • Tailwind CSS  │    │ • LLM Client    │    │ • Semantic Search│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Sources  │
                       │                 │
                       │ • GASTAT APIs   │
                       │ • SAMA Data     │
                       │ • MOF Reports   │
                       │ • PMI Data      │
                       └─────────────────┘
```

## 📁 Project Structure

```
data-saudi-chatbot/
├── front_end/                 # Next.js React frontend
│   ├── src/app/              # App router pages
│   ├── public/               # Static assets
│   └── package.json          # Frontend dependencies
├── back_end/                 # Python FastAPI backend
│   ├── agents/               # AI agents and prompt management
│   ├── data/                 # Processed data and embeddings
│   ├── embedding/            # Text embedding utilities
│   ├── llm/                  # Language model client
│   ├── processing/           # Data processing pipeline
│   ├── scraping/             # Data fetching and scraping
│   ├── sql/                  # SQL query generation
│   ├── vectordb/             # Vector database operations
│   └── main.py               # FastAPI application
├── docker-compose.yml        # Weaviate database setup
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **OpenAI API Key**
- **Weaviate Cloud Account** (recommended) or Docker for local Weaviate

### 1. Clone the Repository

```bash
git clone <repository-url>
cd data-saudi-chatbot
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Weaviate Cloud Configuration (recommended)
WEAVIATE_URL=https://your-cluster-url.weaviate.network
WEAVIATE_API_KEY=your_weaviate_api_key_here

# Optional: Custom model configurations
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-large
```

### 3. Vector Database Setup

#### Option A: Weaviate Cloud (Recommended)

1. **Create a Weaviate Cloud account** at [console.weaviate.cloud](https://console.weaviate.cloud)
2. **Create a new cluster** and get your cluster URL and API key
3. **Add the credentials** to your `.env` file (already done in step 2)

#### Option B: Local Weaviate (Alternative)

If you prefer to run Weaviate locally:

```bash
# Uncomment the weaviate service in docker-compose.yml first
docker-compose up -d
```

This starts Weaviate vector database on `http://localhost:8080`

### 4. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run data pipeline (first time only)
python back_end/main.py --run-pipeline

# Start the API server
python back_end/main.py
```

The backend will be available at `http://localhost:8000`

### 5. Frontend Setup

```bash
cd front_end

# Install dependencies
npm install

# Optional: Check for outdated packages
npm outdated

# Optional: Update packages to latest versions
npm update

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## ☁️ Weaviate Cloud Benefits

This project is designed **cloud-first** with Weaviate Cloud providing several advantages:

- **🚀 Scalability**: Automatic scaling based on your needs
- **🔒 Security**: Enterprise-grade security and compliance
- **🌍 Global Access**: Access your data from anywhere
- **📊 Monitoring**: Built-in monitoring and analytics
- **🔄 Backup**: Automatic backups and disaster recovery
- **💰 Cost-Effective**: Pay only for what you use
- **🛠️ Maintenance-Free**: No server management required
- **🧹 Clean Local Environment**: No local data storage - everything in the cloud
- **⚡ Fast Deployment**: No need to set up local databases
- **📊 Rich Responses**: Markdown-formatted answers with bold numbers and organized data
- **🔄 Auto-Cleanup**: Temporary files automatically removed after processing

## 📊 Data Sources

The chatbot integrates data from multiple Saudi government sources:

- **GASTAT (General Authority for Statistics)**
  - GDP quarterly and yearly data
  - Inflation rates by city
  - Industrial Production Index
  - Wholesale Price Index

- **SAMA (Saudi Arabian Monetary Authority)**
  - Money supply statistics
  - Monthly and yearly financial data

- **MOF (Ministry of Finance)**
  - Government revenues and expenditures
  - Quarterly fiscal reports

- **PMI (Purchasing Managers' Index)**
  - Economic activity indicators

## 🔧 Configuration

### Model Configuration

Edit `back_end/agents/prompts.json` to customize:

- **LLM Model**: Change the language model (default: `gpt-5-chat-latest`)
- **Embedding Model**: Change embedding model (default: `text-embedding-3-large`)
- **Search Parameters**: Adjust `search_top_k`, `max_tokens`, `temperature`
- **Prompts**: Customize system prompts for different languages

### Frontend Configuration

The frontend uses:
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **React Simple Typewriter** for animations
- **React Markdown** for rich text formatting
- **Lucide React** for modern icons

## 🛠️ Development

### Running the Data Pipeline

To update the data and embeddings:

```bash
python back_end/main.py --run-pipeline
```

This will:
1. Fetch latest data from all sources
2. Process and chunk the data
3. Generate embeddings
4. Store in Weaviate Cloud
5. Clean up local temporary files automatically

**Note**: The pipeline processes approximately 12,000+ data chunks and stores them in Weaviate Cloud with automatic cleanup of local files.

### API Endpoints

- `POST /api/ask` - Main chat endpoint
  - **Input**: `{"question": "your question here"}`
  - **Output**: `{"answer": "markdown-formatted response", "context": ["source1", "source2"]}`

### Response Formatting

The chatbot returns responses with rich markdown formatting:
- **Bold text** for important numbers and categories
- Bullet points for organized lists
- *Italic text* for source citations
- Clean paragraph structure for readability

### Adding New Data Sources

1. Create a new fetcher in `back_end/scraping/`
2. Add data processing logic in `back_end/processing/`
3. Update the pipeline in `back_end/pipeline.py`
4. Test with the data pipeline

## 🌐 Deployment

### Production Setup

1. **Environment Variables**: Set production API keys and configurations
2. **Database**: Use production Weaviate instance
3. **Frontend**: Build and deploy to Vercel/Netlify
4. **Backend**: Deploy to cloud provider (AWS, GCP, Azure)

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Saudi Government Data Sources**: GASTAT, SAMA, MOF for providing open data
- **OpenAI**: For powerful language models and embeddings
- **Weaviate**: For vector database capabilities
- **Next.js & React**: For the modern frontend framework

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs` folder

---

**DataSaudi Chatbot** - Your gateway to Saudi Arabia's data insights 🇸🇦
