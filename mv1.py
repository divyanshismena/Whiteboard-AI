import pandas as pd
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Gemini
API_KEY = "AIzaSyCY2HHgNb3458mAgpiEYtrsDeGRTOccJUA"
llm = ChatGoogleGenerativeAI(
    google_api_key=API_KEY,
    model="gemini-2.0-flash-exp",
    temperature=0.1,
    max_output_tokens=1000
)

# Load the CSV file
file_path = 'mentors_data.csv'
df = pd.read_csv(file_path)

# Extract relevant columns
# df = df[['Name', 'Area of Interest', 'Experience', 'Languages']]

# Function to create a single prompt from the entire dataframe
def create_data_prompt(dataframe):
    """
    Creates a prompt string for the entire DataFrame.

    Args:
        dataframe (pd.DataFrame): The DataFrame to process.

    Returns:
        str: The generated prompt containing all rows from the DataFrame.
    """
    prompt = "Data:\n"
    for _, row in dataframe.iterrows():
        prompt += (
            f"Name: {row['Name']}, "
            f"Description with area of focus or expertise: {row['Description']}\n\n"
        )
    return prompt

# Main function to send data + query to Gemini
def process_data_and_query(dataframe, query):
    """
    Processes the entire dataset and sends the user query to Gemini.

    Args:
        dataframe (pd.DataFrame): The dataset to send.
        query (str): The user's query.

    Returns:
        str: The response from Gemini.
    """
    context = (
        "You are a mentors recommendation expert.\n"
        "Tell me all mentors from this data will help develop the set of skills in the next prompts.\n"
        "Tell me only the name of the top 3 mentor from the data who are best suited for the Skills mentioned at the end. It might not be exact skill but return a best suitable person who may mentor in the domain.\n"
        "Keep in mind:\n"
        "- Only use the mentors from the data.\n"
        "- Only give me the mentor name.\n"
        "- Do NOT use external knowledge. Only use the lines from 'Data:'\n"
        "- If no relevant mentors are found, respond exactly with 'None'.\n"
        "- No extra text or explanations.\n"
    )

    # Build the data prompt from the entire dataframe
    data_prompt = create_data_prompt(dataframe)

    # Combine context, data, and the user's query
    final_prompt = f"{context}\n{data_prompt}\nSkill Requirements: {query}"

    try:
        response = llm.invoke(final_prompt)
        return response.content
    except Exception as e:
        return f"Error during query: {e}"

if __name__ == "__main__":
    # Example query
    query = "Decision Making, Communication Skills"

    # Get the response from Gemini using the entire dataset
    response = process_data_and_query(df, query)
    mentor = [x.strip() for x in response.split('\n')]

    print(mentor)

    # print("\nResponse from Gemini:")
    # print(response)
