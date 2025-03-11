import asyncio
import re
import json
from fastapi import FastAPI, Query
from question_prompts_1 import *
from anthropic import AnthropicVertex
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
import mv1 as mv
from test_gemini import split_data_into_chunks, process_all_data
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import subprocess
import threading
import schedule
import time
from datetime import datetime
import numpy as np

SERVICE_ACCOUNT_FILE = 'app_secrets/whiteboard.json'

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

def run_background_script():
    subprocess.Popen(["python", "scraper.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(["python", "metors_scrapers.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_scheduler():
    schedule.every().day.at("00:00").do(run_background_script)  # Schedule for 12:00 AM
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every 60 seconds

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

app = FastAPI()

# Simulated async function for getting questions
async def get_questions(prompt, ind, outputs):
    message = await asyncio.to_thread(client.messages.create, 
                                      max_tokens=8192,
                                      messages=[{"role": "user", "content": prompt}],
                                      model="claude-3-5-sonnet-v2@20241022")

    outputs[ind] = message.content[0].text  # Store response in order

def get_report_data(prompt):
    message = client.messages.create(
                max_tokens=8192,
                messages=[
                    {
                    "role": "user",
                    "content": prompt,
                    }
                ],
                model="claude-3-5-sonnet-v2@20241022",
                )
    match = re.search(r'\{.*\}', message.content[0].text, re.DOTALL)
    # match = re.search(r'\{.*\}', final_response.content, re.DOTALL)
    if match:
        clean_json_string = match.group(0)  # Extract matched JSON
        data = json.loads(clean_json_string)
    
    return data

@app.get("/generate_questions")
async def generate_questions(work_domain: str = Query(...),
    position: str = Query(...),
    yoe: int = Query(...),
    gender: str = Query(...)):

    role_name = f"{position} position in {work_domain} domain with {yoe} YOE"

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

    outputs = [None] * len(ques_prompts)  # Maintain order of responses
    tasks = [asyncio.create_task(get_questions(prompt, i, outputs)) for i, prompt in enumerate(ques_prompts)]

    await asyncio.gather(*tasks)  # Wait for all tasks to finish

    # Process responses
    final_questions = {}
    for response in outputs:
        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            questions_dict = {item['question']: item['options'] for item in data['questions']}
            final_questions.update(questions_dict)

    return {"questions": final_questions}

@app.post("/get_report")
async def get_report(response_data: dict):
    """
    Generates a structured report based on question-answer pairs.
    """

    all_resp = ""

    for question in response_data.keys():
        # print(f"Q.=>{question}\nA.=>{answer}\n\n")
        all_resp += f"\n\n Ques: {question} \n Ans: {response_data[question]}"

    report = get_report_data(report_data_prompt(all_resp))

    return report

class CourseRequest(BaseModel):
    topics: List[str]
    gender: str

@app.post("/recommend_courses")
async def recommend_courses(request: CourseRequest):

    df = pd.read_csv('whiteboard_courses_with_full_description_and_language.csv')
    chunks = split_data_into_chunks(df, chunk_size=50) 
    response = process_all_data(chunks, request.topics, request.gender)

    print(response)

    data = []
    lines = response.strip().split("\n")
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

    return {"recommended_courses": data}

@app.post("/recommend_mentors")
async def recommend_mentor(request: CourseRequest):
    _df = pd.read_csv('mentors_data.csv')
    response = mv.process_data_and_query(_df, request.topics)
    data = []
    if 'None' not in response:
        mentor = [x.strip() for x in response.split('\n')]
        print(mentor)
        
        for name in mentor:
            x = _df[(_df['Name']==name)]
            data.append({"Mentor": name, "Profile Link": x.iloc[0]['Profile Link'], "Image Link": x.iloc[0]['Image Link']})

    return {"recommended_mentors": data}