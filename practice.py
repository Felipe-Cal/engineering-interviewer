#!/usr/bin/env python3
"""
Engineering Interview Practice Tool

Simulates two interview rounds from a modern communications platform's engineering guide:
  1. Coding Interview (60 min) — analyze engineering signals, produce executive summary
  2. System Design Interview (60 min) — design real-world or AI systems
"""

import os
import sys
import json
import time
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ─── Datasets ─────────────────────────────────────────────────────────────────

GITLAB_METRICS = {
    "period": "2024-Q4 (Oct-Dec)",
    "pipelines": [
        {"week": "W40", "total_runs": 312, "passed": 278, "failed": 34, "avg_duration_min": 8.2,  "top_failure_stage": "test"},
        {"week": "W41", "total_runs": 298, "passed": 241, "failed": 57, "avg_duration_min": 9.7,  "top_failure_stage": "test"},
        {"week": "W42", "total_runs": 344, "passed": 310, "failed": 34, "avg_duration_min": 7.9,  "top_failure_stage": "lint"},
        {"week": "W43", "total_runs": 267, "passed": 255, "failed": 12, "avg_duration_min": 7.5,  "top_failure_stage": "lint"},
        {"week": "W44", "total_runs": 389, "passed": 321, "failed": 68, "avg_duration_min": 11.3, "top_failure_stage": "build"},
        {"week": "W45", "total_runs": 402, "passed": 348, "failed": 54, "avg_duration_min": 10.8, "top_failure_stage": "build"},
        {"week": "W46", "total_runs": 356, "passed": 334, "failed": 22, "avg_duration_min": 8.1,  "top_failure_stage": "test"},
        {"week": "W47", "total_runs": 278, "passed": 261, "failed": 17, "avg_duration_min": 7.8,  "top_failure_stage": "lint"},
        {"week": "W48", "total_runs": 415, "passed": 367, "failed": 48, "avg_duration_min": 12.4, "top_failure_stage": "e2e"},
        {"week": "W49", "total_runs": 398, "passed": 341, "failed": 57, "avg_duration_min": 13.1, "top_failure_stage": "e2e"},
        {"week": "W50", "total_runs": 211, "passed": 195, "failed": 16, "avg_duration_min": 8.9,  "top_failure_stage": "test"},
        {"week": "W51", "total_runs": 143, "passed": 138, "failed":  5, "avg_duration_min": 8.2,  "top_failure_stage": "lint"},
        {"week": "W52", "total_runs":  89, "passed":  86, "failed":  3, "avg_duration_min": 7.6,  "top_failure_stage": "test"},
    ],
    "merge_requests": {
        "total_merged": 487,
        "avg_time_to_merge_hours": 18.4,
        "median_time_to_merge_hours": 11.2,
        "p95_time_to_merge_hours": 72.3,
        "by_team": {
            "platform":       {"merged": 142, "avg_hours": 14.2, "review_cycles_avg": 1.8},
            "integrations":   {"merged":  98, "avg_hours": 22.7, "review_cycles_avg": 2.4},
            "mobile":         {"merged":  76, "avg_hours": 19.1, "review_cycles_avg": 2.1},
            "infrastructure": {"merged": 171, "avg_hours": 16.8, "review_cycles_avg": 1.5},
        },
    },
    "incidents": [
        {"week": "W41", "severity": "P1", "duration_hours": 3.2, "root_cause": "failed_migration",       "preceded_by_pipeline_failures": True},
        {"week": "W44", "severity": "P2", "duration_hours": 1.1, "root_cause": "dependency_update",      "preceded_by_pipeline_failures": True},
        {"week": "W45", "severity": "P2", "duration_hours": 0.8, "root_cause": "dependency_update",      "preceded_by_pipeline_failures": True},
        {"week": "W48", "severity": "P1", "duration_hours": 4.7, "root_cause": "e2e_regression_missed",  "preceded_by_pipeline_failures": False},
        {"week": "W49", "severity": "P2", "duration_hours": 2.3, "root_cause": "e2e_regression_missed",  "preceded_by_pipeline_failures": False},
    ],
}

