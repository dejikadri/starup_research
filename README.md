##


# Startup Research API

A comprehensive FastAPI application for managing startup research data with AI-powered analytics using ChatGPT integration.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Serper API key (for research crew)

### Environment Setup

1. **Clone and navigate to the project directory**
```bash
cd startup_research
```

2. **Install dependencies**
```bash
pip install -r requirement.txt
```

3. **Set up environment variables**
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  # Optional
```

## 📊 Step 1: Generate Research Data

Before using the API, you need to populate the results file by running the research crew.

### Option A: Run the Main Research Script
```bash
python research_startups.py
```

This will:
- Generate a list of 10 startups
- Research each startup comprehensively
- Save results to `research_results.json`
- Automatically save to SQLite database

### Option B: Run Batch Processing (Recommended for reliability)
```bash
python research_startups_batch.py
```

This approach:
- Processes startups in smaller batches (3 at a time)
- Reduces API rate limit issues
- Saves intermediate results
- More reliable for large datasets

### Option C: Parse Existing Results
If you already have result files:
```bash
python parse_results_to_db.py all
```

## 🌐 Step 2: Start the API Server

### Start the FastAPI server
```bash
python api.py
```

The server will start on `http://localhost:8000`

### Alternative startup methods
```bash
# With auto-reload for development
uvicorn api:app --reload

# Custom host and port
uvicorn api:app --host 0.0.0.0 --port 8080
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔗 API Endpoints

### 1. Root Endpoint
```http
GET /
```
**Description**: Get API information and available endpoints

**Response**:
```json
{
  "message": "Startup Research API",
  "version": "1.0.0",
  "endpoints": {
    "save_from_file": "/save-from-file",
    "view_data": "/startups",
    "database_stats": "/stats",
    "query_analytics": "/query"
  }
}
```

### 2. Save Data from File
```http
POST /save-from-file?filename={filename}
```
**Description**: Parse result files and save startup data to the database

**Parameters**:
- `filename` (query): File to parse (default: "research_results.json")
  - Use `"all"` to process all available result files

**Examples**:
```bash
# Save from specific file
curl -X POST "http://localhost:8000/save-from-file?filename=research_results.json"

# Save from all available files
curl -X POST "http://localhost:8000/save-from-file?filename=all"
```

**Response**:
```json
{
  "message": "Successfully processed research_results.json",
  "startups_found": 10,
  "startups_saved": 10
}
```

### 3. Get All Startups
```http
GET /startups
```
**Description**: Retrieve startups from the database with optional filtering

**Query Parameters**:
- `limit` (int): Maximum number of startups to return (default: 100)
- `industry` (string): Filter by industry sector
- `founding_year` (int): Filter by founding year

**Examples**:
```bash
# Get all startups (limited to 100)
curl "http://localhost:8000/startups"

# Get first 5 startups
curl "http://localhost:8000/startups?limit=5"

# Get AI startups
curl "http://localhost:8000/startups?industry=AI&limit=10"

