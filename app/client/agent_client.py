#!/usr/bin/env python3

import asyncio
from datetime import datetime
import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import os
from dotenv import load_dotenv
import mss

load_dotenv()

console = Console()

ROLE_STYLES = {
    "You": "bold white on blue",
    "Agent": "bold white on green",
    "Tool Calling": "bold white on red",
    "Session": "bold white on magenta",
    "Tool Response": "bold black on cyan",
}

INDENT_ROLES = set()
USER_ID = os.environ.get("USER_ID")


def time_now():
    return datetime.now().strftime("%H:%M:%S")


def render_chat(turn_messages):
    console.clear()
    table = Table.grid(padding=(0, 1))
    table.add_column("Header", width=20, no_wrap=True)
    table.add_column("Message")

    for author, timestamp, content in turn_messages:
        badge_style = ROLE_STYLES.get(author, "bold white on grey")
        header = Text(f"[{author}]", style=badge_style) + Text(
            f" {timestamp}", style="dim"
        )
        indent = "    " if author in INDENT_ROLES else ""
        table.add_row(header, Text(indent) + content)

    panel = Panel(table, title="Chat", padding=(1, 2))
    console.print(panel)


async def select_session(sessions):
    console.print("\n[bold yellow]Available Sessions:[/bold yellow]")
    for idx, s in enumerate(sessions, 1):
        console.print(f"{idx}. {s}")

    while True:
        choice = await asyncio.to_thread(
            console.input,
            "[bold blue]Select session by number or type 'new': [/bold blue]",
        )
        choice = choice.strip()
        if choice.lower() == "new":
            session_name = await asyncio.to_thread(
                console.input, "[bold green]Enter new session name: [/bold green]"
            )
            session_name = session_name.strip()
            if session_name:
                return session_name
        elif choice.isdigit() and 1 <= int(choice) <= len(sessions):
            return sessions[int(choice) - 1]
        console.print("[bold red]Invalid input. Try again.[/bold red]")


async def call_coding_buddy(query: str, session_id: str, fix: bool = False):
    if fix:
        with mss.mss() as sct:
            # Grab the entire screen
            screenshot = sct.shot(output="error.png")
            query = (
                f"Here is the Image Path:{screenshot} Extract the error from the image"
            )

    url = "http://localhost:8002/run"
    payload = {"query": query, "session_id": session_id, "user_id": USER_ID}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=payload) as response:
            r = await response.json()
            return r


async def main():
    sessions_data = {}

    # Initial session selection/creation
    session_name = await select_session(list(sessions_data.keys()))
    if session_name not in sessions_data:
        sessions_data[session_name] = []
        sessions_data[session_name].append(
            ("Session", time_now(), Text(f"Current Session: {session_name}"))
        )
        render_chat([sessions_data[session_name][-1]])

    while True:
        turn_messages = []

        prompt = f"[bold blue]{session_name} > You[/bold blue] "
        user_input = await asyncio.to_thread(console.input, prompt)
        user_input = user_input.strip()

        if not user_input:
            console.print("\n[bold red]Goodbye![/bold red]")
            break

        # Check for session switch keyword
        if user_input.lower() == "/switch":
            session_name = await select_session(list(sessions_data.keys()))
            if session_name not in sessions_data:
                sessions_data[session_name] = []
                sessions_data[session_name].append(
                    ("Session", time_now(), Text(f"Current Session: {session_name}"))
                )
            render_chat([sessions_data[session_name][-1]])
            continue

        if user_input.lower() == "/exit":
            break

        if user_input.lower() == "/fix":
            agent_response = await call_coding_buddy(
                query=user_input, session_id=session_name, fix=True
            )

        agent_response = await call_coding_buddy(
            query=user_input, session_id=session_name
        )

        # User message
        turn_messages.append(("You", time_now(), Text(user_input, style="blue")))
        sessions_data[session_name].extend(turn_messages)
        render_chat(turn_messages)

        # Agent Response
        turn_messages.append(
            (
                "Agent",
                time_now(),
                Text(agent_response.get("final_response"), style="green"),
            )
        )
        sessions_data[session_name].append(turn_messages[-1])
        render_chat(turn_messages)

        # Tool calling
        turn_messages.append(
            (
                "Tool Calling",
                time_now(),
                Text(
                    str([f for f in agent_response.get("function_calls", [])]),
                    style="red",
                ),
            )
        )
        sessions_data[session_name].append(turn_messages[-1])
        render_chat(turn_messages)

        # Tool response
        turn_messages.append(
            (
                "Tool Response",
                time_now(),
                Text(
                    str([f for f in agent_response.get("function_responses", [])]),
                    style="cyan",
                ),
            )
        )
        sessions_data[session_name].append(turn_messages[-1])
        render_chat(turn_messages)


def start_coding_buddy():
    asyncio.run(main())
