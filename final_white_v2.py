import streamlit as st
from anthropic import AnthropicVertex
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import threading
from question_prompts_1 import *
import streamlit.components.v1 as components
import re, json
from langchain_google_genai import ChatGoogleGenerativeAI
from test_gemini import split_data_into_chunks, process_all_data
import pandas as pd
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import base64
import mv1 as mv
import numpy as np



# Function to run the separate script
def run_background_script():
    subprocess.Popen(["python", "scraper.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(["python", "metors_scrapers.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if "thread_started" not in st.session_state:
    st.session_state.thread_started = True
    thread = threading.Thread(target=run_background_script, daemon=True)
    thread.start()

print(st.session_state['thread_started'], [thread.name for thread in threading.enumerate()])
# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="Whiteboard Assessment")

if "generate_pdf" not in st.session_state:
    st.session_state.generate_pdf = False

# Custom CSS for better styling
st.markdown("""
<style>
    .stRadio > label {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        transition: background-color 0.3s;
    }
    .stRadio > label:hover {
        background-color: #e8eaed;
    }
    .question-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .user-info-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 4px solid #0066cc;
    }
    .section-header {
        padding: 20px 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

SERVICE_ACCOUNT_FILE = 'secrets/whiteboard.json'

# llm, client, LOCATION = None, None, None

# if 'loading_llm' not in st.session_state:
API_KEY = "AIzaSyCY2HHgNb3458mAgpiEYtrsDeGRTOccJUA"  # Replace with your actual API key
llm = ChatGoogleGenerativeAI(
    google_api_key=API_KEY,
    model="gemini-2.0-flash-exp",
    temperature=0.1,
    max_output_tokens=300
)


def extract_claude_secrets():
    key_path = SERVICE_ACCOUNT_FILE
    credentials = Credentials.from_service_account_file(
        key_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform'])
    if credentials.expired:
        credentials.refresh(Request())
    return credentials

LOCATION="us-east5"
client = AnthropicVertex(region=LOCATION, project_id="prj-whiteboard-0125", credentials=extract_claude_secrets())
st.session_state['loading_llm'] = True


if "step" not in st.session_state:
    st.session_state.step = "form"

if st.session_state.step == "form":
    st.markdown("<h1 style='text-align: center;'>Welcome to Whiteboard's Assessment</h1>", unsafe_allow_html=True)
    
    # Create a centered column for the form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='section-header'><h3>Step 1: Fill in your details</h3></div>", unsafe_allow_html=True)
        with st.form("user_details_form", clear_on_submit=False):
            domain = st.text_input("Work Domain", placeholder="e.g., Finance, Technology")
            position = st.text_input("Position", placeholder="e.g., Analyst, Manager")
            experience = st.number_input("Years of Experience", min_value=0, step=1)
            gender = st.selectbox("Select your gender:", ["Male", "Female"])
            
            # Center the submit button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button("Begin Assessment")

            if submitted:
                st.session_state.domain = domain
                st.session_state.position = position
                st.session_state.experience = experience
                st.session_state.gender = gender
                with st.spinner("Generating your personalized assessment..."):
                    lock = threading.Lock()
                    outputs = [None] * 3
                    role_name = f"{st.session_state.position} position in {st.session_state.domain} domain with {st.session_state.experience} YOE"

                    def get_questions(prompt, ind):
                        message = client.messages.create(
                            max_tokens=8192,
                            messages=[{"role": "user", "content": prompt}],
                            model="claude-3-5-sonnet-v2@20241022",
                        )
                        with lock:
                            outputs[ind] = message.content[0].text

                    df = pd.read_excel("Whiteboard Q 4325.xlsx")
                    no_of_threads = int(np.ceil(len(df)/10))

                    ques_prompts = []

                    for i in range(no_of_threads):
                        question = ""
                        strt = i*10
                        end = min(len(df), (i+1)*10)
                        for j in range(strt, end):
                            question += df.iloc[j]['Question'] + "\n"
                            if not pd.isna(df.iloc[j]['Option 1']):
                                question += "* "+df.iloc[j]['Option 1'] + "\n"
                            if not pd.isna(df.iloc[j]['Option 2']):
                                question += "* "+df.iloc[j]['Option 2'] + "\n"
                            if not pd.isna(df.iloc[j]['Option 3']):
                                question += "* "+df.iloc[j]['Option 3'] + "\n"
                            if not pd.isna(df.iloc[j]['Option 4']):
                                question += "* "+df.iloc[j]['Option 4'] + "\n"
                            
                            question += "\n\n"
                        
                        ques_prompts.append(questionare(question, role_name))

                    threads = [
                        threading.Thread(target=get_questions, args=(prompt, i))
                        for i, prompt in enumerate(ques_prompts)
                    ]
                    
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()

                    final_questions = {}
                    try:
                        for response in outputs:
                            json_pattern = r'\{.*\}'
                            json_match = re.search(json_pattern, response, re.DOTALL)
                            if json_match:
                                data = json.loads(json_match.group(0))
                                questions_dict = {
                                    item['question']: item['options'] 
                                    for item in data['questions']
                                }
                                final_questions = {**final_questions, **questions_dict}

                            st.session_state['final_questions'] = final_questions
                        st.session_state.step = "questionnaire"
                        st.rerun()
                    except Exception as E:
                        print(E)
                        st.warning("Please reload and wait for 5 seconds before retrying.")
                    
                #     st.session_state['final_questions'] = final_questions
                # st.session_state.step = "questionnaire"
                # st.rerun()

elif st.session_state.step == "questionnaire":
    # st.markdown("<h1 style='text-align: center;'>LAB Assessment</h1>", unsafe_allow_html=True)

    # # User info card
    # st.markdown("""
    #     <div class='user-info-card'>
    #         <h4>Candidate Profile</h4>
    #         <p><strong>Domain:</strong> {domain}</p>
    #         <p><strong>Position:</strong> {position}</p>
    #         <p><strong>Experience:</strong> {experience} years</p>
    #     </div>
    # """.format(
    #     domain=st.session_state.domain,
    #     position=st.session_state.position,
    #     experience=st.session_state.experience
    # ), unsafe_allow_html=True)

    # st.markdown("<div class='section-header'><h3>Step 2: Complete the Assessment</h3></div>", unsafe_allow_html=True)

    # # Progress tracking
    # total_questions = len(st.session_state["final_questions"])
    # responses = {}
    
    # # Create tabs for question categories
    # questions_per_tab = 5
    # num_tabs = (total_questions + questions_per_tab - 1) // questions_per_tab
    # tabs = st.tabs([f"Section {i+1}" for i in range(num_tabs)])

    # for tab_idx, tab in enumerate(tabs):
    #     with tab:
    #         start_idx = tab_idx * questions_per_tab
    #         end_idx = min(start_idx + questions_per_tab, total_questions)
            
    #         questions_subset = list(st.session_state["final_questions"].items())[start_idx:end_idx]
            
    #         for idx, (question, options) in enumerate(questions_subset, 1):
    #             with st.container():
    #                 st.markdown(f"""
    #                     <div class='question-card'>
    #                         <p style='font-weight: bold; color: #0066cc;'>Question {start_idx + idx}</p>
    #                         <p style='font-size: 1.1em;'>{question}</p>
    #                     </div>
    #                 """, unsafe_allow_html=True)
    #                 response = st.radio("", options, key=question, horizontal=True)
    #                 responses[question] = response
    #             st.markdown("<br>", unsafe_allow_html=True)

    # # Center the submit button
    # col1, col2, col3 = st.columns([1, 1, 1])
    # with col2:
    #     if st.button("Submit Assessment", type="primary", use_container_width=True):
    #         with st.spinner("Generating your Report..."):
    
    st.markdown("<h1 style='text-align: center;'>Professional Personality & Conduct Assessment</h1>", unsafe_allow_html=True)

    # User info card
    st.markdown("""
        <div class='user-info-card' style='padding: 15px; border-radius: 10px; background: #f5f5f5;'>
            <h4>Candidate Profile</h4>
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>Position:</strong> {position}</p>
            <p><strong>Experience:</strong> {experience} years</p>
        </div>
    """.format(
        domain=st.session_state.domain,
        position=st.session_state.position,
        experience=st.session_state.experience
    ), unsafe_allow_html=True)

    st.markdown("<div class='section-header'><h3>Step 2: Complete the Assessment</h3></div>", unsafe_allow_html=True)

    # Initialize session state
    if "current_section" not in st.session_state:
        st.session_state.current_section = 0

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    # Progress tracking
    total_questions = len(st.session_state["final_questions"])
    questions_per_section = 5
    num_sections = (total_questions + questions_per_section - 1) // questions_per_section

    # Stylish section navigation
    # st.markdown("<h4 style='text-align: center; color: #0066cc;'>Select a Section</h4>", unsafe_allow_html=True)

    cols = st.columns(num_sections)
    for i in range(num_sections):
        button_style = "background-color: #0066cc; color: white; border-radius: 10px; padding: 8px 12px; width: 100%;" if i == st.session_state.current_section else "background-color: #ddd; color: black; border-radius: 10px; padding: 8px 12px; width: 100%;"
        if cols[i].button(f"Section {i+1}", key=f"section_{i}", help=f"Go to Section {i+1}", use_container_width=True):
            st.session_state.current_section = i
            st.rerun()
            st.components.v1.html(
                """
                <script>
                    window.scrollTo(0, 0);
                </script>
                """,
                height=0,
            )

    # Display questions for the selected section
    current_section = st.session_state.current_section
    start_idx = current_section * questions_per_section
    end_idx = min(start_idx + questions_per_section, total_questions)
    questions_subset = list(st.session_state["final_questions"].items())[start_idx:end_idx]

    for idx, (question, options) in enumerate(questions_subset, 1):
        with st.container():
            st.markdown(f"""
                <div class='question-card' style='border: 1px solid #ccc; padding: 10px; border-radius: 8px; background: #f9f9f9;'>
                    <p style='font-weight: bold; color: #0066cc;'>Question {start_idx + idx}</p>
                    <p style='font-size: 1.1em;'>{question}</p>
                </div>
            """, unsafe_allow_html=True)

            # Preserve responses in session state
            if question not in st.session_state.responses:
                st.session_state.responses[question] = None
            
            selected_option = st.radio("", options, key=f"q_{start_idx + idx}", 
                                    index=options.index(st.session_state.responses[question]) if st.session_state.responses[question] in options else 0, 
                                    horizontal=True)

            # Update session state response
            st.session_state.responses[question] = selected_option

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_section > 0 and st.button("⬅ Prev", type='secondary'):
            st.session_state.current_section -= 1
            st.rerun()
            st.components.v1.html(
                """
                <script>
                    window.scrollTo(0, 0);
                </script>
                """,
                height=0,
            )

    with col3:
        if current_section < num_sections - 1 and st.button("Next ➡", type='secondary'):
            st.session_state.current_section += 1
            st.rerun()
            st.components.v1.html(
                """
                <script>
                    window.scrollTo(0, 0);
                </script>
                """,
                height=0,
            )

    with col2:
        if current_section == num_sections - 1:
            if st.button("Submit Assessment", type="primary", use_container_width=True):
                with st.spinner("Generating your Report..."):
                    try:
                        all_resp = ""
                        for question, answer in st.session_state.responses.items():
                            # print(f"Q.=>{question}\nA.=>{answer}\n\n")
                            all_resp += f"\n\n Ques: {question} \n Ans: {answer}"

                        print(all_resp)
                        report_prompt = get_report_prompt(all_resp)
                        message = client.messages.create(
                            max_tokens=8192,
                            messages=[
                                {
                                "role": "user",
                                "content": report_prompt,
                                }
                            ],
                            model="claude-3-5-sonnet-v2@20241022",
                            )
                        
                        pattern = r'```(?:[a-zA-Z]*\n)?([^`]+?)```'
                        matches = re.finditer(pattern, message.content[0].text , re.MULTILINE | re.DOTALL)
                        code_blocks = [match.group(1).strip() for match in matches]

                        pattern = r'\"(?:[a-zA-Z]*\n)?([^`]+?)\"'
                        matches = re.finditer(pattern, message.content[0].text , re.MULTILINE | re.DOTALL)
                        improvements = [match.group(1).strip() for match in matches]

                        st.session_state["improvements"] = improvements[-1]
                        st.session_state["html_code"] = code_blocks[0]

                        # Generate course recommendations
                        st.session_state["skills"] = all_resp
                        # st.session_state["responses"] = responses

                        if 'full_report' not in st.session_state:
                        # Generate insights using Gemini
                            response_data = "\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state["responses"].items()])
                            
                            llm2 = ChatGoogleGenerativeAI(
                                google_api_key=API_KEY,
                                model="gemini-1.5-flash",
                                temperature=0.1,
                                max_output_tokens=8192
                            )
                            
                            # Generate insights
                            gemini_prompt = f"""
                            Based on the following assessment responses:
                            {response_data}
                            Generate 2 side by side columns of equal width, one talking about strengths and one talking about potential challenges,
                            each point in the table should be a small one liner, adjust the font such that each point fit in a single row, return the table as an html code snippet thats
                            nicely formatted with properly defined cells, rows and columns with proper line to segregate the columns. Do not exceed maximum limit of 7 rows.
                            """
                            gemini_response = llm2.invoke(gemini_prompt)
                            
                            # Generate workplace stressors
                            gemini_prompt2 = f"""
                            Take these responses and give a rating from 1 to 5 for all the workplace stressors listed below:
                            {response_data}

                            Having to work alone
                            Open discussions
                            Rigid enforcement of rules
                            Change in workplace expectations or job duties
                            A narrowly defined role
                            Having clear and well articulated goals
                            Being exposed to frequent conflict
                            Taking the lead in group settings

                            Include only the workplace stressor and a number. Return the response in a neat bullet point list format.
                            """
                            gemini_response2 = llm2.invoke(gemini_prompt2)
                            
                            # Process stressors for visualization
                            stressors = []
                            ratings = []
                            lines = gemini_response2.content.split('\n')
                            for line in lines:
                                line = line.strip().strip('- ').strip()
                                if ':' in line:
                                    parts = line.split(':')
                                    try:
                                        stressors.append(parts[0].strip())
                                        ratings.append(int(parts[1].strip()))
                                    except:
                                        continue

                            # Build combined HTML report
                            chart_html = """
                            <div class='stressors-section' style='margin: 40px 0;'>
                                <h2 style='color: #2c3e50; border-bottom: 2px solid #0066cc; padding-bottom: 10px;'>Workplace Stressors Analysis</h2>
                                <div style='max-width: 800px; margin: 0 auto;'>
                            """
                            
                            for stressor, rating in zip(stressors, ratings):
                                width = rating * 20  # 20% per point (1-5 scale)
                                chart_html += f"""
                                <div style='margin: 15px 0;'>
                                    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                                        <span><strong>{stressor.replace("* ", "")}</strong></span>
                                        <span>{rating}/5</span>
                                    </div>
                                    <div style='background: #f0f0f0; border-radius: 5px; height: 20px;'>
                                        <div style='background: #0066cc; width: {width}%; height: 100%; border-radius: 5px;'></div>
                                    </div>
                                </div>
                                """
                            
                            chart_html += "</div></div>"

                            # Use triple quotes for the HTML template and format it properly
                            full_report = (
                                "<html>"
                                "<head>"
                                "<style>"
                                ".report-container { padding: 30px; font-family: Arial, sans-serif; line-height: 1.6; }"
                                "h2 { color: #2c3e50; border-bottom: 2px solid #0066cc; padding-bottom: 10px; margin-top: 40px; }"
                                ".insights-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }"
                                ".stressors-section { margin-top: 30px; }"
                                "</style>"
                                "</head>"
                                "<body>"
                                "<div class='report-container'>"
                                f"{st.session_state['html_code']}"
                                "<div class='insights-section'>"
                                "<h2>Key Insights</h2>"
                                f"{gemini_response.content.replace('```', '').replace('html', '')}"  # Remove ``` from the response
                                "</div>"
                                f"{chart_html}"
                                "</div>"
                                "</body>"
                                "</html>"
                            )

                            st.session_state.full_report = full_report
                        else:
                            pass

                        st.session_state.step = "report"
                        st.rerun()
                        st.components.v1.html(
                            """
                            <script>
                                window.scrollTo(0, 0);
                            </script>
                            """,
                            height=0,
                        )
                    except Exception as E:
                            print(E)
                            st.warning("Please wait for 5 seconds before retrying.")

# ... [Keep all previous imports and setup code unchanged until the report section] ...

elif st.session_state.step == "report":
    st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )
    # st.markdown("<h1 style='text-align: center;'>Your LAB Assessment Report</h1>", unsafe_allow_html=True)
    
    components.html(st.session_state.full_report, height=1200, width=1000, scrolling=True)
    st.success("Thank you for completing the assessment!")

    # if st.button("Save as PDF"):
    #     st.session_state.generate_pdf = True

    # if st.session_state.get("generate_pdf", False):
    #     st.session_state.generate_pdf = False  # Reset the flag after running

        # Set up Selenium WebDriver
    if 'downloadable_pdf' not in st.session_state:
        with st.spinner("Preparing Your Downloadable Report..."):
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # Save the HTML file locally
            html_path = os.path.abspath("report.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.full_report)

            # Open the file in Chrome
            driver.get("file://" + html_path)
            time.sleep(5)  # Wait for the page to load

            pdf_path = os.path.abspath("report.pdf")

            # Use Chrome DevTools Protocol (CDP) to generate PDF
            pdf = driver.execute_cdp_cmd("Page.printToPDF", {
                "paperWidth": 9,  # Keep A4 width (in inches)
                "paperHeight": 35,   # Large height to accommodate full page (adjust as needed)
                "scale": 1.0,  # Shrinks the content to fit within one page
                "printBackground": True
            })
            with open("report.pdf", "wb") as f:
                f.write(base64.b64decode(pdf["data"]))

            driver.quit()
            st.session_state.downloadable_pdf = pdf_path
    else:
        pass

    # Allow user to download the PDF
    with open(st.session_state.downloadable_pdf, "rb") as pdf_file:
        st.download_button("Download PDF", pdf_file, "report.pdf", "application/pdf")

    def display_courses(df):
    # Apply custom CSS for button styling
        st.markdown("""
            <style>
            .course-button2 {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                cursor: pointer;
            }
            .course-button1 {
                background-color: #FFA500;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                cursor: pointer;
            }
            .course-name {
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)

        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                st.markdown(f'<span class="course-name">{row["Program"]}</span> (Score: {row["Score"]})', unsafe_allow_html=True)
                
            with col2:
                st.markdown(f'<a href="{row["Link"]}" target="_blank"><button class="course-button2">English Course</button></a>', 
                        unsafe_allow_html=True)

            if len(row['A_link']) != 0:
                with col3: 
                    st.markdown(f'<a href="{row["A_link"]}" target="_blank"><button class="course-button1">Arabic Course</button></a>', 
                            unsafe_allow_html=True)
                
            st.markdown("---")

    
    def display_mentors(df):
        # Apply custom CSS for button styling and alignment
        st.markdown("""
            <style>
            .course-button {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                cursor: pointer;
                display: block;
                margin: 0 auto;
            }
            .course-name {
                font-weight: bold;
                font-size: 20px; /* Increased font size */
                text-align: center; /* Center the text horizontally */
            }
            .column-container {
                display: flex;
                align-items: center; /* Center vertically */
                justify-content: center; /* Center horizontally */
                height: 100%; /* Ensure the container takes full height */
            }
            .stColumn > div {
                display: flex;
                align-items: center; /* Center vertically for all columns */
                height: 100%; /* Ensure the column takes full height */
            }
            </style>
        """, unsafe_allow_html=True)

        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                # Display the mentor's image
                st.image(row["Image Link"], width=150)  # Adjust the width as needed

            with col2:
                # Center the mentor's name vertically and horizontally
                st.markdown(
                    f'<div class="column-container"><span class="course-name">{row["Mentor"]}</span></div>', 
                    unsafe_allow_html=True
                )

            with col3:
                # Center the "Check out" button vertically and horizontally
                st.markdown(
                    f'<div class="column-container"><a href="{row["Profile Link"]}" target="_blank"><button class="course-button">Check out</button></a></div>', 
                    unsafe_allow_html=True
                )
                
            st.markdown("---")

    if "recom_data" not in st.session_state:
        
        df = pd.read_csv('whiteboard_courses_with_full_description_and_language.csv')
        st.markdown("<h1 style='text-align: center;'>Recommended Courses for You</h1>", unsafe_allow_html=True)
        with st.spinner("Loading..."):
            chunks = split_data_into_chunks(df, chunk_size=50)
            response = process_all_data(chunks, st.session_state["skills"], st.session_state.gender)
            # st.markdown("<h3 style='text-align: center;'>The following courses are recommended based on your input:</h3>", unsafe_allow_html=True)
            #st.write(response)
            print(response)

            data = []
            # Process input line by line
            lines = response.strip().split("\n")
            
            # if lines:
            #     st.markdown(f"**{lines[0]}**")  
            programs = []
            for i in range(len(lines)):
                lines[i] = lines[i].replace("*", "")  # Replace special characters
                match = re.match(r"(.+?) - Score: (\d+)", lines[i])
                
                if match:
                    program, score = match.groups()
                    if program in programs:
                        continue
                    else:
                        programs.append(program)
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
 
            # Convert to DataFrame and display
            # if data:
            #     df = pd.DataFrame(data)
            #     st.table(df)  
            # else:
            #     st.write(response)

            if data:
                df = pd.DataFrame(data)
                display_courses(df)
                st.session_state.recom_data = data
            else:
                st.write("++++++++++++++ISSUE OCCURED+++++++++\n", response)
    else:
        st.markdown("<h1 style='text-align: center;'>Recommended Courses for You</h1>", unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.recom_data)
            # print(df.head())
        display_courses(df)

    col1, col2 = st.columns([1, 4])

    with col1:
        st.markdown(f'<a href="https://dev.whiteboard.com.sa/courses/" target="_blank"><button class="course-button">Check out all courses</button></a>', 
                unsafe_allow_html=True)
        
    if st.session_state.experience >= 8:
        if 'mentor' not in st.session_state:
            _df = pd.read_csv('mentors_data.csv')
            st.markdown("<h1 style='text-align: center;'>Recommended Coaches for You</h1>", unsafe_allow_html=True)
            with st.spinner("Loading..."):
                response = mv.process_data_and_query(_df, st.session_state["skills"])
                data = []
                if 'None' not in response:
                    mentor = [x.strip() for x in response.split('\n')]
                    print(mentor)
                    
                    for name in mentor:
                        x = _df[(_df['Name']==name)]
                        data.append({"Mentor": name, "Profile Link": x.iloc[0]['Profile Link'], "Image Link": x.iloc[0]['Image Link']})
                else:
                    pass
                # Convert to DataFrame and display
                # if data:
                #     df = pd.DataFrame(data)
                #     st.table(df)  
                # else:
                #     st.write(response)

                if len(data)>0:
                    df = pd.DataFrame(data)
                    display_mentors(df)
                    st.session_state.mentor = data
                else:
                    st.session_state.mentor = data
        else:
            st.markdown("<h1 style='text-align: center;'>Recommended Mentors for You</h1>", unsafe_allow_html=True)
            if len(st.session_state.mentor)>0:
                df = pd.DataFrame(st.session_state.mentor)
                    # print(df.head())
                display_mentors(df)

        col1, col2 = st.columns([1, 4])

        with col1:
            st.markdown(f'<a href="https://dev.whiteboard.com.sa/coaching/" target="_blank"><button class="course-button">Check out all coaches</button></a>', 
                    unsafe_allow_html=True)
        
    
    # if st.button("Restart"):
    #     st.session_state.step = "form"
    #     st.rerun()