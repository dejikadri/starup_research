import os
import time
import json
import sqlite3
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI
from crewai_tools import ScrapeWebsiteTool
from crewai_tools import SerperDevTool
from dotenv import load_dotenv


load_dotenv()

print(os.environ["OPENAI_API_KEY"])
print(os.environ["SERPER_API_KEY"])

llm = OpenAI(
    temperature=0.1,
    model="gpt-3.5-turbo",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    max_tokens=4000,
    request_timeout=120,
)

# llm = LLM(
#     temperature=0.1,
#     model="gemini/gemini-1.5-pro-latest",
#     openai_api_key=os.environ["GEMINI_API_KEY"],
#     max_tokens=4000,
#     request_timeout=120,
# )

# Configure search tool with rate limiting
search_tool = SerperDevTool()

# Add rate limiting function
def rate_limited_search(query, delay=2):
    """Wrapper for search with rate limiting"""
    time.sleep(delay)
    return search_tool.run(query)

# Database functions
def create_startup_database():
    """Create SQLite database and table for startup data"""
    conn = sqlite3.connect('startup_research.db')
    cursor = conn.cursor()

    # Create table with schema matching the JSON structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            website_url TEXT,
            founding_year INTEGER,
            founders TEXT,  -- JSON string for array of founders
            business_model TEXT,
            industry_sector TEXT,
            funding_rounds TEXT,  -- JSON string for array of funding rounds
            total_capital_raised TEXT,
            current_revenue_estimates TEXT,
            employee_count INTEGER,
            customer_user_base_size TEXT,
            key_partnerships TEXT,  -- JSON string for array of partnerships
            major_competitors TEXT,  -- JSON string for array of competitors
            recent_news_developments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and table created successfully")

def save_startup_to_db(startup_data):
    """Save a single startup record to the database"""
    conn = sqlite3.connect('startup_research.db')
    cursor = conn.cursor()

    try:
        # Extract data from the startup_data dictionary
        company_name = startup_data.get('Company Name', '')
        website_url = startup_data.get('Website URL', '')
        founding_year = startup_data.get('Founding Year', None)
        founders = json.dumps(startup_data.get('Founders', []))
        business_model = startup_data.get('Business Model', '')
        industry_sector = startup_data.get('Industry Sector', '')
        funding_rounds = json.dumps(startup_data.get('Funding Rounds', []))
        total_capital_raised = startup_data.get('Total Capital Raised to Date', '')
        current_revenue_estimates = startup_data.get('Current Revenue Estimates', '')
        employee_count = startup_data.get('Employee Count', None)
        customer_user_base_size = startup_data.get('Customer/User Base Size', '')
        key_partnerships = json.dumps(startup_data.get('Key Partnerships', []))
        major_competitors = json.dumps(startup_data.get('Major Competitors', []))
        recent_news_developments = startup_data.get('Recent News or Developments', '')

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
        print(f"Saved startup: {company_name}")

    except Exception as e:
        print(f"Error saving startup to database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def save_all_startups_to_db(startups_list):
    """Save all startups from the research results to the database"""
    if not startups_list:
        print("No startup data to save")
        return

    create_startup_database()

    saved_count = 0
    for startup in startups_list:
        if isinstance(startup, dict):
            save_startup_to_db(startup)
            saved_count += 1
        else:
            print(f"Skipping invalid startup data: {type(startup)}")

    print(f"Successfully saved {saved_count} startups to database")

def parse_and_save_result_file(filename="research_results.json"):
    """Parse an existing result file and save to database"""
    try:
        print(f"Reading result file: {filename}")

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content:
            print(f"File {filename} is empty")
            return False

        # Try to parse as JSON
        try:
            data = json.loads(content)
            print("Successfully parsed JSON from file")
        except json.JSONDecodeError as e:
            print(f"File is not valid JSON: {e}")
            print("Attempting to extract JSON from text...")

            # Try to find JSON array in the text
            start_idx = content.find('[')
            end_idx = content.rfind(']')

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx+1]
                try:
                    data = json.loads(json_content)
                    print("Successfully extracted JSON array from text")
                except json.JSONDecodeError:
                    print("Could not extract valid JSON from text")
                    return False
            else:
                print("No JSON array found in text")
                return False

        # Validate and save data
        if isinstance(data, list):
            print(f"Found {len(data)} items in the data")

            # Check if items have the expected structure
            valid_items = []
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    # Check for required fields
                    if 'Company Name' in item or 'company_name' in item:
                        valid_items.append(item)
                    else:
                        print(f"Item {i+1} missing company name, skipping")
                else:
                    print(f"Item {i+1} is not a dictionary, skipping")

            if valid_items:
                print(f"Saving {len(valid_items)} valid startup records to database...")
                save_all_startups_to_db(valid_items)
                return True
            else:
                print("No valid startup records found")
                return False

        elif isinstance(data, dict):
            print("Found single startup record")
            if 'Company Name' in data or 'company_name' in data:
                save_all_startups_to_db([data])
                return True
            else:
                print("Single record missing company name")
                return False
        else:
            print(f"Unexpected data type: {type(data)}")
            return False

    except FileNotFoundError:
        print(f"File {filename} not found")
        return False
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        return False

