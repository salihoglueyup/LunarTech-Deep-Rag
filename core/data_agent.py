import json
import logging
from services import supabase_service, llm_service

logger = logging.getLogger(__name__)

DATA_ANALYST_SYSTEM_PROMPT = """You are LunarTech AI's Expert Data Analyst agent.
You have been given a complete JSON dump of the system's current database tables.
Task: Analyze and answer the user's natural language questions based on this data.

Rules:
1. Present the data to the user professionally as tables or statistics.
2. If the user's question requires a Chart (Bar, Line, Pie, etc.), you must definitely produce a JSON in ECharts format.
3. When producing the chart, use the following format:
<echarts>
{ "tooltip": {}, "xAxis": {"type": "category", "data": [...]}, "yAxis": {"type": "value"}, "series": [{"data": [...], "type": "bar"}] }
</echarts>
4. Never make up your own data, only use the "Data Context" in the JSON.
5. Provide the answer in English using corporate language and Markdown format.
"""


def dynamic_data_agent(
    question: str, model: str, temperature: float = 0.2, csv_data: str = None
) -> str:
    """Analyzes the user's data analysis question by combining it with the data in the system."""

    # 1. Data Collection (Supabase REST API) -> Convert to Dictionary
    system_data = {"token_usage": [], "documents": [], "handbooks": []}

    try:
        # Token History
        tokens = supabase_service.get_all_token_usage()
        # Clean up heavy tokens dict slightly
        system_data["token_usage"] = [
            {
                "user_id": t.get("user_id"),
                "model": t.get("model"),
                "tokens": t.get("tokens"),
                "created_at": t.get("created_at"),
            }
            for t in tokens[:500]
        ]

        # Documents
        docs = supabase_service.get_documents()
        system_data["documents"] = [
            {
                "id": d.get("id"),
                "filename": d.get("filename"),
                "page_count": d.get("page_count"),
                "created_at": d.get("created_at"),
                "user_id": d.get("user_id"),
            }
            for d in docs
        ]

        # Handbooks
        hbs = supabase_service.get_handbooks()
        system_data["handbooks"] = [
            {
                "title": h.get("title"),
                "word_count": h.get("word_count"),
                "created_at": h.get("created_at"),
                "user_id": h.get("user_id"),
            }
            for h in hbs
        ]

    except Exception as e:
        logger.error(f"Data API Error: {e}")
        return f"An error occurred while fetching data from the database: {e}"

    if csv_data:
        system_data["user_uploaded_custom_file"] = csv_data

    # 2. Convert Data to Prompt (JSON Serialize)
    data_context = json.dumps(system_data, ensure_ascii=False, default=str)

    messages = [
        {"role": "system", "content": DATA_ANALYST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"## Database (Data Context):\n```json\n{data_context}\n```\n\n## User Question:\n{question}",
        },
    ]

    # 3. LLM API Call
    try:
        response = llm_service.chat_completion(
            messages=messages, model=model, max_tokens=4000, temperature=temperature
        )
        return response
    except Exception as e:
        logger.error(f"Data Agent LLM Error: {e}")
        return f"Could not communicate with the language model during analysis: {e}"
