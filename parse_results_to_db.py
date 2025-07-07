#!/usr/bin/env python3
"""
Standalone script to parse research result files and save them to SQLite database.
This script can handle various JSON formats and extract startup data.
"""

import os
import json
import sqlite3
import glob
from datetime import datetime

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
    print("✅ Database and table created/verified successfully")

def save_startup_to_db(startup_data):
    """Save a single startup record to the database"""
    conn = sqlite3.connect('startup_research.db')
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
        print(f"✅ Saved startup: {company_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving startup to database: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def parse_result_file(filename):
    """Parse a single result file and return startup data"""
    try:
        print(f"📖 Reading file: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"⚠️  File {filename} is empty")
            return []
        
        # Try to parse as JSON
        try:
            data = json.loads(content)
            print("✅ Successfully parsed JSON from file")
        except json.JSONDecodeError as e:
            print(f"⚠️  File is not valid JSON: {e}")
            print("🔍 Attempting to extract JSON from text...")
            
            # Try to find JSON array in the text
            start_idx = content.find('[')
            end_idx = content.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx+1]
                try:
                    data = json.loads(json_content)
                    print("✅ Successfully extracted JSON array from text")
                except json.JSONDecodeError:
                    print("❌ Could not extract valid JSON from text")
                    return []
            else:
                print("❌ No JSON array found in text")
                return []
        
        # Process the data
        if isinstance(data, list):
            print(f"📊 Found {len(data)} items in the data")
            return data
        elif isinstance(data, dict):
            print("📊 Found single startup record")
            return [data]
        else:
            print(f"⚠️  Unexpected data type: {type(data)}")
            return []
            
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return []
    except Exception as e:
        print(f"❌ Error processing file {filename}: {str(e)}")
        return []

def save_startups_to_db(startups_list):
    """Save a list of startups to the database"""
    if not startups_list:
        print("⚠️  No startup data to save")
        return 0
    
    create_startup_database()
    
    saved_count = 0
    for i, startup in enumerate(startups_list, 1):
        if isinstance(startup, dict):
            # Check for required fields
            company_name = (startup.get('Company Name') or 
                           startup.get('company_name') or 
                           startup.get('name', ''))
            
            if company_name:
                if save_startup_to_db(startup):
                    saved_count += 1
            else:
                print(f"⚠️  Item {i} missing company name, skipping")
        else:
            print(f"⚠️  Item {i} is not a dictionary, skipping")
    
    print(f"🎉 Successfully saved {saved_count} startups to database")
    return saved_count

def main():
    """Main function with command line interface"""
    import sys
    
    print("🚀 Startup Research Results Parser")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        
        if filename == "all":
            # Process all result files
            print("🔍 Looking for all result files...")
            
            file_patterns = [
                "research_results.json",
                "research_results_backup_*.json",
                "batch_results_*.json"
            ]
            
            all_files = []
            for pattern in file_patterns:
                all_files.extend(glob.glob(pattern))
            
            if not all_files:
                print("❌ No result files found")
                return
            
            print(f"📁 Found {len(all_files)} result files")
            
            total_saved = 0
            for file in all_files:
                print(f"\n--- Processing {file} ---")
                startups = parse_result_file(file)
                saved = save_startups_to_db(startups)
                total_saved += saved
            
            print(f"\n🎉 Total startups saved across all files: {total_saved}")
            
        else:
            # Process specific file
            startups = parse_result_file(filename)
            save_startups_to_db(startups)
    
    else:
        # Interactive mode
        print("Available options:")
        print("1. Parse specific file")
        print("2. Parse all result files")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            filename = input("Enter filename: ").strip()
            startups = parse_result_file(filename)
            save_startups_to_db(startups)
        elif choice == "2":
            # Process all files
            file_patterns = [
                "research_results.json",
                "research_results_backup_*.json", 
                "batch_results_*.json"
            ]
            
            all_files = []
            for pattern in file_patterns:
                all_files.extend(glob.glob(pattern))
            
            if not all_files:
                print("❌ No result files found")
                return
            
            print(f"📁 Found {len(all_files)} result files")
            
            total_saved = 0
            for file in all_files:
                print(f"\n--- Processing {file} ---")
                startups = parse_result_file(file)
                saved = save_startups_to_db(startups)
                total_saved += saved
            
            print(f"\n🎉 Total startups saved across all files: {total_saved}")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
