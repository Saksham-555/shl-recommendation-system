"""
SHL Assessment Catalog Web Scraper
Scrapes ONLY Individual Test Solutions (377+) from SHL's product catalog
EXCLUDES Pre-packaged Job Solutions
"""

import json
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import time
import warnings
import os
warnings.filterwarnings("ignore")


def scrape_shl_catalog():
    """
    Scrape ONLY Individual Test Solutions from SHL catalog
    Returns: List of assessment dictionaries
    """
    BASE_URL = "https://www.shl.com"
    
    # Pagination URLs - these load both categories, we'll filter programmatically
    CATALOG_URLS = [
        "https://www.shl.com/solutions/products/product-catalog/",
        "https://www.shl.com/solutions/products/product-catalog/?start=12",
        "https://www.shl.com/solutions/products/product-catalog/?start=24",
        "https://www.shl.com/solutions/products/product-catalog/?start=36",
        "https://www.shl.com/solutions/products/product-catalog/?start=48",
        "https://www.shl.com/solutions/products/product-catalog/?start=60",
        "https://www.shl.com/solutions/products/product-catalog/?start=72",
        "https://www.shl.com/solutions/products/product-catalog/?start=84",
        "https://www.shl.com/solutions/products/product-catalog/?start=96",
        "https://www.shl.com/solutions/products/product-catalog/?start=108",
        "https://www.shl.com/solutions/products/product-catalog/?start=120",
        "https://www.shl.com/solutions/products/product-catalog/?start=132",
        "https://www.shl.com/solutions/products/product-catalog/?start=144",
        "https://www.shl.com/solutions/products/product-catalog/?start=156",
        "https://www.shl.com/solutions/products/product-catalog/?start=168",
        "https://www.shl.com/solutions/products/product-catalog/?start=180",
        "https://www.shl.com/solutions/products/product-catalog/?start=192",
        "https://www.shl.com/solutions/products/product-catalog/?start=204",
        "https://www.shl.com/solutions/products/product-catalog/?start=216",
        "https://www.shl.com/solutions/products/product-catalog/?start=228",
        "https://www.shl.com/solutions/products/product-catalog/?start=240",
        "https://www.shl.com/solutions/products/product-catalog/?start=252",
        "https://www.shl.com/solutions/products/product-catalog/?start=264",
        "https://www.shl.com/solutions/products/product-catalog/?start=276",
        "https://www.shl.com/solutions/products/product-catalog/?start=288",
        "https://www.shl.com/solutions/products/product-catalog/?start=300",
        "https://www.shl.com/solutions/products/product-catalog/?start=312",
        "https://www.shl.com/solutions/products/product-catalog/?start=324",
        "https://www.shl.com/solutions/products/product-catalog/?start=336",
        "https://www.shl.com/solutions/products/product-catalog/?start=348",
        "https://www.shl.com/solutions/products/product-catalog/?start=360",
        "https://www.shl.com/solutions/products/product-catalog/?start=372"
    ]
    
    assessments = []
    
    print("🚀 Starting SHL Catalog Scraping")
    print("=" * 70)
    print("⚠️  FILTERING: Individual Test Solutions ONLY")
    print("❌ EXCLUDING: Pre-packaged Job Solutions")
    print("=" * 70)
    
    for page_num, CATALOG_URL in enumerate(CATALOG_URLS, 1):
        try:
            print(f"\n📄 Fetching Page {page_num}/32... ({CATALOG_URL})")
            catalog_response = requests.get(
                CATALOG_URL, 
                headers={'User-Agent': 'Mozilla/5.0'}, 
                timeout=15
            )
            catalog_response.raise_for_status()
            catalog_soup = BeautifulSoup(catalog_response.text, 'html.parser')
            
            # Find ALL tables on the page
            tables = catalog_soup.find_all("table")
            
            if len(tables) < 2:
                print(f"   ⚠️  Expected 2 tables (Pre-packaged + Individual), found {len(tables)}")
            
            # The SECOND table contains "Individual Test Solutions"
            # First table is "Pre-packaged Job Solutions" - we skip it
            individual_table = tables[1] if len(tables) >= 2 else tables[0]
            
            rows = individual_table.select("tr")[1:]  # Skip header row
            print(f"   Found {len(rows)} Individual Test Solutions on this page")
            
            for i, row in enumerate(rows, 1):
                cols = row.select("td")
                if not cols:
                    continue
                    
                link = cols[0].find("a")
                if not link:
                    continue
                
                # Get assessment URL
                assessment_url = urljoin(BASE_URL, link["href"].strip())
                
                # Clean duplicate path in URL
                if "solutions/products/product-catalog/solutions/products" in assessment_url:
                    assessment_url = assessment_url.replace(
                        "solutions/products/product-catalog/solutions/products",
                        "solutions/products"
                    )
                
                # Fetch individual assessment page
                try:
                    assessment_name = link.get_text(strip=True)
                    print(f"   └─ Scraping ({i}/{len(rows)}): {assessment_name[:50]}...")
                    
                    assessment_response = requests.get(
                        assessment_url, 
                        headers={'User-Agent': 'Mozilla/5.0'}, 
                        timeout=10
                    )
                    assessment_soup = BeautifulSoup(assessment_response.text, 'html.parser')
                    
                    # Initialize assessment data
                    assessment_data = {
                        "name": assessment_name,
                        "url": assessment_url,
                        "category": "Individual Test Solutions",
                        "description": "Description unavailable",
                        "duration": "Duration not specified",
                        "languages": [],
                        "job_level": "Level not specified",
                        "remote_testing": "Not specified",
                        "adaptive_support": "Not specified",
                        "test_type": "Type not specified",
                        "source_page": page_num
                    }
                    
                    # Extract description (multiple fallback methods)
                    description = ""
                    
                    # Method 1: Find description heading
                    description_heading = assessment_soup.find(
                        lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4'] 
                        and 'description' in tag.text.lower()
                    )
                    if description_heading:
                        next_element = description_heading.find_next('p')
                        if next_element:
                            description = next_element.get_text(" ", strip=True)
                    
                    # Method 2: Find main content paragraphs
                    if not description:
                        keywords = ["assessment", "measure", "candidate", "skill", "test", "evaluates"]
                        paragraphs = assessment_soup.find_all("p")
                        for p in paragraphs:
                            text = p.get_text(" ", strip=True)
                            if any(kw in text.lower() for kw in keywords) and len(text) > 50:
                                description = text
                                break
                    
                    if description:
                        assessment_data["description"] = description
                    
                    # Extract metadata from specifications section
                    spec_sections = assessment_soup.find_all('div', class_='specification')
                    
                    for spec in spec_sections:
                        spec_text = spec.get_text(" ", strip=True).lower()
                        
                        # Duration
                        if 'duration' in spec_text or 'assessment length' in spec_text:
                            duration_match = spec.find(string=lambda x: 'minutes' in x.lower() if x else False)
                            if duration_match:
                                assessment_data["duration"] = duration_match.strip()
                        
                        # Languages
                        if 'language' in spec_text:
                            lang_text = spec.get_text(strip=True)
                            if ',' in lang_text:
                                assessment_data["languages"] = [l.strip() for l in lang_text.split(',')]
                        
                        # Job Level
                        if 'job level' in spec_text:
                            assessment_data["job_level"] = spec.get_text(strip=True)
                    
                    # Extract Test Type
                    test_type_element = assessment_soup.find(string=lambda x: "test type:" in x.lower() if x else False)
                    if test_type_element:
                        parent = test_type_element.parent
                        test_type_text = parent.get_text(strip=True).replace("Test Type:", "").strip()
                        assessment_data["test_type"] = test_type_text
                    
                    # Remote testing indicator
                    remote_indicator = assessment_soup.find(string=lambda x: "remote testing" in x.lower() if x else False)
                    if remote_indicator:
                        parent = remote_indicator.parent
                        if parent.find(class_='green') or 'yes' in parent.get_text().lower():
                            assessment_data["remote_testing"] = "Yes"
                        else:
                            assessment_data["remote_testing"] = "No"
                    
                    assessments.append(assessment_data)
                    time.sleep(1.5)  # Rate limiting
                
                except Exception as e:
                    print(f"      ⚠️  Failed to scrape details: {str(e)}")
                    assessments.append({
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "category": "Individual Test Solutions",
                        "description": f"Error: {str(e)}",
                        "source_page": page_num
                    })
            
            print(f"   ✅ Page {page_num} complete ({len(assessments)} Individual Tests so far)")
            time.sleep(2)  # Delay between pages
            
        except Exception as e:
            print(f"   ❌ Page {page_num} failed: {str(e)}")
            continue
    
    # # Create data directory if it doesn't exist
    # os.makedirs("data", exist_ok=True)
    
    # # Save to JSON
    # output_path = "data/shl_individual_assessments.json"
    # with open(output_path, "w", encoding='utf-8') as f:
    #     json.dump(assessments, f, indent=2, ensure_ascii=False)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to JSON
    output_path = os.path.join(data_dir, "shl_individual_assessments.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)    
    
    print("\n" + "=" * 70)
    print(f"🎉 SCRAPING COMPLETE!")
    print(f"   Total Individual Test Solutions scraped: {len(assessments)}")
    print(f"   Expected: 377+ assessments")
    print(f"   Status: {'✅ SUCCESS' if len(assessments) >= 377 else '⚠️  INCOMPLETE'}")
    print(f"   Saved to: {output_path}")
    print("=" * 70)
    
    return assessments


if __name__ == "__main__":
    scrape_shl_catalog()
