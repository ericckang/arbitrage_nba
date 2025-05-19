import json, base64
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def extract_nba_odds_from_image(image_path: str):
    # load and base64-encode the screenshot
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    # craft a markdown embed that GPT-4 Vision will see as an image
    prompt = (
        f"![bet365 screenshot]"
        f"(data:image/png;base64,{img_b64})\n\n"
        "This is a Bet365 NBA lines page. "
        "Please return a JSON array named “games”, where each item has:\n"
        "  • team1  – first team name\n"
        "  • team2  – second team name\n"
        "  • odds   – object mapping each team to its money-line value\n\n"
        "Example:\n"
        '{ "games": [ { "team1":"MIN Timberwolves", "team2":"OKC Thunder", '
        '"odds": { "MIN Timberwolves":"+245", "OKC Thunder":"-305" } }, … ] }'
    )

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini", 
        messages=[{"role":"user","content":prompt}]
    )

    # parse and return the JSON that the model spits out
    return json.loads(resp.choices[0].message.content)


if __name__ == "__main__":
    data = extract_nba_odds_from_image("Screenshot 2025-05-19 at 2.22.59 PM.png")
    print(json.dumps(data, indent=2))
