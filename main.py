#!/usr/bin/env python3
"""
Main Entry Point: AI-Powered Career Guidance and Resume Intelligence System
AI/ML with Python Training Program - October 2026 Batch
Production-Grade Terminal Application
"""

import os
import sys
import glob
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.resume_parser import parse_resume
from src.career_recommendation import CareerRecommender
from src.job_matching import JobMatcher, batch_screen_resumes
from src.ai_suggestions import (
    generate_professional_summary,
    rewrite_project_description,
    create_learning_roadmap,
    get_active_provider
)
from src.chatbot import CareerChatbot

console = Console()

class CareerSystemApp:
    def __init__(self):
        self.candidate: Optional[Dict[str, Any]] = None
        self.recommender = CareerRecommender()
        self.sample_resumes = [
            ("sample_data/sample_resumes/alex_morgan_ai_ml_engineer.pdf", "Alex Morgan (AI/ML Engineer)"),
            ("sample_data/sample_resumes/sarah_chen_data_scientist.pdf", "Sarah Chen (Data Scientist)"),
            ("sample_data/sample_resumes/david_kim_software_engineer.pdf", "David Kim (Full Stack Developer)"),
            ("sample_data/sample_resumes/priya_patel_cloud_devops.pdf", "Priya Patel (Cloud & DevOps Engineer)")
        ]
        self.sample_jds = [
            ("sample_data/job_descriptions/ml_engineer_jd.txt", "Machine Learning Engineer (Apex AI)"),
            ("sample_data/job_descriptions/data_scientist_jd.txt", "Senior Data Scientist (InsightMetrics)"),
            ("sample_data/job_descriptions/cloud_devops_jd.txt", "Cloud & DevOps Engineer (CloudScale)"),
            ("sample_data/job_descriptions/fullstack_jd.txt", "Full Stack Software Engineer (Nova Web)")
        ]

    def print_banner(self):
        banner_text = (
            "[bold white]AI-POWERED CAREER GUIDANCE & RESUME INTELLIGENCE SYSTEM[/bold white]\n"
            "[cyan]Production-Grade AI/ML Engine • Terminal Interface • 40+ Industry Roles[/cyan]\n"
            f"[dim]Live Inference Engine: [bold green]{get_active_provider().upper()}[/bold green] | "
            f"Taxonomy: [bold cyan]600+ Skills[/bold cyan][/dim]"
        )
        console.print(Panel(banner_text, style="blue on navy_blue", expand=False))

    def print_status_badge(self):
        if self.candidate:
            name = self.candidate.get("name", "Candidate")
            file_name = self.candidate.get("file_name", "Unknown")
            skills_count = len(self.candidate.get("skills", []))
            exp_yrs = self.candidate.get("estimated_experience_years", "N/A")
            degree = self.candidate.get("highest_degree", "Degree")
            email = self.candidate.get("contact", {}).get("email") or "Not found"

            status_text = (
                f"[bold green]Active Candidate:[/bold green] [bold white]{name}[/bold white] ({file_name})\n"
                f"• [cyan]Education:[/cyan] {degree} | [cyan]Experience:[/cyan] ~{exp_yrs} yrs | [cyan]Skills Extracted:[/cyan] {skills_count}\n"
                f"• [dim]Contact: {email}[/dim]"
            )
            console.print(Panel(status_text, style="green", expand=False))
        else:
            console.print(Panel("[bold yellow]No Resume Loaded.[/bold yellow] Please select option [1] to load candidate PDF.", style="yellow", expand=False))

    def load_resume_menu(self):
        console.print("\n[bold cyan]=== Load & Parse Resume (PDF) ===[/bold cyan]")
        console.print("Choose an option:")
        for idx, (path, label) in enumerate(self.sample_resumes, 1):
            console.print(f"  [{idx}] Sample: {label}")
        console.print(f"  [{len(self.sample_resumes) + 1}] Enter custom PDF file path")
        console.print("  [0] Back to Main Menu")

        choice = Prompt.ask("Select option", default="1")
        if choice == "0":
            return

        selected_path = None
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(self.sample_resumes):
                selected_path = self.sample_resumes[choice_num - 1][0]
            elif choice_num == len(self.sample_resumes) + 1:
                selected_path = Prompt.ask("Enter the full path to your PDF resume").strip('"\'')
        except ValueError:
            console.print("[red]Invalid selection.[/red]")
            return

        if not selected_path:
            return

        try:
            with console.status("[bold green]Parsing PDF and computing multi-column intelligence..."):
                self.candidate = parse_resume(selected_path)
            console.print(f"[bold green]Successfully parsed resume:[/bold green] {self.candidate['name']}")
            console.print(f"Detected [bold cyan]{len(self.candidate['skills'])}[/bold cyan] skills across {len(self.candidate['skills_by_category'])} categories.")
            console.print(f"Estimated Work Experience: [bold yellow]~{self.candidate['estimated_experience_years']} years[/bold yellow] | Highest Degree: [bold cyan]{self.candidate['highest_degree']}[/bold cyan]")
        except Exception as e:
            console.print(f"[bold red]Failed to load resume:[/bold red] {e}")

    def view_candidate_profile(self):
        if not self.candidate:
            console.print("[yellow]Please load a resume first (Option 1).[/yellow]")
            return

        console.print(f"\n[bold cyan]=== Comprehensive Candidate Profile: {self.candidate['name']} ===[/bold cyan]")
        contact = self.candidate.get("contact", {})
        console.print(f"[bold]Email:[/bold] {contact.get('email') or 'N/A'} | [bold]Phone:[/bold] {contact.get('phone') or 'N/A'}")
        console.print(f"[bold]LinkedIn:[/bold] {contact.get('linkedin') or 'N/A'} | [bold]GitHub:[/bold] {contact.get('github') or 'N/A'}")
        console.print(f"[bold]Highest Degree:[/bold] {self.candidate.get('highest_degree')} | [bold]Experience:[/bold] ~{self.candidate.get('estimated_experience_years')} yrs")

        verb_metrics = self.candidate.get("action_verb_metrics", {})
        console.print(f"[bold]ATS Action Verb Density Score:[/bold] [green]{verb_metrics.get('action_verb_score', 0)}/100[/green] (Key Verbs: {', '.join(verb_metrics.get('verbs_used', [])[:6])})")

        table = Table(title="Extracted Skills by Domain Taxonomy", show_header=True, header_style="bold magenta")
        table.add_column("Domain Category", style="cyan", width=32)
        table.add_column("Verified Technical Skills", style="white")

        for cat, skills in self.candidate.get("skills_by_category", {}).items():
            table.add_row(cat, ", ".join(skills))

        console.print(table)

    def career_recommendation_menu(self):
        if not self.candidate:
            console.print("[yellow]Please load a resume first (Option 1).[/yellow]")
            return

        console.print("\n[bold cyan]=== Career Path Recommendation Engine ===[/bold cyan]")
        categories = ["All"] + self.recommender.get_categories()
        console.print("Filter by Career Domain:")
        for idx, cat in enumerate(categories, 1):
            console.print(f"  [{idx}] {cat}")

        cat_choice = Prompt.ask("Select domain filter", default="1")
        selected_category = "All"
        try:
            c_idx = int(cat_choice)
            if 1 <= c_idx <= len(categories):
                selected_category = categories[c_idx - 1]
        except ValueError:
            pass

        top_k = int(Prompt.ask("Number of career recommendations to display", default="6"))

        with console.status("[bold green]Calculating TF-IDF semantic alignment and eligibility..."):
            recommendations = self.recommender.recommend(
                self.candidate,
                top_k=top_k,
                category_filter=selected_category if selected_category != "All" else None
            )

        table = Table(title=f"Top {len(recommendations)} Career Recommendations for {self.candidate['name']} [{selected_category}]", show_header=True, header_style="bold green")
        table.add_column("Rank", justify="center", style="dim", width=5)
        table.add_column("Role & Domain", style="bold white", width=28)
        table.add_column("Match Score", justify="center", style="bold yellow", width=12)
        table.add_column("Matched Skills", style="green", width=32)
        table.add_column("Key Missing Gaps", style="red", width=25)
        table.add_column("Demand & Salary", style="cyan", width=25)

        for rank, rec in enumerate(recommendations, 1):
            role_desc = f"{rec['role_name']}\n[dim]{rec['category']}[/dim]"
            score_bar = f"{rec['match_percentage']}%"
            matched = ", ".join(rec["matched_skills"][:5])
            if len(rec["matched_skills"]) > 5:
                matched += f" (+{len(rec['matched_skills']) - 5} more)"
            missing = ", ".join(rec["missing_skills"][:4]) if rec["missing_skills"] else "[green]None[/green]"
            demand_salary = f"[bold]{rec.get('market_demand', 'High')}[/bold]\n{rec['avg_salary_range']}"

            table.add_row(str(rank), role_desc, score_bar, matched or "None", missing, demand_salary)

        console.print(table)

    def job_matching_menu(self):
        if not self.candidate:
            console.print("[yellow]Please load a resume first (Option 1).[/yellow]")
            return

        console.print("\n[bold cyan]=== Enterprise ATS Job Matching & 4-Pillar Scorecard ===[/bold cyan]")
        console.print("Select a Job Description to match against:")
        for idx, (path, label) in enumerate(self.sample_jds, 1):
            console.print(f"  [{idx}] Sample: {label}")
        console.print(f"  [{len(self.sample_jds) + 1}] Load JD from a text file")
        console.print(f"  [{len(self.sample_jds) + 2}] Paste JD directly into terminal")
        console.print("  [0] Back to Main Menu")

        choice = Prompt.ask("Select option", default="1")
        if choice == "0":
            return

        jd_text = ""
        jd_title = "Target Position"

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(self.sample_jds):
                jd_path, jd_title = self.sample_jds[choice_num - 1]
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
            elif choice_num == len(self.sample_jds) + 1:
                custom_file = Prompt.ask("Enter path to JD text file").strip('"\'')
                with open(custom_file, "r", encoding="utf-8") as f:
                    jd_text = f.read()
                jd_title = os.path.basename(custom_file)
            elif choice_num == len(self.sample_jds) + 2:
                console.print("Paste the Job Description below (press Enter twice when finished):")
                lines = []
                while True:
                    try:
                        line = input()
                        if not line and lines and not lines[-1]:
                            break
                        lines.append(line)
                    except EOFError:
                        break
                jd_text = "\n".join(lines)
                jd_title = Prompt.ask("Enter role title", default="Custom Position")
        except Exception as e:
            console.print(f"[bold red]Error reading job description:[/bold red] {e}")
            return

        matcher = JobMatcher(self.candidate)
        with console.status("[bold green]Running 4-pillar ATS diagnostic analysis..."):
            result = matcher.match(jd_text, jd_title=jd_title)

        score = result["overall_match_percentage"]
        pillars = result["pillar_breakdown"]
        color = result["verdict_color"]

        summary_md = (
            f"### ATS Compatibility Audit: `{result['target_role']}`\n\n"
            f"**Candidate:** {result['candidate_name']}  \n"
            f"**Overall ATS Compatibility Index:** [{color}]{score}%[/{color}]  \n"
            f"**Readiness Verdict:** **{result['readiness_level']}**  \n"
            f"*{result['recommended_action']}*\n\n"
            f"---\n"
            f"#### 4-Pillar Diagnostic Breakdown:\n"
            f"• **Technical Skills Overlap (40% wt):** `{pillars['skill_alignment_score']}%` ({result['total_matching_skills']}/{result['total_jd_skills_found']} skills)\n"
            f"• **Semantic Relevance (25% wt):** `{pillars['semantic_similarity_score']}%`\n"
            f"• **Experience Fit (20% wt):** `{pillars['experience_fit_score']}%` (Candidate: ~{result['experience_comparison']['candidate_exp_years']} yrs vs Min: {result['experience_comparison']['jd_expected_min_years']} yrs)\n"
            f"• **Action-Verb Impact (15% wt):** `{pillars['action_verb_impact_score']}%`\n\n"
            f"---\n"
            f"**Matching Core Skills:**\n{', '.join(result['matching_skills']) or 'None'}\n\n"
            f"**Critical Missing Skill Gaps:**\n{', '.join([f'`{s}`' for s in result['missing_skills']]) or '[green]Zero technical gaps detected![/green]'}\n"
        )
        console.print(Panel(Markdown(summary_md), title="ATS Match Result", border_style=color))

        if Confirm.ask("Export this comprehensive ATS Audit Report to disk?", default=True):
            report_filename = f"reports/ats_audit_{self.candidate['name'].replace(' ', '_').lower()}.md"
            matcher.generate_report(result, save_path=report_filename)
            console.print(f"[bold green]Audit report successfully saved to:[/bold green] {report_filename}")

    def recruiter_batch_screening_menu(self):
        console.print("\n[bold cyan]=== Recruiter Mode: Multi-Candidate Batch Screening ===[/bold cyan]")
        console.print("Screen and rank all candidate resumes in a folder against a specific Job Description.")

        folder = Prompt.ask("Enter folder path containing candidate PDF resumes", default="sample_data/sample_resumes")
        pdf_files = glob.glob(os.path.join(folder, "*.pdf"))

        if not pdf_files:
            console.print(f"[red]No PDF resumes found in directory: {folder}[/red]")
            return

        console.print(f"Found [bold cyan]{len(pdf_files)}[/bold cyan] resumes for screening.")
        console.print("Select target Job Description:")
        for idx, (path, label) in enumerate(self.sample_jds, 1):
            console.print(f"  [{idx}] {label}")

        jd_choice = Prompt.ask("Select JD", default="1")
        try:
            jd_path, jd_title = self.sample_jds[int(jd_choice) - 1]
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        except Exception:
            return

        with console.status(f"[bold green]Batch screening {len(pdf_files)} resumes against {jd_title}..."):
            ranked = batch_screen_resumes(pdf_files, jd_text, role_title=jd_title)

        table = Table(title=f"Candidate Screening Leaderboard: {jd_title}", show_header=True, header_style="bold green")
        table.add_column("Rank", justify="center", style="dim", width=6)
        table.add_column("Candidate Name", style="bold white", width=25)
        table.add_column("ATS Fit %", justify="center", style="bold yellow", width=12)
        table.add_column("Skills Match", justify="center", style="cyan", width=14)
        table.add_column("Experience Fit", justify="center", style="magenta", width=16)
        table.add_column("Readiness Verdict", style="white")

        for rank, c in enumerate(ranked, 1):
            table.add_row(
                str(rank),
                c["candidate_name"],
                f"{c['overall_match_percentage']}%",
                f"{c['pillar_breakdown']['skill_alignment_score']}%",
                f"{c['pillar_breakdown']['experience_fit_score']}%",
                f"[{c['verdict_color']}]{c['readiness_level']}[/{c['verdict_color']}]"
            )

        console.print(table)

    def ai_optimizer_menu(self):
        if not self.candidate:
            console.print("[yellow]Please load a resume first (Option 1).[/yellow]")
            return

        console.print(f"\n[bold cyan]=== Generative AI Resume Optimizer (Provider: {get_active_provider().upper()}) ===[/bold cyan]")
        console.print("  [1] Generate ATS-Optimized Professional Summary")
        console.print("  [2] Rewrite Project Description (STAR Framework - No Fabricated Metrics)")
        console.print("  [3] Generate Personalized 8-Week Upskilling Roadmap")
        console.print("  [0] Back to Main Menu")

        choice = Prompt.ask("Select option", default="1")
        if choice == "1":
            target_role = Prompt.ask("Target career role for summary", default="Machine Learning Engineer")
            with console.status(f"[bold green]Generating summary using {get_active_provider().upper()}..."):
                summary = generate_professional_summary(self.candidate, target_role)
            console.print(Panel(Markdown(summary), title=f"AI Professional Summary ({target_role})", border_style="green"))

        elif choice == "2":
            sample_project = "Built a real-time object detection pipeline with YOLO and Docker on AWS."
            console.print(f"\n[dim]Default Sample Project: {sample_project}[/dim]")
            use_sample = Confirm.ask("Use default sample project?", default=True)
            if use_sample:
                proj_desc = sample_project
                tech_stack = "PyTorch, YOLO, Docker, AWS"
            else:
                proj_desc = Prompt.ask("Enter original project description")
                tech_stack = Prompt.ask("Enter tech stack used", default="Python")

            target_role = Prompt.ask("Target role alignment", default="Computer Vision Engineer")
            with console.status(f"[bold green]Rewriting using STAR method ({get_active_provider().upper()})..."):
                rewritten = rewrite_project_description(proj_desc, target_role, tech_stack)
            console.print(Panel(Markdown(rewritten), title="STAR Rewritten Bullet Points", border_style="cyan"))

        elif choice == "3":
            target_role = Prompt.ask("Target role for roadmap", default="MLOps Engineer")
            sample_gaps = ["Kubernetes", "MLflow", "Triton Server", "Terraform"]
            with console.status(f"[bold green]Synthesizing curriculum roadmap ({get_active_provider().upper()})..."):
                roadmap = create_learning_roadmap(sample_gaps, target_role, duration_weeks=8)
            console.print(Panel(Markdown(roadmap), title=f"Upskilling Roadmap ({target_role})", border_style="magenta"))

    def chatbot_menu(self):
        if not self.candidate:
            console.print("[yellow]Please load a resume first (Option 1).[/yellow]")
            return

        target_role = Prompt.ask("Enter target role for conversation context", default="Machine Learning Engineer")
        bot = CareerChatbot(self.candidate, target_role=target_role)
        bot.run_interactive_loop()

    def search_roles_catalog_menu(self):
        console.print("\n[bold cyan]=== Search & Browse 40+ Tech Career Catalog ===[/bold cyan]")
        query = Prompt.ask("Enter search keyword or role title (e.g. 'ML', 'Cloud', 'Data', 'Security')", default="AI")
        matches = self.recommender.search_roles(query)

        if not matches:
            console.print(f"[yellow]No roles found matching '{query}'.[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}' ({len(matches)} roles found)", show_header=True, header_style="bold cyan")
        table.add_column("Role Name", style="bold white", width=28)
        table.add_column("Category & Subcategory", style="cyan", width=25)
        table.add_column("Min Exp", justify="center", style="yellow", width=10)
        table.add_column("Market Demand", justify="center", style="magenta", width=14)
        table.add_column("Avg Salary", style="green", width=22)

        for m in matches[:10]:
            sub = f"{m['category']}\n[dim]({m.get('subcategory', '')})[/dim]"
            table.add_row(m["role_name"], sub, f"{m.get('min_experience_years', 1)} yrs", m.get("market_demand", "High"), m["avg_salary_range"])

        console.print(table)

    def run_tests_and_evaluation(self):
        console.print("\n[bold cyan]=== Running System Verification & Benchmark Suite ===[/bold cyan]")
        import evaluate_models
        evaluate_models.run_evaluation()

    def run(self):
        try:
            self.candidate = parse_resume(self.sample_resumes[0][0])
        except Exception:
            pass

        while True:
            console.print("\n")
            self.print_banner()
            self.print_status_badge()

            console.print("[bold]PRODUCTION APPLICATION CAPABILITIES[/bold]")
            console.print("  [1] Load & Parse Resume (PDF)")
            console.print("  [2] View Candidate Profile & 600+ Skills Breakdown")
            console.print("  [3] Career Path Recommendation Engine (with Domain Filtering)")
            console.print("  [4] Single Job Description ATS Matching & 4-Pillar Scorecard")
            console.print("  [5] Recruiter Mode: Multi-Candidate Batch Resume Screening")
            console.print("  [6] Search & Explore 40+ Industry Tech Roles Catalog")
            console.print("  [7] Generative AI Resume Optimizer (Summary, STAR Rewriter, Roadmap)")
            console.print("  [8] Interactive Context-Aware Career Counselor Chatbot")
            console.print("  [9] Run Automated System Benchmark Evaluation")
            console.print("  [0] Exit Application")

            choice = Prompt.ask("\nEnter menu choice", default="3")

            if choice == "1":
                self.load_resume_menu()
            elif choice == "2":
                self.view_candidate_profile()
            elif choice == "3":
                self.career_recommendation_menu()
            elif choice == "4":
                self.job_matching_menu()
            elif choice == "5":
                self.recruiter_batch_screening_menu()
            elif choice == "6":
                self.search_roles_catalog_menu()
            elif choice == "7":
                self.ai_optimizer_menu()
            elif choice == "8":
                self.chatbot_menu()
            elif choice == "9":
                self.run_tests_and_evaluation()
            elif choice in ["0", "exit", "quit"]:
                console.print("[bold green]Thank you for using AI-Powered Career Guidance. Goodbye![/bold green]")
                break
            else:
                console.print("[red]Invalid selection, please try again.[/red]")

def main():
    app = CareerSystemApp()
    app.run()

if __name__ == "__main__":
    main()