JIRA_METRICS = {
    "period": "2024-Q4 (Oct-Dec)",
    "sprints": [
        {"sprint": "S22", "team": "platform",     "planned": 34, "completed": 28, "carried_over":  6, "bugs_filed": 4, "avg_cycle_days": 3.2},
        {"sprint": "S23", "team": "platform",     "planned": 31, "completed": 31, "carried_over":  0, "bugs_filed": 2, "avg_cycle_days": 2.9},
        {"sprint": "S24", "team": "platform",     "planned": 38, "completed": 27, "carried_over": 11, "bugs_filed": 7, "avg_cycle_days": 5.1},
        {"sprint": "S25", "team": "platform",     "planned": 29, "completed": 25, "carried_over":  4, "bugs_filed": 3, "avg_cycle_days": 4.2},
        {"sprint": "S22", "team": "integrations", "planned": 22, "completed": 19, "carried_over":  3, "bugs_filed": 5, "avg_cycle_days": 4.8},
        {"sprint": "S23", "team": "integrations", "planned": 24, "completed": 20, "carried_over":  4, "bugs_filed": 4, "avg_cycle_days": 5.2},
        {"sprint": "S24", "team": "integrations", "planned": 26, "completed": 24, "carried_over":  2, "bugs_filed": 3, "avg_cycle_days": 4.1},
        {"sprint": "S25", "team": "integrations", "planned": 23, "completed": 23, "carried_over":  0, "bugs_filed": 2, "avg_cycle_days": 3.7},
    ],
    "bug_backlog": {
        "total_open": 87,
        "p1_critical": 3,
        "p2_high": 14,
        "p3_medium": 41,
        "p4_low": 29,
        "oldest_open_days": 94,
        "avg_age_days": 18.3,
    },
    "ticket_aging": [
        {"bucket": "< 7 days",   "count": 312},
        {"bucket": "7-30 days",  "count":  94},
        {"bucket": "30-60 days", "count":  38},
        {"bucket": "60-90 days", "count":  22},
        {"bucket": "> 90 days",  "count":  11},
    ],
}

DATASETS = {
    "gitlab": GITLAB_METRICS,
    "jira":   JIRA_METRICS,
}

# ─── Coding Exercise Prompts ───────────────────────────────────────────────────

CODING_PROMPTS = [
    {
        "id": "ci_health",
        "title": "CI/CD Health Report",
        "dataset_key": "gitlab",
        "prompt": """\
## Context
You're an engineer at a global cloud-based communications platform. Your EM has asked you to build a script that analyzes
recent GitLab CI/CD data and produces an **executive-style summary** for the VP of
Engineering's weekly review.

## Data
You have Q4 pipeline metrics, merge request data, and incident records (printed below).

## Requirements  (some are intentionally vague)
1. Compute the overall pipeline **pass rate** for the quarter.
2. Identify **notable trends** — weeks or periods that stand out.
3. Flag any **correlation** between pipeline health and production incidents.
4. Produce a concise **executive summary** suitable for a non-technical audience.
   The exact format is up to you — interpret what's most useful.

## Constraints
- Terminal output is fine; no UI needed.
- Python, TypeScript, or Java are all acceptable.
- Don't worry about perfect formatting — focus on correct insights.
""",
    },
    {
        "id": "sprint_health",
        "title": "Sprint Delivery Health",
        "dataset_key": "jira",
        "prompt": """\
## Context
You work on the engineering-productivity team at a fast-growing SaaS communications company. A product director has asked
for a summary of **team delivery health** across Q4 to help plan Q1 resourcing.

## Data
You have sprint-level Jira metrics for two teams: platform and integrations (printed below).

## Requirements  (some are intentionally vague)
1. Compute **velocity trends** for each team across sprints.
2. Determine whether either team has a **systemic carry-over problem**.
3. Surface **bug trends** — is quality improving or degrading over time?
4. Highlight the **ticket aging** distribution — are items getting stuck?
5. Write an **executive summary** with concrete, actionable recommendations.

## Constraints
- Terminal output is fine; no UI needed.
- Python, TypeScript, or Java are all acceptable.
- Focus on correct insights over code style.
""",
    },
]

# ─── System Design Prompts ────────────────────────────────────────────────────

