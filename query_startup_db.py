import sqlite3
import json
from datetime import datetime

def connect_to_db():
    """Connect to the startup research database"""
    try:
        conn = sqlite3.connect('startup_research.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_all_startups():
    """Retrieve all startups from the database"""
    conn = connect_to_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
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
                'Company Name': row[1],
                'Website URL': row[2],
                'Founding Year': row[3],
                'Founders': json.loads(row[4]) if row[4] else [],
                'Business Model': row[5],
                'Industry Sector': row[6],
                'Funding Rounds': json.loads(row[7]) if row[7] else [],
                'Total Capital Raised to Date': row[8],
                'Current Revenue Estimates': row[9],
                'Employee Count': row[10],
                'Customer/User Base Size': row[11],
                'Key Partnerships': json.loads(row[12]) if row[12] else [],
                'Major Competitors': json.loads(row[13]) if row[13] else [],
                'Recent News or Developments': row[14],
                'created_at': row[15]
            }
            startups.append(startup)
        
        return startups
        
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")
        return []
    finally:
        conn.close()

def get_startup_count():
    """Get the total number of startups in the database"""
    conn = connect_to_db()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM startups')
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Error counting startups: {e}")
        return 0
    finally:
        conn.close()

def search_startups_by_industry(industry):
    """Search for startups by industry sector"""
    conn = connect_to_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT company_name, industry_sector, total_capital_raised 
            FROM startups 
            WHERE industry_sector LIKE ?
            ORDER BY company_name
        ''', (f'%{industry}%',))
        
        rows = cursor.fetchall()
        return rows
        
    except sqlite3.Error as e:
        print(f"Error searching by industry: {e}")
        return []
    finally:
        conn.close()

def display_startup_summary():
    """Display a summary of all startups in the database"""
    print("=== Startup Research Database Summary ===")
    
    count = get_startup_count()
    print(f"Total startups in database: {count}")
    
    if count == 0:
        print("No startups found in database.")
        return
    
    startups = get_all_startups()
    
    print(f"\nStartups found:")
    print("-" * 80)
    
    for i, startup in enumerate(startups, 1):
        print(f"{i}. {startup['Company Name']}")
        print(f"   Industry: {startup['Industry Sector']}")
        print(f"   Founded: {startup['Founding Year']}")
        print(f"   Funding: {startup['Total Capital Raised to Date']}")
        print(f"   Website: {startup['Website URL']}")
        print(f"   Added to DB: {startup['created_at']}")
        print()

def export_to_json():
    """Export all startup data to a JSON file"""
    startups = get_all_startups()
    
    if not startups:
        print("No startups to export")
        return
    
    # Remove database-specific fields for clean export
    clean_startups = []
    for startup in startups:
        clean_startup = {k: v for k, v in startup.items() if k not in ['id', 'created_at']}
        clean_startups.append(clean_startup)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"startup_export_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(clean_startups, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(clean_startups)} startups to {filename}")

def main():
    """Main function to demonstrate database queries"""
    print("Startup Research Database Query Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Display startup summary")
        print("2. Export to JSON")
        print("3. Search by industry")
        print("4. Show database stats")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            display_startup_summary()
        elif choice == '2':
            export_to_json()
        elif choice == '3':
            industry = input("Enter industry to search for: ").strip()
            results = search_startups_by_industry(industry)
            if results:
                print(f"\nStartups in '{industry}' industry:")
                for company, sector, funding in results:
                    print(f"- {company} ({sector}) - {funding}")
            else:
                print(f"No startups found in '{industry}' industry")
        elif choice == '4':
            count = get_startup_count()
            print(f"\nDatabase contains {count} startups")
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
