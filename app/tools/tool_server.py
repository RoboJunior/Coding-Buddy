import asyncio
import aiohttp
from fastmcp import FastMCP
from google import genai
from google.genai import types
import os
import base64
from dotenv import load_dotenv

load_dotenv()

GITHUB_BASE = "https://api.github.com"
REDDIT_BASE = "https://www.reddit.com"
BASE_URL = "https://api.stackexchange.com/2.3"

mcp = FastMCP("Coding-Buddy Tool Server")


@mcp.tool(
    name="error_tracer",
    title="Get the exact error root cause",
    description="Get all the information related to the occuring error",
)
async def error_extractor(image_path: str):
    system_prompt = """
    You are an advanced code-error analyzer. Your task is to carefully examine the provided code or image containing code and extract all relevant information about errors in a structured, comprehensive, and precise manner.
    Output Format (strictly):
        * Line No: Exact line number where the error occurs
        * Type of Error: Type or category of the error (e.g., SyntaxError, TypeError, NameError)
        * Error Message: Full error message as shown in logs or console
        * Error Context: Surrounding code or function/block where the error occurs (at least 2–3 lines before and after the error)
        * Traceback Info: Full traceback or call stack if available
        * Variables Involved: Any variables, functions, or objects mentioned in the error
        * Module/Function: The module, class, or function where the error occurs (if identifiable)
        * Error Severity: Indicate whether it is critical (stops execution) or warning-level
        * Environment Info: Any hints from the error about runtime environment, dependencies, or versions (if mentioned)
        * Additional Notes: Any extra hints visible in the error message that could clarify the issue

    Instructions:
        * Extract all available details about the error.
        * Only provide structured error information; do not provide solutions, fixes, or explanations.
        * Be as precise and thorough as possible, even for subtle or multi-line errors.
        * If multiple errors are present, extract each one separately with the same structured format
    
    User Query : {user_query}
    """
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=system_prompt.format(user_query="Traceback the error")
                )
            ],
        )
    ]
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(mime_type="image/png", data=encoded_string)
                ],
            )
        )
    client = genai.Client(
        api_key=os.environ.get('GOOGLE_API_KEY')
    )
    model = "gemini-2.5-flash"
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
    )
    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )
    return response.text


# Github issues tools
@mcp.tool(
    name="github_related_issues",
    title="Fetch similar github issues",
    description="Get all the relavent issues from github which are solved previously",
)
async def search_github_issues(query: str, limit: int = 5):
    async with aiohttp.ClientSession() as session:
        url = f"{GITHUB_BASE}/search/issues"
        params = {"q": query, "sort": "created", "order": "desc", "per_page": limit}
        async with session.get(url=url, params=params) as response:
            data = await response.json()
            return data


# Reddit issues tool
@mcp.tool(
    name="reddit_related_issues",
    title="Fetch similar reddit issues",
    description="Get all the relavent issues from reddit which are solved previously",
)
async def search_reddit_issues(
    query: str, subreddit: str = "programming", limit: int = 5
):
    async with aiohttp.ClientSession() as session:
        url = f"{REDDIT_BASE}/r/{subreddit}/search.json"
        params = {"q": query, "restrict_sr": 1, "sort": "new", "limit": limit}
        async with session.get(url=url, params=params) as response:
            r = await response.json()
            data = [d for d in r["data"]["children"]]
            return data


# Stackoverflow tools
@mcp.tool(
    name="search_by_error_stackoverflow",
    title="Search Stack Overflow by error message with all filters applied",
    description="Get all the relavent by error message from stackoverflow which are solved previously",
)
async def search_by_error(
    errorMessage: str,
    language: str = None,
    technologies: list[str] = None,
    minScore: int = None,
    includeComments: bool = False,
    responseFormat: str = "json",
    limit: int = 3,
):
    async with aiohttp.ClientSession() as session:
        params = {
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "intitle": errorMessage,
            "filter": "!9_bDDxJY5",  # default filter for questions
        }

        # Apply optional filters
        if language:
            params["tagged"] = language

        if technologies:
            # Join multiple technologies with a semicolon as required by Stack Overflow API
            params["tagged"] = (
                ";".join(technologies)
                if not language
                else f"{language};{';'.join(technologies)}"
            )

        if minScore is not None:
            params["min"] = minScore  # min votes score

        url = f"{BASE_URL}/search/advanced"
        async with session.get(url=url, params=params) as response:
            r = await response.json()

            items = r.get("items", [])[:limit]

            # Optionally include comments
            if includeComments and items:
                for item in items:
                    question_id = item.get("question_id")
                    if question_id:
                        comments_url = f"{BASE_URL}/questions/{question_id}/comments"
                        async with session.get(
                            comments_url,
                            params={
                                "order": "desc",
                                "sort": "creation",
                                "site": "stackoverflow",
                            },
                        ) as comments_resp:
                            comments_data = await comments_resp.json()
                            item["comments"] = comments_data.get("items", [])

            if responseFormat.lower() == "json":
                return items
            elif responseFormat.lower() == "text":
                return [f"{item['title']}: {item['link']}" for item in items]
            else:
                return items


