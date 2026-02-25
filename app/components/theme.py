"""LunarTech AI — Premium CSS Theme"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,*::before,*::after{box-sizing:border-box}
.stApp{font-family:'Inter',-apple-system,sans-serif;background:#06080f;color:#e2e8f0}
.stApp::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 15% 50%,rgba(99,102,241,.08) 0%,transparent 55%),radial-gradient(ellipse at 85% 15%,rgba(139,92,246,.06) 0%,transparent 50%),radial-gradient(ellipse at 50% 85%,rgba(59,130,246,.05) 0%,transparent 50%);animation:cosmosShift 20s ease-in-out infinite alternate;z-index:-2;pointer-events:none}
@keyframes cosmosShift{0%{opacity:.8;transform:scale(1)}50%{opacity:1;transform:scale(1.03)}100%{opacity:.8;transform:scale(1)}}

.stars-container{position:fixed;inset:0;pointer-events:none;z-index:-1;overflow:hidden}
.star{position:absolute;border-radius:50%;animation:twinkle ease-in-out infinite}
.star:nth-child(1){width:2px;height:2px;top:12%;left:8%;background:rgba(165,180,252,.6);animation-duration:3s}
.star:nth-child(2){width:3px;height:3px;top:25%;left:22%;background:rgba(196,181,253,.4);animation-duration:4s;animation-delay:1s}
.star:nth-child(3){width:1px;height:1px;top:8%;left:45%;background:rgba(147,197,253,.7);animation-duration:2.5s;animation-delay:.5s}
.star:nth-child(4){width:2px;height:2px;top:65%;left:70%;background:rgba(165,180,252,.5);animation-duration:3.5s;animation-delay:2s}
.star:nth-child(5){width:3px;height:3px;top:40%;left:88%;background:rgba(196,181,253,.3);animation-duration:5s}
.star:nth-child(6){width:1px;height:1px;top:78%;left:35%;background:rgba(147,197,253,.6);animation-duration:2s;animation-delay:1.5s}
.star:nth-child(7){width:2px;height:2px;top:55%;left:55%;background:rgba(251,191,36,.3);animation-duration:4.5s;animation-delay:.8s}
.star:nth-child(8){width:1px;height:1px;top:90%;left:15%;background:rgba(165,180,252,.5);animation-duration:3s;animation-delay:3s}
@keyframes twinkle{0%,100%{opacity:.2;transform:scale(.8)}50%{opacity:1;transform:scale(1.2)}}

section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(10,10,20,.97) 0%,rgba(6,8,15,.99) 100%);border-right:1px solid rgba(99,102,241,.08)}
section[data-testid="stSidebar"] .stMarkdown h3{color:#475569;font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:2.5px;margin-top:1rem;margin-bottom:.4rem}

.logo-area{text-align:center;padding:.5rem 0 .2rem}
.logo-moon{display:inline-block;font-size:2.8rem;animation:moonOrbit 6s ease-in-out infinite;filter:drop-shadow(0 0 12px rgba(139,92,246,.5))}
@keyframes moonOrbit{0%,100%{transform:translateY(0) rotate(0deg);filter:drop-shadow(0 0 12px rgba(139,92,246,.5))}25%{transform:translateY(-4px) rotate(5deg);filter:drop-shadow(0 0 18px rgba(99,102,241,.6))}50%{transform:translateY(-2px) rotate(0deg);filter:drop-shadow(0 0 24px rgba(139,92,246,.7))}75%{transform:translateY(-4px) rotate(-5deg);filter:drop-shadow(0 0 18px rgba(99,102,241,.6))}}
.logo-text{background:linear-gradient(135deg,#c4b5fd,#818cf8,#6366f1,#a78bfa);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.4rem;font-weight:900;letter-spacing:-.5px;animation:gradShift 8s ease infinite}
.logo-sub{color:#334155;font-size:.6rem;letter-spacing:3px;text-transform:uppercase;font-weight:500}
@keyframes gradShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

.glow-div{border:none;height:1px;background:linear-gradient(90deg,transparent,rgba(99,102,241,.15),transparent);margin:.8rem 0}
.lang-btn{display:inline-flex;align-items:center;justify-content:center;width:36px;height:28px;border-radius:8px;cursor:pointer;transition:all .2s;font-size:1rem;text-decoration:none;border:1px solid transparent}
.lang-btn-active{background:rgba(99,102,241,.12);border-color:rgba(99,102,241,.25);box-shadow:0 0 10px rgba(99,102,241,.1)}
.lang-btn-inactive{background:rgba(255,255,255,.02);opacity:.5}
.lang-btn-inactive:hover{opacity:.8;background:rgba(99,102,241,.05)}

.stButton>button{background:rgba(255,255,255,.03);color:#94a3b8!important;border:1px solid rgba(255,255,255,.05);border-radius:10px;font-weight:500;font-size:.85rem;font-family:'Inter',sans-serif;padding:.45rem .8rem;transition:all .35s cubic-bezier(.4,0,.2,1);overflow:hidden}
.stButton>button:hover{background:rgba(99,102,241,.08);color:#c4b5fd!important;border-color:rgba(99,102,241,.2);transform:translateY(-1px);box-shadow:0 4px 20px rgba(99,102,241,.12)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,rgba(99,102,241,.25),rgba(139,92,246,.2));border:1px solid rgba(99,102,241,.3);color:#c4b5fd!important;box-shadow:0 0 15px rgba(99,102,241,.08)}

.glass{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:16px;padding:1.25rem;backdrop-filter:blur(16px);transition:all .4s cubic-bezier(.4,0,.2,1)}
.glass:hover{background:rgba(255,255,255,.04);border-color:rgba(99,102,241,.15);box-shadow:0 8px 40px rgba(99,102,241,.06)}

.pg-header{margin-bottom:1.5rem;animation:headerFade .5s ease-out}
@keyframes headerFade{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.pg-title{font-size:1.6rem;font-weight:800;letter-spacing:-.5px;margin-bottom:.15rem}
.pg-title-chat{background:linear-gradient(135deg,#c4b5fd,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pg-title-handbook{background:linear-gradient(135deg,#93c5fd,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pg-title-dash{background:linear-gradient(135deg,#6ee7b7,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pg-title-kg{background:linear-gradient(135deg,#fbbf24,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.pg-sub{color:#475569;font-size:.85rem}

.m-card{background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);border-radius:16px;padding:1.5rem 1rem;text-align:center;transition:all .3s ease;position:relative;overflow:hidden}
.m-card::before{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:linear-gradient(90deg,transparent,rgba(99,102,241,.4),transparent)}
.m-card:hover{border-color:rgba(99,102,241,.12);box-shadow:0 0 30px rgba(99,102,241,.05);transform:translateY(-2px)}
.m-val{font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,#c4b5fd,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1}
.m-lbl{color:#475569;font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;margin-top:.5rem}

.stChatMessage{animation:msgIn .35s ease-out;border:none!important;background:transparent!important}
@keyframes msgIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
div[data-testid="stChatMessage"]:has(img[alt="🧑‍💻"]){background:linear-gradient(135deg,rgba(99,102,241,.08),rgba(139,92,246,.05))!important;border:1px solid rgba(99,102,241,.1)!important;border-radius:16px 16px 4px 16px!important;margin-left:10%}
div[data-testid="stChatMessage"]:has(img[alt="🌙"]){background:rgba(255,255,255,.015)!important;border:1px solid rgba(255,255,255,.04)!important;border-radius:16px 16px 16px 4px!important;margin-right:10%}

.typing-dots{display:inline-flex;gap:4px;padding:8px 16px;background:rgba(255,255,255,.03);border-radius:20px;border:1px solid rgba(255,255,255,.05)}
.typing-dots span{width:6px;height:6px;background:#818cf8;border-radius:50%;animation:bounce 1.4s ease-in-out infinite}
.typing-dots span:nth-child(2){animation-delay:.16s}.typing-dots span:nth-child(3){animation-delay:.32s}
@keyframes bounce{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-6px);opacity:1}}

.welcome{background:linear-gradient(135deg,rgba(99,102,241,.04),rgba(139,92,246,.02),rgba(59,130,246,.02));border:1px solid rgba(99,102,241,.08);border-radius:24px;padding:3.5rem 2rem;text-align:center;animation:welcomeIn .6s ease;position:relative;overflow:hidden}
.welcome::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 40%,rgba(99,102,241,.04) 0%,transparent 50%);animation:welcomeGlow 8s ease-in-out infinite}
@keyframes welcomeIn{from{opacity:0;transform:scale(.96) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes welcomeGlow{0%,100%{transform:rotate(0deg)}50%{transform:rotate(180deg)}}
.welcome h2{font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,#e2e8f0,#94a3b8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;position:relative;z-index:1}
.welcome p{color:#475569;position:relative;z-index:1;line-height:1.6}

.feat{background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);border-radius:16px;padding:1.5rem 1rem;text-align:center;transition:all .4s cubic-bezier(.4,0,.2,1);cursor:default}
.feat:hover{background:rgba(99,102,241,.04);border-color:rgba(99,102,241,.15);transform:translateY(-4px);box-shadow:0 12px 40px rgba(99,102,241,.08)}
.feat-icon{font-size:2.2rem;margin-bottom:.6rem}.feat-title{color:#e2e8f0;font-weight:600;font-size:.9rem;margin-bottom:.35rem}.feat-desc{color:#475569;font-size:.78rem;line-height:1.45}

.doc{background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);border-radius:12px;padding:.6rem .9rem;margin-bottom:6px;transition:all .25s ease;display:flex;justify-content:space-between;align-items:center}
.doc:hover{background:rgba(99,102,241,.04);border-color:rgba(99,102,241,.12)}
.doc-info{flex:1}.doc-name{color:#cbd5e1;font-weight:500;font-size:.82rem}.doc-meta{color:#475569;font-size:.68rem;margin-top:2px}

.badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-size:.7rem;font-weight:500}
.badge-on{background:rgba(34,197,94,.08);color:#4ade80;border:1px solid rgba(34,197,94,.15)}
.badge-off{background:rgba(239,68,68,.08);color:#f87171;border:1px solid rgba(239,68,68,.15)}
.pulse-dot{display:inline-block;width:8px;height:8px;border-radius:50%;animation:pulse 2s ease-in-out infinite}
.pulse-on{background:#4ade80;box-shadow:0 0 8px rgba(74,222,128,.5)}.pulse-off{background:#f87171;box-shadow:0 0 8px rgba(248,113,113,.5)}
@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.4);opacity:.6}}

.e-chip{display:inline-block;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.15);color:#a5b4fc;padding:3px 10px;border-radius:20px;font-size:.75rem;margin:3px;transition:all .2s;cursor:default}
.e-chip:hover{background:rgba(99,102,241,.15);transform:scale(1.05)}
.r-chip{display:inline-block;background:rgba(251,191,36,.06);border:1px solid rgba(251,191,36,.12);color:#fbbf24;padding:3px 10px;border-radius:20px;font-size:.75rem;margin:3px}

.model-card{background:rgba(99,102,241,.03);border:1px solid rgba(99,102,241,.08);border-radius:10px;padding:8px 12px}
.model-id{color:#64748b;font-size:.68rem;font-family:monospace}.model-meta{color:#475569;font-size:.68rem;margin-top:3px}

.conv-item{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:10px;padding:6px 10px;margin-bottom:4px;cursor:pointer;transition:all .2s;display:flex;justify-content:space-between;align-items:center}
.conv-item:hover{background:rgba(99,102,241,.04);border-color:rgba(99,102,241,.12)}
.conv-active{background:rgba(99,102,241,.08)!important;border-color:rgba(99,102,241,.2)!important;border-left:3px solid #818cf8}
.conv-name{color:#cbd5e1;font-size:.78rem;font-weight:500}.conv-count{color:#475569;font-size:.65rem}

.mini-stat{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.02)}
.mini-stat-label{color:#475569;font-size:.72rem}.mini-stat-val{color:#94a3b8;font-size:.72rem;font-weight:600}

.sb-footer{text-align:center;padding:.5rem 0;margin-top:.5rem}
.sb-footer-text{color:#1e293b;font-size:.6rem}

.tl-item{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.02);animation:msgIn .3s ease-out}
.tl-dot{width:8px;height:8px;border-radius:50%;margin-top:6px;flex-shrink:0}
.tl-dot-user{background:#818cf8}.tl-dot-ai{background:#6ee7b7}
.tl-content{color:#64748b;font-size:.8rem;line-height:1.4}

.empty-state{text-align:center;padding:3rem 1rem;color:#334155}
.empty-icon{font-size:3rem;margin-bottom:.75rem;opacity:.5}.empty-text{font-size:.9rem}

.stFileUploader>div{border:2px dashed rgba(99,102,241,.12)!important;border-radius:14px;background:rgba(99,102,241,.01);transition:all .3s}
.stFileUploader>div:hover{border-color:rgba(99,102,241,.25)!important;background:rgba(99,102,241,.03)}
.stSelectbox>div>div{border-radius:10px}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(99,102,241,.2);border-radius:3px}::-webkit-scrollbar-thumb:hover{background:rgba(99,102,241,.4)}
</style>
<div class="stars-container"><div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div></div>
"""


def inject_css():
    """CSS'i Streamlit'e enjekte eder."""
    import streamlit as st

    st.markdown(CSS, unsafe_allow_html=True)