SYSTEM_DESIGN_PROMPTS = [
    {
        "id": "call_intelligence",
        "title": "Real-Time Call Intelligence Platform",
        "prompt": """\
Design a system that provides **real-time intelligence** during phone calls for the platform's customers.

The system should:
- Transcribe calls in real time as they happen.
- Surface relevant information to the agent during the call (e.g., customer history,
  suggested responses, compliance alerts).
- Generate a call summary and action items automatically after the call ends.
- Support ~50,000 concurrent calls at peak load.

You have 60 minutes. Start by asking any clarifying questions you need.
""",
    },
    {
        "id": "engineering_metrics",
        "title": "Engineering Metrics Platform",
        "prompt": """\
Design a platform that collects, stores, and surfaces **engineering productivity metrics**
across all teams at a mid-sized SaaS company (~200 engineers, 20 teams).

Data sources include: GitLab (pipelines, MRs), Jira (tickets, sprints),
PagerDuty (incidents), and GitHub (code review).

The platform should:
- Ingest data from multiple sources with different update frequencies.
- Power a real-time dashboard for EMs and VPs.
- Support custom alerts (e.g., "notify me if pass rate drops below 80%").
- Enable historical trend analysis going back 2 years.

You have 60 minutes. Start by asking any clarifying questions you need.
""",
    },
    {
        "id": "rag_support",
        "title": "AI-Powered Support Knowledge Base",
        "prompt": """\
Design an AI system that helps the company's support agents answer customer questions.

The system should:
- Index the company's documentation, help articles, and past resolved tickets
  (~500,000 documents total).
- Allow agents to ask natural-language questions and receive grounded answers
  with citations — no hallucinations.
- Improve over time based on agent feedback (thumbs up / thumbs down).
- Scale from ~2,000 queries/day today to ~20,000 queries/day in 12 months.

You have 60 minutes. Start by asking any clarifying questions you need.
""",
    },
]

# ─── AI Interviewer System Prompts ────────────────────────────────────────────

def coding_system_prompt(prompt_data: dict, dataset: dict) -> str:
    return f"""\
You are a senior software engineer at a cloud communications company conducting a 60-minute coding interview.

The candidate has been given this exercise:

---
{prompt_data['prompt']}
---

Dataset available to them:
```json
{json.dumps(dataset, indent=2)}
```

Your role:
- Be a friendly, professional engineer — not a quiz show host.
- Answer clarifying questions helpfully. Where the requirements are ambiguous, give a
  reasonable, realistic answer (as a real EM would).
- When the candidate shares code or reasoning, engage with it honestly: point out what
  works, ask about edge cases, suggest alternatives only if they seem stuck.
- Do NOT solve the problem for them — ask leading questions instead.
- At the very end (when they say they're done or time is called), provide a structured
  evaluation across these four dimensions:
    1. Requirements Understanding — did they identify ambiguities, ask clarifying questions?
    2. Problem-Solving Approach — did they decompose the problem, think out loud?
    3. Working with Data — did they parse, aggregate, identify patterns correctly?
    4. Engineering Judgment — did they make sensible trade-offs and explain their choices?

Do NOT penalise for algorithm trivia, LeetCode patterns, or perfect formatting.

Start the session by greeting the candidate, briefly confirming the exercise title,
and inviting them to ask any initial clarifying questions before they start coding.
"""


def system_design_system_prompt(prompt_data: dict) -> str:
    return f"""\
You are a staff engineer at a cloud communications company conducting a 60-minute system design interview.

The candidate has been asked to design:

---
{prompt_data['prompt']}
---

Your role:
- Let the candidate drive — don't over-prompt or give away the architecture.
- Ask targeted follow-up questions to probe depth, for example:
    * "How does that component scale to 10x load?"
    * "What happens if that service goes down mid-call?"
    * "How would you monitor that in production?"
    * "What are the trade-offs of using X vs Y here?"
    * For AI designs: "How would you measure retrieval quality?" /
      "How do you prevent hallucinations?" / "How do you handle model updates?"
- Naturally cover these areas over the 60 minutes:
    * System architecture (service boundaries, APIs, data flow)
    * Data & storage (data models, storage choice, indexing)
    * Scalability (sync vs async, queues, caching, horizontal scaling)
    * Reliability (retries, rate limiting, graceful degradation)
    * For AI systems: knowledge retrieval pipeline, retrieval quality, grounding,
      production operations (monitoring, model updates, cost/latency)

At the very end (when the candidate wraps up or time is called), provide a structured
evaluation across:
    1. Clarity — did they define scope and system boundaries clearly?
    2. Reasoned Decisions — did they justify choices and acknowledge trade-offs?
    3. Scalability Awareness — did they identify bottlenecks and plan for growth?
    4. Operational Thinking — monitoring, deployment, long-term maintenance?
    (For AI designs, also evaluate: retrieval quality, grounding, production ops)

Keep follow-up questions short and natural. One question at a time — don't pile on.

Start by briefly confirming the problem statement and inviting the candidate to begin.
"""

# ─── Interview Runner ─────────────────────────────────────────────────────────