@mcp.tool(
    name="analyze_stack_trace",
    title="Analyze a stack trace to search relevant questions on Stack Overflow.",
    description="Search relevant questions and understand how it got resolved",
)
async def analyze_stack_trace(
    stackTrace: str,
    language: str = None,
    technologies: list[str] = None,
    minScore: int = None,
    includeComments: bool = False,
    responseFormat: str = "json",
    limit: int = 3,
):
    first_line = stackTrace.splitlines()[0] if stackTrace else ""

    async with aiohttp.ClientSession() as session:
        params = {
            "order": "desc",
            "sort": "relevance",
            "site": "stackoverflow",
            "intitle": first_line,
            "filter": "!9_bDDxJY5",
        }

        # Optional filters
        if language:
            params["tagged"] = language

        if technologies:
            tags = ";".join(technologies)
            if "tagged" in params:
                params["tagged"] += f";{tags}"
            else:
                params["tagged"] = tags

        if minScore is not None:
            params["min"] = minScore

        url = f"{BASE_URL}/search/advanced"
        async with session.get(url=url, params=params) as response:
            r = await response.json()
            items = r.get("items", [])[:limit]

            # Include comments if requested
            if includeComments and items:
                for item in items:
                    question_id = item.get("question_id")
                    if question_id:
                        comments_url = f"{BASE_URL}/questions/{question_id}/comments"
                        async with session.get(
                            comments_url,
                            params={
                                "order": "desc",
                                "sort": "creation",
                                "site": "stackoverflow",
                            },
                        ) as comments_resp:
                            comments_data = await comments_resp.json()
                            item["comments"] = comments_data.get("items", [])

            if responseFormat.lower() == "json":
                return items
            elif responseFormat.lower() == "text":
                return [f"{item['title']}: {item['link']}" for item in items]
            else:
                return items


@mcp.tool(
    name="advanced_search",
    title="Rich search using filters like score, accepted answers, and comments.",
    description="Get all the information to get deeper understanding of the occuring issue",
)
async def advanced_search(
    keywords: str = None,
    tags: list[str] = None,
    min_score: int = None,
    has_accepted: bool = False,
    include_comments: bool = False,
    response_format: str = "json",
    limit: int = 5,
):
    url = f"{BASE_URL}/search/advanced"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "filter": "!9_bDDxJY5",
    }

    if keywords:
        params["q"] = keywords

    if tags:
        params["tagged"] = ";".join(tags)

    if min_score is not None:
        params["min"] = min_score

    if has_accepted:
        params["accepted"] = "True"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            r = await response.json()
            items = r.get("items", [])[:limit]

            if include_comments and items:
                for item in items:
                    question_id = item.get("question_id")
                    if question_id:
                        comments_url = f"{BASE_URL}/questions/{question_id}/comments"
                        async with session.get(
                            comments_url,
                            params={
                                "order": "desc",
                                "sort": "creation",
                                "site": "stackoverflow",
                            },
                        ) as comments_resp:
                            comments_data = await comments_resp.json()
                            item["comments"] = comments_data.get("items", [])

            if response_format.lower() == "json":
                return items
            elif response_format.lower() == "text":
                return [f"{item['title']}: {item['link']}" for item in items]
            else:
                return items


async def _get_agent_card_req(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{url}/.well-known/agent.json") as response:
            r = await response.json()
            return r


@mcp.tool(
    name="get_agent_cards",
    title="Get all agent cards",
    description="This tools is used to get all agent cards and agent skills",
)
async def get_agent_card():
    agent_urls = os.environ.get("AGENT_URLS").split(",")
    tasks = [_get_agent_card_req(url) for url in agent_urls]
    agent_cards = await asyncio.gather(*tasks)
    return agent_cards


@mcp.tool(
    name="call_agent",
    title="Call agent to complete the task",
    description="This tool is used to call the agent which can get the task done",
)
async def call_agent(agent_url: str, query: str, session_id: str, user_id: str):
    url = f"{agent_url}/run"
    payload = {"query": query, "session_id": session_id, "user_id": user_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=payload) as response:
            r = await response.json()
            return r


def start_mcp_server():
    mcp.run(transport="sse", host="0.0.0.0", port=8005)
