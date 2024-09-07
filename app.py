import os
from fasthtml.common import *
from fasthtml.components import Zero_md
from dotenv import load_dotenv
from openai import OpenAI

app = FastHTML()
load_dotenv()

base_url = "https://api.crosshatch.app/v1"
api_key = os.environ.get("CROSSHATCH_API_KEY")
model = "lmsys-overall"
recommendations = {}

openai_client = OpenAI(base_url=base_url,api_key=api_key)

sp = f"""
    You are a helpful and concise assistant.
    Your task is to recommend an appropriate age based on a children's book title.
    Also provide reasons for why you gave that recommendation.

    Respond in well formatted html. Only respond with html without any backticks.

    Start with <h3> tag with the book title.
    Then the recommended age.
    Then the reasons in a list.
"""

def BookTitleInput():
    return Card(
        Input(name="title", id="new-title", placeholder="Enter a book title",
        cls="input input-bordered w-full", hx_swap_oob='true'),
    )

@app.get("/")
def home():
    add = Form(BookTitleInput(), hx_post="/", target_id='age-recommendation', hx_swap="afterbegin")
    clear_button = Button("Clear", hx_post="/clear", hx_target="#age-recommendation", hx_swap="innerHTML")
    age_recommendation = Div(id='age-recommendation')
    return Title("Children's Book Age Recommender"), Main(H1("What's a good age for this book?"), add, age_recommendation, clear_button, cls='container')


@app.post("/")
def age(title:str):
    if title.lower() in recommendations:
        return recommendations.get(title)

    r = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sp},
                {"role": "user", "content": title}
            ]
    )
    content = r.choices[0].message.content
    content.strip('`')
    if content.startswith('html'):
        content = content[4:].strip()
    print(content)

    # add to cache
    recommendations[title] = content
    return r.choices[0].message.content

@app.post("/clear")
def clear():
    return ""