# Get startups founded in 2020
curl "http://localhost:8000/startups?founding_year=2020"
```

**Response**:
```json
{
  "total_returned": 5,
  "startups": [
    {
      "id": 1,
      "company_name": "Example Startup",
      "website_url": "https://example.com",
      "founding_year": 2020,
      "founders": ["John Doe", "Jane Smith"],
      "business_model": "SaaS platform for...",
      "industry_sector": "AI/ML",
      "funding_rounds": [
        {
          "Amount": "$5 million",
          "Date": "June 2021"
        }
      ],
      "total_capital_raised": "$5 million",
      "current_revenue_estimates": "Not disclosed",
      "employee_count": 50,
      "customer_user_base_size": "10,000+ users",
      "key_partnerships": ["Google", "Microsoft"],
      "major_competitors": ["Competitor A", "Competitor B"],
      "recent_news_developments": "Launched new AI feature",
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

### 4. Get Specific Startup
```http
GET /startups/{startup_id}
```
**Description**: Get detailed information about a specific startup

**Parameters**:
- `startup_id` (path): Database ID of the startup

**Example**:
```bash
curl "http://localhost:8000/startups/1"
```

### 5. Database Statistics
```http
GET /stats
```
**Description**: Get comprehensive database statistics

**Example**:
```bash
curl "http://localhost:8000/stats"
```

**Response**:
```json
{
  "total_startups": 25,
  "industries": ["AI/ML", "Fintech", "Healthtech", "E-commerce"],
  "avg_founding_year": 2020.5,
  "total_funding_disclosed": 18
}
```

### 6. AI-Powered Analytics Query
```http
POST /query
```
**Description**: Ask questions about the startup data using ChatGPT for intelligent analysis

**Request Body**:
```json
{
  "question": "Your analytical question here"
}
```

**Examples**:
```bash
# Ask about industry trends
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 3 industries by startup count and their average funding?"}'

# Ask about competitive landscape
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Which startups are direct competitors and what differentiates them?"}'
```

**Response**:
```json
{
  "question": "What are the top 3 industries by startup count?",
  "answer": "Based on the startup database, the top 3 industries are:\n1. AI/ML (8 startups) - Average funding: $12.5M\n2. Fintech (5 startups) - Average funding: $8.2M\n3. Healthtech (4 startups) - Average funding: $15.1M\n\nThe AI/ML sector shows the highest activity with diverse applications from computer vision to natural language processing...",
  "database_stats": {
    "total_startups": 25,
    "industries": ["AI/ML", "Fintech", "Healthtech"],
    "avg_founding_year": 2020.5,
    "total_funding_disclosed": 18
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🤖 Sample Analytics Questions

Here are example questions you can ask the AI analytics endpoint:

**Industry Analysis**:
- "What are the most common industries and their characteristics?"
- "Which industry has the highest average funding per startup?"
- "What are the emerging trends across different sectors?"

**Funding Analysis**:
- "Which startups have raised the most funding and in what rounds?"
- "What's the average funding amount by founding year?"
- "Which companies are still seeking funding?"

**Competitive Analysis**:
- "Which startups are direct competitors to each other?"
- "What are the different business models in the AI sector?"
- "Which companies have similar target markets?"

**Market Insights**:
- "What recent developments indicate market trends?"
- "Which startups have the most strategic partnerships?"
- "What's the average team size by industry?"

## 🧪 Testing

### Run the test suite
```bash
python test_api.py
```

This will test all endpoints and provide a comprehensive report.

### Manual testing with curl
```bash
# Test API status
curl "http://localhost:8000/"

# Import data
curl -X POST "http://localhost:8000/save-from-file?filename=all"

# View data
curl "http://localhost:8000/startups?limit=3"

# Get analytics
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What industries are represented in the database?"}'
```

## 📁 Project Structure

```
startup_research/
├── api.py                          # FastAPI application
├── research_startups.py            # Main research crew script
├── research_startups_batch.py      # Batch processing script
├── parse_results_to_db.py         # Standalone result parser
├── query_startup_db.py            # Database query utility
├── test_api.py                    # API testing script
├── requirement.txt                # Python dependencies
├── .env                           # Environment variables
├── startup_research.db            # SQLite database (created automatically)
├── research_results.json          # Research results (generated)
└── README.md                      # This file
```

## 🔧 Troubleshooting

### Common Issues

1. **API won't start**: Check if port 8000 is available
2. **No data in database**: Run the research crew first or import existing files
3. **ChatGPT queries fail**: Verify OPENAI_API_KEY is set correctly
4. **Research crew fails**: Check SERPER_API_KEY and internet connection

### Error Handling

The API includes comprehensive error handling:
- 404: File not found or startup not found
- 400: Invalid request data
- 500: Server errors (check logs for details)

## 📊 Database Schema

The SQLite database automatically stores startup data with the following structure:
- Company information (name, website, founding year)
- Founders and team data (stored as JSON)
- Business model and industry classification
- Funding rounds and capital raised (stored as JSON)
- Employee and customer metrics
- Partnerships and competitors (stored as JSON)
- Recent developments and news

## 🚀 Production Deployment

For production deployment, consider:
- Using a production ASGI server like Gunicorn with Uvicorn workers
- Setting up proper environment variable management
- Implementing rate limiting for the ChatGPT endpoint
- Adding authentication and authorization
- Using a production database like PostgreSQL

```bash
# Production example
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```