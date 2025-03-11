import requests
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# RSS Feed URL
RSS_FEED_URL = "https://dev.whiteboard.com.sa/feed/?post_type=lp_course"
# Main Courses Page URL (if RSS is blocked)
COURSES_PAGE_URL = "https://dev.whiteboard.com.sa/courses/"

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_from_rss():
    """Fetch course data from RSS feed"""
    response = requests.get(RSS_FEED_URL, headers=HEADERS)
    if response.status_code != 200:
        return None  # RSS feed failed
    
    root = ET.fromstring(response.content)
    courses = []
    
    for item in root.findall(".//item"):
        course = {
            "Title": item.find("title").text if item.find("title") is not None else "",
            "Link": item.find("link").text if item.find("link") is not None else "",
            "Instructor": item.find(".//dc:creator", namespaces={"dc": "http://purl.org/dc/elements/1.1/"}).text if item.find(".//dc:creator", namespaces={"dc": "http://purl.org/dc/elements/1.1/"}) is not None else "",
            "Publication Date": item.find("pubDate").text if item.find("pubDate") is not None else "",
            "Short Description": item.find("description").text if item.find("description") is not None else "",
            "Post ID": item.find(".//post-id", namespaces={"wp": "com-wordpress:feed-additions:1"}).text if item.find(".//post-id", namespaces={"wp": "com-wordpress:feed-additions:1"}) is not None else ""
        }
        courses.append(course)
    
    return courses


def fetch_from_webpage():
    """Scrape course data from the Whiteboard webpage if RSS fails"""
    response = requests.get(COURSES_PAGE_URL, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to retrieve data from the webpage.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    courses = []

    course_cards = soup.find_all("div", class_="course-card")  # Adjust class based on webpage structure

    for card in course_cards:
        title = card.find("h3", class_="course-title").text.strip() if card.find("h3", class_="course-title") else "N/A"
        link = card.find("a")["href"] if card.find("a") else "N/A"
        instructor = card.find("div", class_="instructor-name").text.strip() if card.find("div", class_="instructor-name") else "N/A"
        duration = card.find("span", class_="duration").text.strip() if card.find("span", class_="duration") else "N/A"
        category = card.find("span", class_="category").text.strip() if card.find("span", class_="category") else "N/A"
        price = card.find("span", class_="price").text.strip() if card.find("span", class_="price") else "N/A"

        courses.append({
            "Title": title,
            "Link": link,
            "Instructor": instructor,
            "Duration": duration,
            "Category": category,
            "Price": price
        })

    return courses


def get_detailed_info(course_url):
    """Scrape full course description & language from individual course pages"""
    try:
        response = requests.get(course_url, headers=HEADERS)
        if response.status_code != 200:
            return "Description not available", "Language not available"

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract full course description
        desc_div = soup.select_one("#learn-press-course-description > div")
        full_description = desc_div.get_text(strip=True) if desc_div else "No additional description"

        # Extract course language
        lang_div = soup.select_one("#sidebar div.elementor-element-b098034 div.elementor-element-7e6515a span.thim-ekit-single-course__meta__language")
        language = lang_div.get_text(strip=True) if lang_div else "Language not specified"

        return full_description, language
    
    except Exception as e:
        return f"Error fetching description: {str(e)}", "Error fetching language"


def scrapper_task():
    course_data = fetch_from_rss()
    if course_data is None:
        print("RSS failed, switching to web scraping...")
        course_data = fetch_from_webpage()

    for course in course_data:
        if course.get("Link") and course["Link"] != "N/A":
            print(f"Fetching details for: {course['Title']}")
            full_description, course_language = get_detailed_info(course["Link"])
            course["Full Description"] = f"{course.get('Short Description', '')} {full_description}"
            course["Language"] = course_language
        
        time.sleep(2)

    # Convert to DataFrame
    df = pd.DataFrame(course_data)

    # Save to CSV file
    csv_filename = "whiteboard_courses_with_full_description_and_language.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"Data successfully saved to {csv_filename}")

def update_variable_daily():
    """Function that runs continuously and updates a value at midnight."""
    while True:
        now = datetime.now()
        next_run = datetime(now.year, now.month, now.day) + timedelta(days=1)  # Next midnight
        sleep_time = (next_run - now).total_seconds()
        
        time.sleep(sleep_time)  # Sleep until midnight
        
        scrapper_task()
        
if __name__ == "__main__":
    print("Thread Running")
    update_variable_daily()
    # scrapper_task()