def parse_all_result_files():
    """Parse and save all available result files to database"""
    import glob

    # Look for various result file patterns
    file_patterns = [
        "research_results.json",
        "research_results_backup_*.json",
        "batch_results_*.json"
    ]

    files_processed = 0

    for pattern in file_patterns:
        matching_files = glob.glob(pattern)
        for filename in matching_files:
            print(f"\n--- Processing {filename} ---")
            if parse_and_save_result_file(filename):
                files_processed += 1
                print(f"✅ Successfully processed {filename}")
            else:
                print(f"❌ Failed to process {filename}")

    print(f"\n=== Summary ===")
    print(f"Total files processed successfully: {files_processed}")

    # Show database stats
    conn = sqlite3.connect('startup_research.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM startups')
        total_count = cursor.fetchone()[0]
        print(f"Total startups now in database: {total_count}")
    except:
        print("Could not get database count")
    finally:
        conn.close()



startup_list= Agent(
    role = "Startup List Generator",
    goal = "generate a list of startups in the US and Canada that were started within the last 5 years",
    backstory=("You are an expert searcher with a specialization in searching for  startups. "
    ),
    llm = llm,
    verbose=True,
    )

startup_researcher = Agent(
    role = "Startup Researcher",
    goal = "find information about all the startups you received from the Startup List Generator. let the Startup Information Collator know when you have found all the information.",
    backstory=("You are an expert researcher with a specialization in researching information about startups. You are detail oriented and have a knack for finding the most relevant information."
    ),
    llm = llm,
    verbose=True,
    tools=[search_tool]
    )

startup_info_collator = Agent(
    role = "Startup Information Collator",
    goal = "collate all the information you received from the Startup Researcher about each starpup into a single item for each startup",
    backstory=("You are an expert writer with a specialization in writing information about startups. You are detail oriented and have a knack for finding the most relevant information."
    ),
    llm = llm,
    verbose=True,
    )

research_list_task = Task(
    description=(
        "Generate a list of exactly 10 startups in the US and Canada that were started within the last 5 years (2019-2024). "
        "Focus on well-known startups that have raised significant funding or gained notable traction. "
        "Include a mix of different industries (AI/ML, fintech, healthtech, e-commerce, etc.). "
        "For each startup, provide the company name clearly. "
        "Examples of the type of companies to include: companies that have raised Series A or later funding, "
        "have been featured in major tech publications, or have significant user bases. "
        "Make sure to return exactly 10 company names in a clear, numbered list format."
    ),
    expected_output="A numbered list of exactly 10 startup company names, one per line",
    agent=startup_list,
    )

research_startup_task = Task(
    description=(
        "Research EACH AND EVERY startup in the list provided by the previous task. "
        "You MUST research ALL 10 startups - do not stop until you have researched every single one. "
        "For each startup, include information that is relevant for basic analytics: "
        "- Company name and website URL "
        "- Founding year and founders "
        "- Business model and industry "
        "- Funding rounds and total capital raised "
        "- Current revenue (if available) "
        "- Employee count "
        "- Customer count or user base "
        "- Key partnerships and competitors "
        "Process the startups one by one and ensure you complete research for all 10 before finishing."
    ),
    expected_output="Complete research information for all 10 startups from the list, with detailed analytics data for each company",
    tools=[search_tool],
    agent=startup_researcher,
    context=[research_list_task]
    )

