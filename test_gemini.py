import pandas as pd
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from secrets.gemini import API_KEY

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    google_api_key=API_KEY,
    model="gemini-2.0-flash-exp",
    temperature=0.1,
    max_output_tokens=1000
)

# Load the Excel file
file_path = 'whiteboard_courses_with_full_description_and_language.csv'
df = pd.read_csv(file_path)

# Extract relevant columns
df = df[['Title', 'Full Description', 'Publication Date','Link', 'Language']]
df['Publication Date'] = pd.to_datetime(df['Publication Date'], errors='coerce')

# Function to split the data into 50-row chunks
def split_data_into_chunks(dataframe, chunk_size=50):
    """
    Splits a DataFrame into smaller chunks with a fixed number of rows.

    Args:
        dataframe (pd.DataFrame): The DataFrame to split.
        chunk_size (int): Number of rows per chunk. Default is 50.

    Returns:
        list of pd.DataFrame: A list of DataFrame chunks.
    """
    return [dataframe.iloc[i:i + chunk_size] for i in range(0, len(dataframe), chunk_size)]

# Function to create a prompt for a chunk
def create_chunk_prompt(chunk):
    """
    Creates a prompt string for a chunk of data.

    Args:
        chunk (pd.DataFrame): A DataFrame chunk.

    Returns:
        str: The generated prompt for the chunk.
    """
    chunk_prompt = "Data:\n"
    for _, row in chunk.iterrows():
        chunk_prompt += f"Title: {row['Title']}, Description: {row['Full Description']}, Schedule: {row['Publication Date']}, Link: {row['Link']}\n, language: {row['Language']}\n"
    return chunk_prompt

# Function to process chunks and send them iteratively to Gemini
def process_all_data(chunks, query, gender):
    """
    Processes all data chunks iteratively to ensure Gemini considers all data.

    Args:
        chunks (list of pd.DataFrame): List of DataFrame chunks.
        query (str): User's query.

    Returns:
        str: The final response from Gemini.
    """
    context = "You are a course recommendation expert.\n"
    context += """
Tell me which courses from this data will help develop the set of skills in the next prompts.
and tell me only the name of the courses from the data and give a score of how important this course is for these skills.
Keep in mind:
- Do NOT use external knowledge. Only use the lines from 'Data:'\n"
- If a course title indicates it is for a specific gender (e.g., it includes 'women', 'female', 'men', or 'male'), only recommend that course if the query matches that same gender. Otherwise, exclude any other courses based on gender only if the title has gender.
- Prefer courses in both arabic and english on top of only english courses.
- Only use the courses from the data.
- Only give me the EXACT course name.
- Only give me the top 5 best courses to improve the areas of weaknesses mentioned and their score out of 10.
- Only return the course with score greater than eight in descendong order of their scores.
- Do not repeat the same courses.

Sample Output: 
<Exact Course Name> - Score: 9
<Exact Course Name> - Score: 8
.
.

"""

    # Feed each chunk iteratively
    for chunk in chunks:
        chunk_prompt = create_chunk_prompt(chunk)
        try:
            context += f"\n{chunk_prompt}"
            llm.invoke(context)  # Update Gemini's memory/context with the chunk
        except Exception as e:
            return f"Error processing chunk: {e}"

    # Final query after feeding all chunks
    final_query = f"{context}\n\nWeaknesses: {query}\n\n Gender: {gender}"
    try:
        final_response = llm.invoke(final_query)
        return final_response.content
        # return final_response.content if final_response and final_response.content else "No response from Gemini."
    except Exception as e:
        return f"Error during final query: {e}"

import re
def extract_course_data(response):
    data = []
    courses = re.split(r'\n\s*----\s*\n', response.strip())  # Split courses by '----'
    
    for course in courses:
        lines = course.strip().split("\n")
        course_info = {}
        
        for line in lines:
            line = line.strip().strip("\"")  # Remove extra quotes if present
            
            if not line:
                continue
            
            if not re.match(r"'.+':", line):  # Course Name (doesn't start with a key)
                course_info["Program"] = line.strip()
            elif "Link English" in line:
                course_info["Link English"] = line.split(": ", 1)[1].strip()
            elif "Link Arabic" in line:
                course_info["Link Arabic"] = line.split(": ", 1)[1].strip()
            elif "Score" in line:
                course_info["Score"] = int(line.split(": ", 1)[1].strip())
        
        data.append(course_info)
    
    return data

if __name__ == "__main__":
    # Example query
    query = """
Develop more flexible decision-making approaches
Build stronger team collaboration skills
Enhance emotional intelligence in leadership
Balance analytical and intuitive thinking
Improve project management capabilities
"""
    # Split data into 50-row chunks
    chunks = split_data_into_chunks(df, chunk_size=50)

    # Get response from Gemini
    response = process_all_data(chunks, query, 'female')

    print("\nResponse from Gemini:")
    print(response)

    data = []
            # Process input line by line
    lines = response.strip().split("\n")
    
    # if lines:
    #     st.markdown(f"**{lines[0]}**")  

    for i in range(len(lines)):
        lines[i] = lines[i].replace("*", "")  # Replace special characters
        match = re.match(r"(.+?) - Score: (\d+)", lines[i])
        if match:
            program, score = match.groups()
            x = df[(df['Title'] == program) & (df['Language'] == "Language:Arabic")]
            if len(x) > 0:
                a_link = x.iloc[0]['Link']
            else:
                a_link = ""

            x = df[(df['Title'] == program) & (df['Language'] == "Language:English")]
            if len(x) > 0:
                link = x.iloc[0]['Link']
            else:
                link = ""

            data.append({"Program": program, "Score": int(score), "Link": link, "A_link": a_link})
    # print(extract_course_data(response))
    print(data)
