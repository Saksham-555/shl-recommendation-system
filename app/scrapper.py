"""
SHL Assessment Catalog Web Scraper
Scrapes 377+ Individual Test Solutions from SHL's product catalog
"""

import json
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import time
import warnings
warnings.filterwarnings("ignore")


def scrape_shl_catalog():
    """
    Scrape all Individual Test Solutions from SHL catalog
    Returns: List of assessment dictionaries
    """
    BASE_URL = "https://www.shl.com"
    
    # All 32 pagination URLs (12 items per page)
    CATALOG_URLS = [
        "https://www.shl.com/solutions/products/product-catalog/",
        "https://www.shl.com/solutions/products/product-catalog/?start=12&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=24&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=36&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=48&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=60&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=72&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=84&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=96&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=108&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=120&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=132&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=144&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=156&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=168&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=180&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=192&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=204&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=216&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=228&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=240&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=252&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=264&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=276&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=288&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=300&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=312&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=324&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=336&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=348&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=360&type=1",
        "https://www.shl.com/solutions/products/product-catalog/?start=372&type=1"
    ]
    
    assessments = []
    
    print("🚀 Starting SHL Catalog Scraping")
    print("=" * 70)
    
    for tab_num, CATALOG_URL in enumerate(CATALOG_URLS, 1):
        try:
            print(f"\n📄 Fetching Page {tab_num}/32... ({CATALOG_URL})")
            catalog_response = requests.get(
                CATALOG_URL, 
                headers={'User-Agent': 'Mozilla/5.0'}, 
                timeout=15
            )
            catalog_response.raise_for_status()
            catalog_soup = BeautifulSoup(catalog_response.text, 'html.parser')
            
            # Find all assessment rows in table
            rows = catalog_soup.select("table tr")[1:]  # Skip header row
            print(f"   Found {len(rows)} assessments on this page")
            
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
                    print(f"   └─ Scraping ({i}/{len(rows)}): {link.get_text(strip=True)[:40]}...")
                    
                    assessment_response = requests.get(
                        assessment_url, 
                        headers={'User-Agent': 'Mozilla/5.0'}, 
                        timeout=10
                    )
                    assessment_soup = BeautifulSoup(assessment_response.text, 'html.parser')
                    
                    # Initialize assessment data
                    assessment_data = {
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "description": "Description unavailable",
                        "duration": "Duration not specified",
                        "languages": [],
                        "job_level": "Level not specified",
                        "remote_testing": "Not specified",
                        "adaptive_support": "Not specified",
                        "test_type": "Type not specified",
                        "source_page": tab_num
                    }
                    
                    # Extract description
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
                    
                    # Method 2: Find paragraphs with keywords
                    if not description:
                        keywords = ["assessment", "measure", "candidate", "skill", "test"]
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
                    
                    # Extract Test Type (look for pattern like "Test Type: K P B")
                    test_type_element = assessment_soup.find(string=lambda x: "test type:" in x.lower() if x else False)
                    if test_type_element:
                        parent = test_type_element.parent
                        test_type_text = parent.get_text(strip=True).replace("Test Type:", "").strip()
                        assessment_data["test_type"] = test_type_text
                    
                    # Remote testing indicator
                    remote_indicator = assessment_soup.find(string=lambda x: "remote testing" in x.lower() if x else False)
                    if remote_indicator:
                        parent = remote_indicator.parent
                        # Look for green/red indicator
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
                        "description": f"Error: {str(e)}",
                        "source_page": tab_num
                    })
            
            print(f"   ✅ Page {tab_num} complete ({len(assessments)} total so far)")
            time.sleep(2)  # Delay between pages
            
        except Exception as e:
            print(f"   ❌ Page {tab_num} failed: {str(e)}")
            continue
    
    # Save to JSON
    output_path = "data/shl_assessments_complete.json"
    with open(output_path, "w") as f:
        json.dump(assessments, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"🎉 SCRAPING COMPLETE!")
    print(f"   Total assessments scraped: {len(assessments)}")
    print(f"   Saved to: {output_path}")
    print("=" * 70)
    
    return assessments


if __name__ == "__main__":
    scrape_shl_catalog()