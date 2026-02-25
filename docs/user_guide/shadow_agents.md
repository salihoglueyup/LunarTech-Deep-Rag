# Shadow Agents (Background Workers)

Large Language Models (LLMs) are notorious for long generation times. If a user asks the AI to scrape 5 websites and compile a report, they often have to sit and watch a loading spinner for minutes.

LunarTech solves this by introducing **Shadow Agents**.

## How they work

Shadow Agents are persistent background tasks that run decoupled from the Streamlit UI event loop.

1. **Task Submission**
   Users navigate to the `Shadow Agents` view and define a task. This can be a "General Research", "Web Scrape", or "Database Analysis" task.
2. **Scheduling**
   Tasks can be executed `Immediate` or `Scheduled`. Scheduled tasks can be set to run infinitely on a cron-like interval (e.g., "Run every 60 minutes").
3. **Execution Pipeline**
   When a task is submitted, it is added to a persistent JSON-based queue (`tasks.json`). A completely separate Python thread `BackgroundWorker` checks this queue continuously. It pulls `pending` tasks, switches them to `running`, and executes the LLM workflow completely in the background.
4. **Result Retrieval**
   The user can close their browser entirely. The next day, they can log back into LunarTech, navigate to the Shadow Agents view, step into the completed task expanser, and retrieve the final 10,000-word report.
