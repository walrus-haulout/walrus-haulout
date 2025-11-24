import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = "https://www.deepsurge.xyz/api/projects"
HACKATHON_ID = "26f4d734-b30f-4009-9b41-edac04308c01"

def fetch_all_projects(page_limit=50, progress_callback=None):
    """
    Fetches all projects from the DeepSurge API.
    
    Args:
        page_limit (int): Maximum number of pages to fetch.
        progress_callback (callable): Optional function to call with progress updates (current_page, total_items).
        
    Returns:
        list: A list of project dictionaries.
    """
    all_projects = []
    seen_ids = set()
    next_cursor = None
    page = 0
    
    # Setup headers with User-Agent and optional Cookie
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    cookie = os.getenv("DEEPSURGE_COOKIE")
    if cookie:
        headers["Cookie"] = cookie

    while page < page_limit:
        try:
            params = {
                "hackathonId": HACKATHON_ID,
                "limit": 20,  # Use smaller page size for stability
            }
            if next_cursor:
                params["after"] = next_cursor  # API expects 'after' parameter, not 'cursor'
            
            # Add delay between requests to avoid rate limiting
            if page > 0:
                time.sleep(1)
            
            print(f"Requesting page {page + 1} with params: {params}")
            response = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.text[:500]}") # Print first 500 chars
            response.raise_for_status()
            data = response.json()
            
            # Based on debug output: {"success":true,"data":{"items":[...]}}
            response_data = data.get("data", {})
            items = response_data.get("items", [])
            
            # Filter out duplicates
            new_items = []
            for item in items:
                item_id = item.get("id")
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    new_items.append(item)
            
            if not new_items:
                print("Stopping: No new items found (all duplicates).")
                break
                
            all_projects.extend(new_items)
            
            page += 1
            if progress_callback:
                progress_callback(page, len(all_projects))
            
            # Extract pagination info from the correct location
            pagination = response_data.get("pagination", {})
            next_cursor = pagination.get("nextCursor")
            has_next = pagination.get("hasNext")
            print(f"Page {page}: New Items={len(new_items)}, Total={len(all_projects)}, NextCursor={next_cursor[:50] if next_cursor else None}, HasNext={has_next}")
            
            if not has_next:
                print("Stopping: hasNext is False.")
                break
            
            if not next_cursor:
                print("Stopping: No nextCursor found.")
                break
            
            # Rate limiting sleep
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching page {page + 1}: {e}"
            print(error_msg)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            
            # Simple retry logic
            time.sleep(3)
            try:
                response = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                response_data = data.get("data", {})
                items = response_data.get("items", [])
                all_projects.extend(items)
                next_cursor = response_data.get("nextCursor")
                if not response_data.get("hasNext") or not next_cursor:
                    break
            except Exception as retry_e:
                print(f"Retry failed for page {page + 1}: {retry_e}")
                if hasattr(retry_e, 'response') and retry_e.response is not None:
                    print(f"Retry Response content: {retry_e.response.text}")
                raise retry_e # Raise the exception to be caught by the UI


    return all_projects

def clean_html(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def check_github_accessible(github_url):
    """
    Check if a GitHub URL is publicly accessible.
    Returns True if accessible (200-399), False otherwise.
    """
    if not github_url:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        # Use GET instead of HEAD - more reliable for GitHub
        response = requests.get(github_url, headers=headers, timeout=8, allow_redirects=True)
        # Consider 2xx and 3xx as accessible (GitHub may redirect)
        return 200 <= response.status_code < 400
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False

def process_projects(projects_data):
    """
    Process raw project data into a clean DataFrame.
    """
    processed_list = []
    
    for p in projects_data:
        # Extract links by type
        links = p.get("links", [])
        github_url = next((l.get("url") for l in links if l.get("type") == "github"), None)
        website_url = next((l.get("url") for l in links if l.get("type") == "website"), None)
        youtube_url = next((l.get("url") for l in links if l.get("type") == "youtube"), None)
        
        # Keep all original fields and add extracted link fields
        processed_obj = {
            "id": p.get("id"),
            "hackathonId": p.get("hackathonId"),
            "createdBy": p.get("createdBy"),
            "projectName": p.get("projectName"),
            "description": p.get("description"),  # Keep original HTML
            "projectLogoUrl": p.get("projectLogoUrl"),
            "track": p.get("track"),
            "bounties": p.get("bounties"),
            "mediaFileUrls": p.get("mediaFileUrls", []),
            "github_url": github_url,
            "website_url": website_url,
            "youtube_url": youtube_url,
            "packageId": p.get("packageId"),
            "deployNetwork": p.get("deployNetwork"),
            "status": p.get("status"),
            "listOnProjectPage": p.get("listOnProjectPage"),
            "likeCount": p.get("likeCount", 0),
            "reportCount": p.get("reportCount", 0),
            "createdAt": p.get("createdAt"),
            "updatedAt": p.get("updatedAt"),
            "isReported": p.get("isReported", False),
        }
        processed_list.append(processed_obj)
    
    df = pd.DataFrame(processed_list)
    return df
