def questionare(questions, role_name):
    prompt = f"""You are helpful Language and Behavior Profile Test generator.
                
    Rephrase ALL questions and their options in this questionnaire to fit the position of "{role_name}",
    make the questions specific for the role without changing the meaning,
    rephrase the options of any question in such a way that they don't seem similar,
    Return ALL questions and options in json format.

    {questions}
    """

    return prompt

def questionare_1(role_name):
    prompt1 = f"""You are helpful Language and Behavior Profile Test generator.
                
    Rephrase ALL questions and their options in this questionnaire to fit the position of "{role_name}",
    make the questions specific for the role without changing the meaning,
    rephrase the options of any question in such a way that they don't seem similar,
    Return ALL questions and options in json format.

    What motivates you most when pursuing a goal?
    •⁠  ⁠I focus on avoiding unwanted outcomes.
    •⁠  ⁠I focus on what I want to achieve

    How do you know you’ve done a good job?*
    •⁠  ⁠I look at the results for validation.
    •⁠  ⁠I just know.
    •⁠  ⁠I seek feedback from others.
    •⁠  ⁠I reflect on both internal and external feedback.

    When you receive a new task, how do you respond?
    •⁠  ⁠I take immediate action.
    •⁠  ⁠I think it over before acting.

    When considering the impact of decisions, what do you focus on?
    •⁠  ⁠I focus on how it affects me.
    •⁠  ⁠I focus on how it affects others.
    •⁠  ⁠I balance between both.

    How do you prefer to approach tasks?
    •⁠  ⁠I focus on the big picture first.
    •⁠  ⁠I start with small details.
    •⁠  ⁠I consider both equally.
    How do you make decisions?
    •⁠  ⁠I prefer to have options.
    •⁠  ⁠I follow a set procedure or plan.

    How do you approach problem-solving?
    •⁠  ⁠I look for similarities.
    •⁠  ⁠I look for differences.
    •⁠  ⁠I try to balance both.

    When you're learning something new or engaging in a task, what helps you understand it best?
    •⁠  ⁠I prefer to see how it’s done.
    •⁠  ⁠I think through it logically or step-by-step.
    •⁠  ⁠I learn by physically doing it myself.
    •⁠  ⁠I like hearing explanations or instructions.

    How do you know when something is true or when you're convinced of something?
    •⁠  ⁠I need to see the evidence or results.
    •⁠  ⁠I need to think it through logically and analyse the facts.
    •⁠  ⁠I have to feel it or experience it for myself.
    •⁠  ⁠I need to hear it from others or hear convincing arguments.

    When making decisions, where do you focus your attention?
    •⁠  ⁠I stay focused on what's happening now.
    •⁠  ⁠I reflect on past experiences.
    •⁠  ⁠I think about future possibilities and consequences.
    """

    return prompt1

def questionare_2(role_name):

    prompt2 = f"""You are helpful Language and Behavior Profile Test generator.
                
    Rephrase ALL questions and their options in this questionnaire to fit the position of "{role_name}",
    make the questions specific for the role without changing the meaning,
    rephrase the options of any question in such a way that they don't seem similar,
    Return ALL questions and options in json format.

    How do you approach a new project?
    •⁠  ⁠I focus on what must be done.
    •⁠  ⁠I focus on what’s possible.

    How do you prefer to receive information?
    •⁠  ⁠I prefer small chunks of information.
    •⁠  ⁠I prefer large chunks.
    •⁠  ⁠A mix of both depending on the situation.

    Who do you believe controls the outcome of your life?
    •⁠  ⁠I am in control of my results.
    •⁠  ⁠External factors determine my success.
    •⁠  ⁠It’s a mix of both.

    When faced with a problem, how do you usually react?
    •⁠  ⁠I tackle it head-on and fix it quickly.
    •⁠  ⁠I prefer to wait, gather more information, and then decide.

    How do you prefer to communicate with others?
    •⁠  ⁠I prefer subtle, nuanced conversation.
    •⁠  ⁠I like direct, clear communication. 

    How quickly do you make decisions?
    •⁠  ⁠I make decisions quickly.
    •⁠  ⁠I prefer to take my time.

    How often does someone have to prove their competence to you before you're convinced?
    •⁠  ⁠They need to demonstrate competence a specific number of times.
    •⁠  ⁠I need to see it over a period of time.
    •⁠  ⁠I need them to show consistency over time.
    •⁠  ⁠I'm convinced immediately after one demonstration.

    How do you feel about managing yourself and others?
    •⁠  ⁠I understand what I need to do but find it difficult to tell others.
    •⁠  ⁠I find it easier to manage others than myself.
    •⁠  ⁠I know what I need but not necessarily what others need.
    •⁠  ⁠I understand both what I need and what others need to do to be successful.

    What makes you happiest in a work environment?
    •⁠  ⁠I like to be in a management or leadership role.
    •⁠  ⁠I enjoy being part of a team.
    •⁠  ⁠I prefer to work independently.

    What type of work brings you the most satisfaction?
    •⁠  ⁠Working with systems or processes.
    •⁠  ⁠Working with things.
    •⁠  ⁠Working with people.

    """

    return prompt2


