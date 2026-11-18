"""
Module: chatbot.py
Description: Interactive command-line career guidance chatbot grounded in candidate's
extracted resume profile and target role.
"""

from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.ai_suggestions import answer_career_question, generate_professional_summary, create_learning_roadmap

console = Console()

class CareerChatbot:
    """Conversational assistant for candidate career guidance and resume intelligence."""

    def __init__(self, candidate_profile: Dict[str, Any], target_role: Optional[str] = None):
        self.candidate = candidate_profile
        self.target_role = target_role or "Machine Learning Engineer"
        self.history: List[Dict[str, str]] = []

    def print_welcome(self):
        name = self.candidate.get("name", "Candidate")
        skills_count = len(self.candidate.get("skills", []))
        
        welcome_md = (
            f"### Welcome to the Career Guidance Assistant!\n\n"
            f"**Candidate Context:** {name} | **Identified Skills:** {skills_count}\n"
            f"**Current Target Role:** `{self.target_role}`\n\n"
            f"**Quick Shortcuts:**\n"
            f"- Type `/summary` to generate an ATS summary.\n"
            f"- Type `/roadmap` to create a learning roadmap.\n"
            f"- Type `/skills` to view your parsed skills.\n"
            f"- Type `/role <name>` to change your target role.\n"
            f"- Type `exit` or `quit` to return to the main menu.\n"
        )
        console.print(Panel(Markdown(welcome_md), title="[bold cyan]AI Career Counselor[/bold cyan]", border_style="cyan"))

    def set_target_role(self, new_role: str):
        self.target_role = new_role.strip()
        console.print(f"[bold green]Target role updated to:[/bold green] [bold yellow]{self.target_role}[/bold yellow]\n")

    def handle_input(self, user_msg: str) -> bool:
        """
        Processes a single user message.
        Returns False if user requests to exit, True otherwise.
        """
        trimmed = user_msg.strip()
        if not trimmed:
            return True

        lower = trimmed.lower()
        if lower in ["exit", "quit", "q", "bye"]:
            console.print("[bold yellow]Exiting Career Counselor session. Good luck with your career goals![/bold yellow]\n")
            return False

        if lower == "/summary":
            console.print("\n[dim]Generating ATS Professional Summary...[/dim]")
            summary = generate_professional_summary(self.candidate, self.target_role)
            console.print(Panel(Markdown(summary), title="[bold green]Generated Professional Summary[/bold green]", border_style="green"))
            return True

        if lower == "/roadmap":
            console.print("\n[dim]Synthesizing Personalized Learning Roadmap...[/dim]")
            roadmap = create_learning_roadmap(["System Design", "Cloud Deployment", "MLOps"], self.target_role, 6)
            console.print(Panel(Markdown(roadmap), title="[bold green]Career Roadmap[/bold green]", border_style="green"))
            return True

        if lower == "/skills":
            skills = self.candidate.get("skills", [])
            console.print(f"\n[bold cyan]Extracted Resume Skills ({len(skills)}):[/bold cyan]")
            console.print(", ".join([f"[green]{s}[/green]" for s in skills]) + "\n")
            return True

        if lower.startswith("/role "):
            new_role = trimmed[6:].strip()
            if new_role:
                self.set_target_role(new_role)
            return True

        # Generate contextual conversational response
        console.print("[dim]Analyzing profile context & formulating advice...[/dim]")
        answer = answer_career_question(self.candidate, trimmed, self.target_role)
        self.history.append({"user": trimmed, "assistant": answer})

        console.print(Panel(Markdown(answer), title=f"[bold blue]Advisor Response ({self.target_role})[/bold blue]", border_style="blue"))
        return True

    def run_interactive_loop(self):
        """Runs the continuous interactive terminal session."""
        self.print_welcome()
        while True:
            try:
                user_msg = console.input("[bold cyan]You > [/bold cyan]")
                should_continue = self.handle_input(user_msg)
                if not should_continue:
                    break
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Session terminated by user.[/yellow]")
                break

def launch_chatbot(candidate_profile: Dict[str, Any], target_role: Optional[str] = None):
    """Entry point helper to launch chatbot."""
    bot = CareerChatbot(candidate_profile, target_role)
    bot.run_interactive_loop()
