#!/usr/bin/env python3
"""
FastAPI application for startup research database management and analytics.
Provides endpoints for data management and ChatGPT-powered analytics.
"""

import os
import json
import sqlite3
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Startup Research API",
    description="API for managing startup research data and analytics",
    version="1.0.0"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models
class StartupData(BaseModel):
    company_name: str
    website_url: Optional[str] = None
    founding_year: Optional[int] = None
    founders: List[str] = []
    business_model: Optional[str] = None
    industry_sector: Optional[str] = None
    funding_rounds: List[Dict[str, Any]] = []
    total_capital_raised: Optional[str] = None
    current_revenue_estimates: Optional[str] = None
    employee_count: Optional[int] = None
    customer_user_base_size: Optional[str] = None
    key_partnerships: List[str] = []
    major_competitors: List[str] = []
    recent_news_developments: Optional[str] = None

class QueryRequest(BaseModel):
    question: str

class DatabaseStats(BaseModel):
    total_startups: int
    industries: List[str]
    avg_founding_year: Optional[float]
    total_funding_disclosed: int

# Database functions
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('startup_research.db')

def create_startup_database():
    """Create SQLite database and table for startup data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            website_url TEXT,
            founding_year INTEGER,
            founders TEXT,
            business_model TEXT,
            industry_sector TEXT,
            funding_rounds TEXT,
            total_capital_raised TEXT,
            current_revenue_estimates TEXT,
            employee_count INTEGER,
            customer_user_base_size TEXT,
            key_partnerships TEXT,
            major_competitors TEXT,
            recent_news_developments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_startup_to_db(startup_data: dict) -> bool:
    """Save a single startup record to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Handle different field name variations
        company_name = (startup_data.get('Company Name') or 
                       startup_data.get('company_name') or 
                       startup_data.get('name', ''))
        
        website_url = (startup_data.get('Website URL') or 
                      startup_data.get('website_url') or 
                      startup_data.get('website', ''))
        
        founding_year = (startup_data.get('Founding Year') or 
                        startup_data.get('founding_year') or 
                        startup_data.get('founded', None))
        
        founders = json.dumps(startup_data.get('Founders', startup_data.get('founders', [])))
        business_model = (startup_data.get('Business Model') or 
                         startup_data.get('business_model', ''))
        
        industry_sector = (startup_data.get('Industry Sector') or 
                          startup_data.get('industry_sector') or 
                          startup_data.get('industry', ''))
        
        funding_rounds = json.dumps(startup_data.get('Funding Rounds', 
                                                   startup_data.get('funding_rounds', [])))
        
        total_capital_raised = (startup_data.get('Total Capital Raised to Date') or 
                               startup_data.get('total_capital_raised') or 
                               startup_data.get('total_funding', ''))
        
        current_revenue_estimates = (startup_data.get('Current Revenue Estimates') or 
                                   startup_data.get('current_revenue_estimates') or 
                                   startup_data.get('revenue', ''))
        
        employee_count = (startup_data.get('Employee Count') or 
                         startup_data.get('employee_count') or 
                         startup_data.get('employees', None))
        
        customer_user_base_size = (startup_data.get('Customer/User Base Size') or 
                                  startup_data.get('customer_user_base_size') or 
                                  startup_data.get('users', ''))
        
        key_partnerships = json.dumps(startup_data.get('Key Partnerships', 
                                                      startup_data.get('key_partnerships', [])))
        
        major_competitors = json.dumps(startup_data.get('Major Competitors', 
                                                       startup_data.get('major_competitors', [])))
        
        recent_news_developments = (startup_data.get('Recent News or Developments') or 
                                   startup_data.get('recent_news_developments') or 
                                   startup_data.get('recent_news', ''))
        
        cursor.execute('''
            INSERT INTO startups (
                company_name, website_url, founding_year, founders, business_model,
                industry_sector, funding_rounds, total_capital_raised, current_revenue_estimates,
                employee_count, customer_user_base_size, key_partnerships, major_competitors,
                recent_news_developments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name, website_url, founding_year, founders, business_model,
            industry_sector, funding_rounds, total_capital_raised, current_revenue_estimates,
            employee_count, customer_user_base_size, key_partnerships, major_competitors,
            recent_news_developments
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error saving startup to database: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def parse_result_file(filename: str) -> List[dict]:
    """Parse a result file and return startup data"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            return []
        
        # Try to parse as JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            start_idx = content.find('[')
            end_idx = content.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx+1]
                data = json.loads(json_content)
            else:
                return []
        
        # Process the data
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []
            
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        return []

def get_all_startups_from_db() -> List[dict]:
    """Retrieve all startups from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                id, company_name, website_url, founding_year, founders, 
                business_model, industry_sector, funding_rounds, 
                total_capital_raised, current_revenue_estimates, 
                employee_count, customer_user_base_size, key_partnerships, 
                major_competitors, recent_news_developments, created_at
            FROM startups 
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        
        startups = []
        for row in rows:
            startup = {
                'id': row[0],
                'company_name': row[1],
                'website_url': row[2],
                'founding_year': row[3],
                'founders': json.loads(row[4]) if row[4] else [],
                'business_model': row[5],
                'industry_sector': row[6],
                'funding_rounds': json.loads(row[7]) if row[7] else [],
                'total_capital_raised': row[8],
                'current_revenue_estimates': row[9],
                'employee_count': row[10],
                'customer_user_base_size': row[11],
                'key_partnerships': json.loads(row[12]) if row[12] else [],
                'major_competitors': json.loads(row[13]) if row[13] else [],
                'recent_news_developments': row[14],
                'created_at': row[15]
            }
            startups.append(startup)
        
        return startups
        
    except Exception as e:
        print(f"Error querying database: {e}")
        return []
    finally:
        conn.close()

def get_database_stats() -> dict:
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total startups
        cursor.execute('SELECT COUNT(*) FROM startups')
        total_startups = cursor.fetchone()[0]
        
        # Unique industries
        cursor.execute('SELECT DISTINCT industry_sector FROM startups WHERE industry_sector IS NOT NULL AND industry_sector != ""')
        industries = [row[0] for row in cursor.fetchall()]
        
        # Average founding year
        cursor.execute('SELECT AVG(founding_year) FROM startups WHERE founding_year IS NOT NULL')
        avg_founding_year = cursor.fetchone()[0]
        
        # Count of startups with disclosed funding
        cursor.execute('SELECT COUNT(*) FROM startups WHERE total_capital_raised IS NOT NULL AND total_capital_raised != "" AND total_capital_raised != "Not disclosed"')
        total_funding_disclosed = cursor.fetchone()[0]
        
        return {
            'total_startups': total_startups,
            'industries': industries,
            'avg_founding_year': avg_founding_year,
            'total_funding_disclosed': total_funding_disclosed
        }
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {
            'total_startups': 0,
            'industries': [],
            'avg_founding_year': None,
            'total_funding_disclosed': 0
        }
    finally:
        conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    create_startup_database()
    print("✅ Database initialized")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Startup Research API",
        "version": "1.0.0",
        "endpoints": {
            "save_from_file": "/save-from-file",
            "view_data": "/startups",
            "database_stats": "/stats",
            "query_analytics": "/query"
        }
    }

@app.post("/save-from-file")
async def save_from_file(filename: str = Query(default="research_results.json", description="Filename to parse and save")):
    """Save data to database from result file"""
    try:
        # Check if file exists
        if not os.path.exists(filename):
            # Try to find files with pattern
            if filename == "all":
                file_patterns = [
                    "research_results.json",
                    "research_results_backup_*.json",
                    "batch_results_*.json"
                ]

                all_files = []
                for pattern in file_patterns:
                    all_files.extend(glob.glob(pattern))

                if not all_files:
                    raise HTTPException(status_code=404, detail="No result files found")

                total_saved = 0
                processed_files = []

                for file in all_files:
                    startups = parse_result_file(file)
                    saved_count = 0

                    for startup in startups:
                        if isinstance(startup, dict):
                            company_name = (startup.get('Company Name') or
                                           startup.get('company_name') or
                                           startup.get('name', ''))
                            if company_name and save_startup_to_db(startup):
                                saved_count += 1

                    total_saved += saved_count
                    processed_files.append({
                        "filename": file,
                        "startups_saved": saved_count
                    })

                return {
                    "message": f"Successfully processed {len(all_files)} files",
                    "total_startups_saved": total_saved,
                    "files_processed": processed_files
                }
            else:
                raise HTTPException(status_code=404, detail=f"File {filename} not found")

        # Parse single file
        startups = parse_result_file(filename)

        if not startups:
            raise HTTPException(status_code=400, detail=f"No valid startup data found in {filename}")

        saved_count = 0
        for startup in startups:
            if isinstance(startup, dict):
                company_name = (startup.get('Company Name') or
                               startup.get('company_name') or
                               startup.get('name', ''))
                if company_name and save_startup_to_db(startup):
                    saved_count += 1

        return {
            "message": f"Successfully processed {filename}",
            "startups_found": len(startups),
            "startups_saved": saved_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/startups")
async def get_startups(
    limit: int = Query(default=100, description="Maximum number of startups to return"),
    industry: Optional[str] = Query(default=None, description="Filter by industry sector"),
    founding_year: Optional[int] = Query(default=None, description="Filter by founding year")
):
    """Get all startups from database with optional filtering"""
    try:
        startups = get_all_startups_from_db()

        # Apply filters
        if industry:
            startups = [s for s in startups if s.get('industry_sector', '').lower().find(industry.lower()) != -1]

        if founding_year:
            startups = [s for s in startups if s.get('founding_year') == founding_year]

        # Apply limit
        startups = startups[:limit]

        return {
            "total_returned": len(startups),
            "startups": startups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving startups: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = get_database_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@app.post("/query")
async def query_analytics(request: QueryRequest):
    """Query database using ChatGPT for analytics"""
    try:
        # Get current database stats and sample data
        stats = get_database_stats()
        startups = get_all_startups_from_db()

        # Prepare context for ChatGPT
        # Format average founding year safely
        avg_year_str = f"{stats['avg_founding_year']:.1f}" if stats['avg_founding_year'] else 'N/A'

        context = f"""
You are an AI assistant analyzing a startup research database. Here's the current database information:

Database Statistics:
- Total startups: {stats['total_startups']}
- Industries represented: {', '.join(stats['industries'][:10])}{'...' if len(stats['industries']) > 10 else ''}
- Average founding year: {avg_year_str}
- Startups with disclosed funding: {stats['total_funding_disclosed']}

Sample startup data (first 5 companies):
"""

        # Add sample data
        for i, startup in enumerate(startups[:5]):
            context += f"""
{i+1}. {startup['company_name']}
   - Industry: {startup['industry_sector']}
   - Founded: {startup['founding_year']}
   - Funding: {startup['total_capital_raised']}
   - Employees: {startup['employee_count']}
   - Business Model: {startup['business_model'][:100]}{'...' if len(str(startup['business_model'])) > 100 else ''}
"""

        context += f"""
Based on this startup database information, please answer the following question: {request.question}

Provide specific insights based on the data available. If you need more specific data to answer accurately, mention what additional information would be helpful.
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a startup research analyst providing insights based on database information."},
                {"role": "user", "content": context}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        answer = response.choices[0].message.content

        return {
            "question": request.question,
            "answer": answer,
            "database_stats": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/startups/{startup_id}")
async def get_startup_by_id(startup_id: int):
    """Get a specific startup by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                id, company_name, website_url, founding_year, founders,
                business_model, industry_sector, funding_rounds,
                total_capital_raised, current_revenue_estimates,
                employee_count, customer_user_base_size, key_partnerships,
                major_competitors, recent_news_developments, created_at
            FROM startups
            WHERE id = ?
        ''', (startup_id,))

        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Startup with ID {startup_id} not found")

        startup = {
            'id': row[0],
            'company_name': row[1],
            'website_url': row[2],
            'founding_year': row[3],
            'founders': json.loads(row[4]) if row[4] else [],
            'business_model': row[5],
            'industry_sector': row[6],
            'funding_rounds': json.loads(row[7]) if row[7] else [],
            'total_capital_raised': row[8],
            'current_revenue_estimates': row[9],
            'employee_count': row[10],
            'customer_user_base_size': row[11],
            'key_partnerships': json.loads(row[12]) if row[12] else [],
            'major_competitors': json.loads(row[13]) if row[13] else [],
            'recent_news_developments': row[14],
            'created_at': row[15]
        }

        return startup

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving startup: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
