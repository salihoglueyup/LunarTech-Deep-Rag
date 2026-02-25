# Extending the User Interface (UI)

LunarTech uses a component-based architecture mimicking React, despite being built on Streamlit. If you want to add a new page (e.g., "Financial Analyst Dashboard"), follow these steps:

## 1. Create the View

Create a new Python file in the `app/views/` directory. For example, `app/views/finance.py`.

```python
import streamlit as st
from app.lang import LANG

def t(key):
    lang = st.session_state.get('lang', 'tr')
    return LANG.get(lang, LANG['tr']).get(key, key)

def render_finance_page():
    st.markdown('<div class="pg-header"><div class="pg-title">💰 Finance Dashboard</div></div>', unsafe_allow_html=True)
    
    st.write("Welcome to the new finance view.")
    # Add your graphs, chat inputs, or tables here...
```

## 2. Register the View in the Sidebar

Open `app/components/sidebar.py`.
Locate the `pages` dictionary mapping inside the `render_sidebar()` function and add your new view:

```python
pages = {
    "💬 Chat": "chat",
    "📚 Handbook": "handbook",
    "🧠 AI Tools": "ai_tools",
    "📊 Dashboard": "dashboard",
    "🔬 Knowledge Graph": "kg",
    "🕒 Shadow Agents": "shadow_agents",
    "🧩 Swarm Studio": "swarm_studio",
    "💰 Finance": "finance" # <--- ADD THIS
}
```

## 3. Map the View in the Main Router

Finally, tell the main event loop what to do when your page is selected.
Open `app/main.py` and locate the page routing `if/elif` block:

```python
from app.views import finance

# ... inside the main loop ...
elif page == "finance":
    finance.render_finance_page()
```

## 4. Add CSS Styling (Optional)

If your new view requires custom CSS grid layouts or specialized animations, append your CSS rules to the raw string inside `app/components/theme.py`. Avoid using inline HTML `<style>` tags directly inside your view functions.