def questionare_3(role_name):

    prompt3 = f"""
    You are helpful Language and Behavior Profile Test generator.
                
    Rephrase ALL questions and their options in this questionnaire to fit the position of "{role_name}",
    make the questions specific for the role without changing the meaning,
    rephrase the options of any question in such a way that they don't seem similar,
    Return ALL questions and options in json format.

    What excites you most about your favourite restaurant or activity?
    •⁠  ⁠The food or things involved.
    •⁠  ⁠The information or details.
    •⁠  ⁠The place itself.
    •⁠  ⁠The activities or experiences.
    •⁠  ⁠The people I’m with.

    How do you react in stressful situations?
    •⁠  ⁠I react based on my emotions.
    •⁠  ⁠I make a choice based on the situation.
    •⁠  ⁠I tend to think through it logically.

    How do you perceive the past and the future?
    •⁠  ⁠I see the past and future all around me, focused on the present.
    •⁠  ⁠I see the past behind me and the future ahead of me.

    When you are given information, how do you like to understand it?
    •⁠  ⁠I prefer a big-picture view.
    •⁠  ⁠I prefer starting with details and working up to the big picture.
    •⁠  ⁠I prefer starting with the big picture and then zooming into details.
    •⁠  ⁠I prefer a focus on the small details.

    If someone you knew said, "I'm thirsty," how would you respond?
    •⁠  ⁠I'd probably just find the comment interesting, but do nothing.
    •⁠  ⁠I’d feel compelled to act and get them something to drink.

    How do you prefer to communicate when you feel someone is not performing well?
    •⁠  ⁠I’d hint at it or imply what needs to be done.
    •⁠  ⁠I'd tell them directly.

    What do you tend to notice about situations and people?
    •⁠  ⁠I focus on how things are different.
    •⁠  ⁠I balance between noticing both similarities and differences.
    •⁠  ⁠I focus on how things are similar.

    """

    return prompt3

def get_report_prompt(all_resp):
    prompt = f"""Generate a personalized report with cool charts, plots and insights on strengths and weaknesses based on the following questions and answers:

    {all_resp}
    
First Task:
Generate a cool dashboard with html, css, js that can be rendered on a webpage. It should be proper and center aligned. 
There should be a spider plot, the spider plot should contain the following: 

Achievement
Motivation
Conscientiousness
Assertiveness
Extroversion
Cooperativeness
Competitiveness
Patience
self-confidence
Openness


followed by two vertical bar charts placed on top of each other.
Make SURE that the scale starts from 0 for both graphs for strength and weakness for different properties.
Make the graph descriptive enough so that people can understand it easily. Label the x and y axis with the appropriate name.
At last there should be list of improvements with one liner description that can be done in the report.
Code should ALWAYS be enclosed within ``` like "``` code .... ```". 

Second Task:
Additionally provide the list of improvements as a python list at the end seperately within "" like "['improvement area 1', 'improvement area 2' ...]".

"""
    return prompt

def report_data_prompt(answer):
    prompt = """Based on the question and their answers, populate the required fields in the given output format.
Return only the output JSON.

Output Format:
{
    "spider_plot": {
        
        "theta": [
            "Achievement",
            "Motivation",
            "Conscientiousness",
            "Assertiveness",
            "Extroversion",
            "Cooperativeness",
            "Competitiveness",
            "Patience",
            "Self-confidence",
            "Openness"
        ],

        "r": [
            <generate scores out of 10 based on the question and answers for each of the corresponding property in theta>
        ]
    },

    "strength_chart": {
        "labels": [
            <generate top 5 strengths based on the question and answers>
        ],
        "data": [
            <generate scores out of 10 based on the question and answers for each of the corresponding strengths>
        ]
    },

    "weakness_chart": {
        "labels": [
            <generate top 5 weaknesses based on the question and answers>
        ],
        "data": [
            <generate scores out of 10 based on the question and answers for each of the corresponding weaknesses>
        ]
    },

    "improvements": [
        <provide top 5 areas of improvements>
    ],

    "key_insights": {"strength": <give top 5 strengths (one short & simple line for each) based on the question and answers within a list>
        "weakness": <give top 5 weaknesses (one short & simple line for each) based on the question and answers within a list>
    },

    "workplace_stressors": [
        {
            "stressor": "Having to work alone",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "Open discussions",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "Rigid enforcement of rules",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "Change in workplace expectations or job duties",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "A narrowly defined role",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "Having clear and well articulated goals",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "Being exposed to frequent conflict",
            "score": <get score out of 5 for the above stressor based on question and answers>
        },
        {
            "stressor": "Taking the lead in group settings",
            "score": <get score out of 5 for the above stressor based on question and answers>
        }
    ]
}

Question/Answers are as follows:

""" + answer
    
    return prompt