class Interview:
    def __init__(self, system_prompt: str, title: str, duration_min: int = 60):
        self.client = anthropic.Anthropic()
        self.system = system_prompt
        self.title = title
        self.duration_min = duration_min
        self.messages: list = []
        self.start_time: float = 0.0

    def elapsed(self) -> str:
        secs = int(time.time() - self.start_time)
        return f"{secs // 60}:{secs % 60:02d}"

    def remaining_secs(self) -> int:
        return max(0, self.duration_min * 60 - int(time.time() - self.start_time))

    def remaining(self) -> str:
        s = self.remaining_secs()
        return f"{s // 60}:{s % 60:02d}"

    def send(self, user_content: str) -> str:
        self.messages.append({"role": "user", "content": user_content})
        full_response = ""

        print(f"\n\033[94mInterviewer\033[0m [{self.elapsed()}]: ", end="", flush=True)

        with self.client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=self.system,
            messages=self.messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text

        print()
        self.messages.append({"role": "assistant", "content": full_response})
        return full_response

    def run(self):
        self.start_time = time.time()
        warned_5min = False

        print(f"\n{'─' * 62}")
        print(f"  {self.title}")
        print(f"  Duration: {self.duration_min} minutes")
        print(f"{'─' * 62}")
        print("  Commands:  'done' — wrap up and get evaluation")
        print("             'time' — check time remaining")
        print("             'quit' — exit without evaluation")
        print(f"{'─' * 62}\n")

        # Interviewer opens
        self.send("[INTERVIEW_START]")

        while True:
            remaining = self.remaining_secs()

            if remaining <= 0:
                print("\n\033[93m[TIME'S UP]\033[0m The 60 minutes are over.\n")
                break

            if remaining <= 300 and not warned_5min:
                warned_5min = True
                print("\n\033[93m[5 MINUTES REMAINING]\033[0m\n")

            try:
                user_input = input(f"\n\033[92mYou\033[0m [{self.elapsed()}]: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nInterview interrupted.")
                sys.exit(0)

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd == "quit":
                print("\nExiting without evaluation. Good luck!\n")
                return

            if cmd == "time":
                print(f"  Time remaining: {self.remaining()}")
                continue

            if cmd == "done":
                break

            self.send(user_input)

        # Final evaluation
        print(f"\n{'─' * 62}")
        print("  Time called — requesting evaluation")
        print(f"{'─' * 62}\n")
        self.send(
            "[INTERVIEW_END] Please provide your structured evaluation of the candidate "
            "based on our conversation so far."
        )
        print(f"\n{'─' * 62}")
        print("  Interview complete. Good luck!")
        print(f"{'─' * 62}\n")


# ─── Menu Helpers ─────────────────────────────────────────────────────────────

def pick(prompt: str, options: list[str]) -> int:
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = int(input("\nEnter number: ").strip())
            if 1 <= choice <= len(options):
                return choice - 1
        except (ValueError, EOFError):
            pass
        print(f"  Please enter a number between 1 and {len(options)}.")


# ─── Interview Launchers ──────────────────────────────────────────────────────

def run_coding_interview():
    idx = pick("Choose an exercise:", [p["title"] for p in CODING_PROMPTS])
    p = CODING_PROMPTS[idx]
    dataset = DATASETS[p["dataset_key"]]

    print(f"\n\033[1mExercise: {p['title']}\033[0m")
    print("\nDataset (also visible to the interviewer):")
    print(json.dumps(dataset, indent=2))

    system = coding_system_prompt(p, dataset)
    Interview(system, f"Coding Interview — {p['title']}").run()


def run_system_design_interview():
    idx = pick("Choose a design problem:", [p["title"] for p in SYSTEM_DESIGN_PROMPTS])
    p = SYSTEM_DESIGN_PROMPTS[idx]
    system = system_design_system_prompt(p)
    Interview(system, f"System Design — {p['title']}").run()


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Copy .env.example to .env and add your key, then run: source .env")
        sys.exit(1)

    print("\n\033[1m╔════════════════════════════════════════════╗")
    print("║       Engineering Interview Practice       ║")
    print("╚════════════════════════════════════════════╝\033[0m")
    print("""
Two rounds to practice:
  1. Coding Interview (60 min)
     Analyze an engineering-signals dataset and generate an executive summary.
  2. System Design Interview (60 min)
     Design a real-world or AI system and defend your architecture.

The AI interviewer will ask clarifying questions, give feedback, and evaluate
you at the end using the same rubric from the company's prep guide.
""")

    options = ["Coding Interview", "System Design Interview", "Exit"]
    while True:
        choice = pick("Select a round:", options)
        if choice == 0:
            run_coding_interview()
        elif choice == 1:
            run_system_design_interview()
        else:
            print("\nGood luck with the real interview!\n")
            break


if __name__ == "__main__":
    main()
