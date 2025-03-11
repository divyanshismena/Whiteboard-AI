from bs4 import BeautifulSoup
import requests
import pandas as pd

# URL of the RSS feed
url = "https://dev.whiteboard.com.sa/feed/?post_type=coach"

# Headers to bypass security blocks
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# Request the RSS feed
response = requests.get(url, headers=headers)

# Parse the XML using BeautifulSoup
soup = BeautifulSoup(response.text, "xml")

# Extract instructor details
instructors = []
for item in soup.find_all("item"):
    name = item.find("title").text
    link = item.find("link").text

    # Extracting description from both <description> and <content:encoded>
    description_tag = item.find("description")
    content_tag = item.find("content:encoded")

    description = ""
    if description_tag:
        description += BeautifulSoup(description_tag.text, "html.parser").get_text(separator=" ").strip()
    if content_tag:
        description += " " + BeautifulSoup(content_tag.text, "html.parser").get_text(separator=" ").strip()

    # Extracting Image URL from <description>
    image_url = "No Image"
    if description_tag:
        desc_soup = BeautifulSoup(description_tag.text, "html.parser")
        img_tag = desc_soup.find("img")
        if img_tag and "src" in img_tag.attrs:
            image_url = img_tag["src"]

    # Append instructor details to the list
    instructors.append({
        "Name": name,
        "Profile Link": link,
        "Image Link": image_url,
        "Description": description.strip()
    })

# Convert to DataFrame and save to CSV
df = pd.DataFrame(instructors)
df.to_csv('mentors_data.csv', index=False)

# Print success message
print("Data successfully saved to mentors_data.csv ✅")