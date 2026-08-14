from phi.agent import Agent
from phi.model.groq import Groq
from ddgs import DDGS
from dotenv import load_dotenv
import os


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY not found.\n"
        "Please create a .env file and add:\n"
        "GROQ_API_KEY=your_groq_api_key"
    )

print("Groq API key loaded successfully.")


# ============================================================
# 2. CREATE GROQ MODEL
# ============================================================

def create_model():

    return Groq(
        id="llama-3.3-70b-versatile",
        api_key=groq_api_key
    )


# ============================================================
# 3. DUCKDUCKGO SEARCH FUNCTION
# ============================================================

def search_web(query, max_results=8):

    print(f"\nSearching web for: {query}")

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for result in search_results:

                results.append({
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "href": result.get("href", "")
                })

    except Exception as e:

        print("Search error:", e)

    return results


# ============================================================
# 4. FORMAT SEARCH RESULTS
# ============================================================

def format_results(results):

    if not results:

        return "No web search results were found."

    formatted_text = ""

    for i, result in enumerate(results, start=1):

        formatted_text += f"""
SOURCE {i}

Title:
{result["title"]}

URL:
{result["href"]}

Information:
{result["body"]}

----------------------------------------
"""

    return formatted_text


# ============================================================
# 5. LIVE MATCH AGENT
# ============================================================

match_agent = Agent(

    name="Live Match Agent",

    model=create_model(),

    instructions=[
        "You are a cricket live-score specialist.",
        "Analyze the web search results provided to you.",
        "Find the latest India vs Australia cricket match information.",
        "Report the teams, score, wickets, overs and match status.",
        "Use the most recent information available.",
        "If no current match is found, clearly say that.",
        "Never invent a cricket score.",
        "Use a markdown table.",
        "Keep the answer concise."
    ],

    markdown=True
)


# ============================================================
# 6. PLAYER STATS AGENT
# ============================================================

player_agent = Agent(

    name="Player Stats Agent",

    model=create_model(),

    instructions=[
        "You are a cricket statistics specialist.",
        "Analyze the web search results provided to you.",
        "Find recent statistics for Virat Kohli.",
        "Focus on his latest available matches.",
        "Include runs, highest score, average and strike rate when available.",
        "Use reliable information from the search results.",
        "Never invent statistics.",
        "Use a markdown table.",
        "Keep the answer concise."
    ],

    markdown=True
)


# ============================================================
# 7. CRICKET NEWS AGENT
# ============================================================

news_agent = Agent(

    name="Cricket News Agent",

    model=create_model(),

    instructions=[
        "You are a cricket news specialist.",
        "Analyze the web search results provided to you.",
        "Find the latest cricket news.",
        "Highlight important cricket headlines.",
        "Mention upcoming matches when available.",
        "Mention injuries and team updates when available.",
        "Mention tournament updates when available.",
        "Mention sources when possible.",
        "Never invent news.",
        "Use markdown formatting.",
        "Keep the answer concise."
    ],

    markdown=True
)


# ============================================================
# 8. LIVE MATCH SEARCH
# ============================================================

print("\n")
print("=" * 70)
print("LIVE MATCH INFORMATION")
print("=" * 70)

match_results = search_web(
    "India Australia cricket live score latest ESPNcricinfo Cricbuzz",
    max_results=8
)

match_data = format_results(match_results)


# ============================================================
# 9. SEND MATCH RESULTS TO MATCH AGENT
# ============================================================

match_response = match_agent.run(

    f"""
Analyze the following web search results.

Find the latest India vs Australia cricket match information.

SEARCH RESULTS:

{match_data}

Provide the result in a clear markdown table.
Do not invent any information.
"""
)

print("\n")
print(match_response.content)


# ============================================================
# 10. VIRAT KOHLI SEARCH
# ============================================================

print("\n")
print("=" * 70)
print("VIRAT KOHLI RECENT STATS")
print("=" * 70)

player_results = search_web(
    "Virat Kohli latest match score runs statistics ESPNcricinfo Cricbuzz",
    max_results=8
)

player_data = format_results(player_results)


# ============================================================
# 11. SEND PLAYER RESULTS TO PLAYER AGENT
# ============================================================

player_response = player_agent.run(

    f"""
Analyze the following web search results.

Find recent statistics for Virat Kohli.

SEARCH RESULTS:

{player_data}

Provide the statistics in a clear markdown table.
Do not invent any statistics.
"""
)

print("\n")
print(player_response.content)


# ============================================================
# 12. CRICKET NEWS SEARCH
# ============================================================

print("\n")
print("=" * 70)
print("LATEST CRICKET NEWS")
print("=" * 70)

news_results = search_web(
    "latest cricket news India Australia Virat Kohli ESPNcricinfo Cricbuzz ICC",
    max_results=8
)

news_data = format_results(news_results)


# ============================================================
# 13. SEND NEWS RESULTS TO NEWS AGENT
# ============================================================

news_response = news_agent.run(

    f"""
Analyze the following web search results.

Find the latest cricket news.

SEARCH RESULTS:

{news_data}

Summarize the most important cricket news.
Mention sources when possible.
Do not invent information.
"""
)

print("\n")
print(news_response.content)


# ============================================================
# 14. PROGRAM COMPLETED
# ============================================================

print("\n")
print("=" * 70)
print("CRICKET ANALYSIS COMPLETED")
print("=" * 70)