research_startup_collation_task = Task(
    description=(
        "Collate ALL information about EACH AND EVERY startup from the previous task. "
        "You MUST process all 10 startups - verify you have information for each one. "
        "Create a structured JSON array where each element contains complete information for one startup "
        "using EXACTLY this format for each startup: "
        "{\n"
        '  "Company Name": "Company Name Here",\n'
        '  "Website URL": "https://company-website.com",\n'
        '  "Founding Year": 2020,\n'
        '  "Founders": ["Founder Name 1", "Founder Name 2"],\n'
        '  "Business Model": "Description of business model",\n'
        '  "Industry Sector": "Industry name",\n'
        '  "Funding Rounds": [{"Amount": "$X million", "Date": "Month Year"}],\n'
        '  "Total Capital Raised to Date": "$X million",\n'
        '  "Current Revenue Estimates": "Revenue info or Not disclosed",\n'
        '  "Employee Count": 100,\n'
        '  "Customer/User Base Size": "User count or Not disclosed",\n'
        '  "Key Partnerships": ["Partner 1", "Partner 2"],\n'
        '  "Major Competitors": ["Competitor 1", "Competitor 2"],\n'
        '  "Recent News or Developments": "Recent developments"\n'
        "}\n"
        "Ensure the final output contains exactly 10 startup profiles in this exact JSON format."
    ),
    expected_output="A complete JSON array with exactly this structure for all 10 startups, with each startup following the exact field names and format specified",
    agent=startup_info_collator,
    context=[research_startup_task]
    )

research_startups_crew = Crew(
    agents=[startup_list, startup_researcher, startup_info_collator],
    tasks=[research_list_task, research_startup_task, research_startup_collation_task],
    process=Process.sequential,
    verbose=True,
    max_execution_time=3600,  # 1 hour timeout
)

try:
    print("Starting startup research process...")
    result = research_startups_crew.kickoff()

    print("Research completed successfully!")
    print(f"Result length: {len(str(result))}")
    print("First 500 characters of result:")
    print(str(result)[:500])

    # Parse the result and save to database
    parsed_result = None
    if isinstance(result, str):
        try:
            parsed_result = json.loads(result)
            print("Successfully parsed JSON result")
        except json.JSONDecodeError:
            print("Result is not valid JSON, saving as text")
    else:
        print("Result is not a string, converting to string")
        result = str(result)

    # Write result to file with better formatting
    with open("research_results.json", "w", encoding='utf-8') as f:
        if parsed_result:
            json.dump(parsed_result, f, indent=2, ensure_ascii=False)
        else:
            f.write(result)

    print("Results saved to research_results.json")

    # Save to SQLite database
    if parsed_result and isinstance(parsed_result, list):
        print(f"Saving {len(parsed_result)} startups to database...")
        save_all_startups_to_db(parsed_result)
    else:
        print("Could not save to database - result is not a valid JSON array")
        print("Please check the research_results.json file and manually parse if needed")

    # Also save a backup with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"research_results_backup_{timestamp}.json"
    with open(backup_filename, "w", encoding='utf-8') as f:
        if parsed_result:
            json.dump(parsed_result, f, indent=2, ensure_ascii=False)
        else:
            f.write(result)

    print(f"Backup saved to {backup_filename}")

except Exception as e:
    print(f"Error during research process: {str(e)}")
    print(f"Error type: {type(e).__name__}")

    # Save error information
    error_info = {
        "error": str(e),
        "error_type": type(e).__name__,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("research_error.json", "w") as f:
        json.dump(error_info, f, indent=2)

    print("Error information saved to research_error.json")

# Command line interface for parsing existing files
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "parse":
            if len(sys.argv) > 2:
                filename = sys.argv[2]
                print(f"Parsing specific file: {filename}")
                parse_and_save_result_file(filename)
            else:
                print("Parsing all available result files...")
                parse_all_result_files()

        elif command == "parse-all":
            print("Parsing all available result files...")
            parse_all_result_files()

        elif command == "help":
            print("Usage:")
            print("  python research_startups.py                    # Run normal research")
            print("  python research_startups.py parse              # Parse all result files")
            print("  python research_startups.py parse <filename>   # Parse specific file")
            print("  python research_startups.py parse-all          # Parse all result files")
            print("  python research_startups.py help               # Show this help")

        else:
            print(f"Unknown command: {command}")
            print("Use 'python research_startups.py help' for usage information")

    else:
        # Run normal research process
        pass  # The existing try-catch block will execute




