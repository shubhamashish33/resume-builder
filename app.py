import streamlit as st
from datetime import date
from jinja2 import Template
import base64
import json
import os

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Resume Builder", layout="wide")

# ─── Default Resume Data (Pre-filled from Shubham's resume) ─────────────────
DEFAULT_RESUME = {
    "meta": {
        "template": "classic",
        "accent_color": "#2563eb",
        "font_family": "Inter",
        "spacing": "normal",
        "ats_mode": False,
        "section_order": ["summary", "experience", "skills", "projects", "education"]
    },
    "personal": {
        "name": "Shubham Ashish",
        "title": "Full-Stack Software Engineer",
        "email": "shubhamashish8@gmail.com",
        "phone": "+91-7903632459",
        "location": "Bangalore",
        "linkedin": "https://linkedin.com/in/shubhamashish",
        "github": "https://github.com/shubhamashish",
        "website": ""
    },
    "summary": "Full-Stack Software Engineer with 2+ years of production experience building enterprise-grade fintech applications for banking platforms. Strong proficiency in Angular 14+, TypeScript, and NgRx state management. Hands-on backend experience with Java Spring Boot in production fintech environments including bug resolution and codebase refactoring. Skilled in designing end-to-end features across frontend, backend, and database layers.",
    "experience": [
        {
            "role": "Software Engineer - FinTech Product Team",
            "company": "Tata Consultancy Services",
            "location": "Bangalore",
            "start_date": "2023-12-01",
            "end_date": "",
            "current": True,
            "bullets": [
                "Designed and implemented scalable Angular architecture using NgRx, lazy loading, and micro-frontends to support independent team deployments.",
                "Reduced dashboard load time from 4.2s → 1.8s by optimizing component lifecycle, routing strategy, and bundle splitting.",
                "Built centralized caching and state orchestration layer using NgRx Effects, cutting redundant API calls by 65%.",
                "Improved rendering performance on large datasets using OnPush change detection, memoized selectors, and virtualized views.",
                "Led development of ICICI Auto Loans module, implementing compliance-driven workflows with dynamic validations.",
                "Established unit testing standards, achieving 85%+ coverage across core modules.",
                "Led migration of 15–20 internal libraries from Angular 8 to Angular 20, adopting standalone components and modern build tooling.",
                "Developing an AI-powered policy assistant for banking clients using RAG — ingesting compliance and policy PDFs into a vector store."
            ]
        }
    ],
    "education": [
        {
            "institution": "G.H. Raisoni College of Engineering",
            "degree": "B.Tech",
            "field": "Computer Science & Engineering",
            "grade": "82.3%",
            "start_date": "2019-08-01",
            "end_date": "2023-05-01",
            "current": False
        }
    ],
    "skills": [
        {"category": "Languages", "tags": ["TypeScript", "JavaScript", "Java", "Python"]},
        {"category": "Frontend", "tags": ["Angular 14+", "React", "NgRx", "RxJS", "HTML5", "CSS3"]},
        {"category": "Backend", "tags": ["Node.js", "Express.js", "Java Spring Boot"]},
        {"category": "Databases", "tags": ["MySQL", "MongoDB"]},
        {"category": "Tools", "tags": ["Git", "Jenkins", "GitLab", "Postman"]},
        {"category": "AI / GenAI", "tags": ["RAG", "Vector Search", "LLM Integration"]}
    ],
    "projects": [
        {
            "name": "Splitz: Expense Sharing Platform",
            "description": "Complex Angular SPA with authentication, dynamic calculation flows, and modern standalone architecture.",
            "link": "",
            "tech_stack": ["Angular", "TypeScript", ".NET", "PostgreSQL"],
            "bullets": [
                "Built Angular 20 application using standalone components, route-level lazy loading, and functional guards/interceptors.",
                "Implemented reactive form systems with nested controls and custom validators for multi-user expense split logic.",
                "Designed service-driven state management using RxJS BehaviorSubject for auth/session synchronization.",
                "Integrated JWT + Google OAuth authentication with HTTP interceptors and token lifecycle handling.",
                "Enabled PWA capabilities with Angular Service Worker, caching strategies, and offline-ready app shell."
            ]
        },
        {
            "name": "JSON Comparator: Advanced Diff Tool",
            "description": "High-performance JSON comparison tool with interactive tree visualization for nested object analysis.",
            "link": "",
            "tech_stack": ["React", "TypeScript"],
            "bullets": [
                "Engineered custom deep-diff algorithm handling arrays, objects, and primitives at unlimited nesting depth.",
                "Optimized rendering using React.memo, useCallback, useMemo reducing memory overhead during large file comparisons.",
                "Implemented 500ms debounced search across diff results with clickable navigation and auto-expand functionality.",
                "Built intuitive UI with drag-and-drop file upload, JSON validation, and color-coded diff highlighting."
            ]
        },
        {
            "name": "NexChat: Real-Time Messaging Application",
            "description": "Full-stack chat application with real-time bidirectional communication and persistent message storage.",
            "link": "",
            "tech_stack": ["React", "Node.js", "Express", "MongoDB", "Socket.IO"],
            "bullets": [
                "Built WebSocket server with Socket.IO for concurrent connections using room-based architecture.",
                "Designed MongoDB schema with compound indexing for conversation queries and message history retrieval.",
                "Implemented authentication flow with JWT tokens and secure session management.",
                "Created message delivery pipeline tracking statuses (sent → delivered → read) with real-time UI synchronization."
            ]
        }
    ],
    "certifications": [],
    "languages": [],
    "volunteering": []
}

# ─── Session State Init ──────────────────────────────────────────────────────
if "resume" not in st.session_state:
    st.session_state.resume = json.loads(json.dumps(DEFAULT_RESUME))

# ─── Helper: Format Date ─────────────────────────────────────────────────────
def fmt_date(iso_str):
    if not iso_str:
        return ""
    try:
        return date.fromisoformat(iso_str).strftime("%b %Y")
    except:
        return iso_str

def date_input_field(label, key, stored_val):
    val = date.fromisoformat(stored_val) if stored_val else date.today()
    picked = st.date_input(label, value=val, key=key, format="MM/DD/YYYY")
    return picked.isoformat()

# ─── HTML TEMPLATE ───────────────────────────────────────────────────────────
RESUME_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family={{ font_family | replace(' ', '+') }}:wght@300;400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: '{{ font_family }}', sans-serif;
    font-size: {% if spacing == 'compact' %}12px{% elif spacing == 'spacious' %}14px{% else %}13px{% endif %};
    color: #1a1a2e;
    line-height: {% if spacing == 'compact' %}1.4{% elif spacing == 'spacious' %}1.8{% else %}1.6{% endif %};
    padding: {% if spacing == 'compact' %}28px 36px{% elif spacing == 'spacious' %}44px 52px{% else %}36px 44px{% endif %};
  }

  /* ── Header ── */
  .header { margin-bottom: 14px; }
  .header h1 {
    font-size: 26px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.3px;
  }
  .header .title {
    font-size: 14px;
    color: {{ accent_color }};
    font-weight: 500;
    margin-top: 2px;
  }
  .contact-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
    margin-top: 8px;
    font-size: 12px;
    color: #475569;
  }
  .contact-row a { color: #475569; text-decoration: none; }
  .contact-row span::before { content: ""; }

  /* ── Divider ── */
  .section-divider {
    border: none;
    border-top: 1.5px solid {{ accent_color }};
    margin: 12px 0 8px 0;
    opacity: 0.25;
  }

  /* ── Section ── */
  .section { margin-bottom: {% if spacing == 'compact' %}10px{% elif spacing == 'spacious' %}20px{% else %}14px{% endif %}; }
  .section-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: {{ accent_color }};
    margin-bottom: 6px;
    padding-bottom: 3px;
    border-bottom: 1.5px solid {{ accent_color }};
  }

  /* ── Experience / Project Entry ── */
  .entry { margin-bottom: {% if spacing == 'compact' %}7px{% elif spacing == 'spacious' %}14px{% else %}10px{% endif %}; }
  .entry-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }
  .entry-title {
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
  }
  .entry-date {
    font-size: 11px;
    color: #64748b;
    white-space: nowrap;
  }
  .entry-sub {
    font-size: 12px;
    color: #475569;
    margin-top: 1px;
  }
  .entry-sub .company { font-weight: 500; }

  /* ── Bullets ── */
  ul.bullets {
    margin: 4px 0 0 14px;
    padding: 0;
  }
  ul.bullets li {
    font-size: 12px;
    color: #334155;
    margin-bottom: 2px;
    line-height: 1.5;
  }

  /* ── Skills ── */
  .skills-grid { display: flex; flex-direction: column; gap: 3px; }
  .skill-row { display: flex; gap: 6px; font-size: 12px; }
  .skill-cat { font-weight: 600; color: #0f172a; min-width: 90px; }
  .skill-items { color: #334155; }

  /* ── Education ── */
  .edu-entry { margin-bottom: 6px; }

  /* ── Tech tags ── */
  .tech-stack { margin-top: 3px; display: flex; flex-wrap: wrap; gap: 4px; }
  .tech-tag {
    background: #f1f5f9;
    color: #475569;
    font-size: 10px;
    padding: 1px 7px;
    border-radius: 3px;
    font-weight: 500;
  }

  /* ── ATS overrides ── */
  {% if ats_mode %}
  .tech-tag { background: none; padding: 0; }
  .tech-tag::after { content: ", "; }
  .tech-tag:last-child::after { content: ""; }
  {% endif %}

  /* ── Summary ── */
  .summary-text { font-size: 12.5px; color: #334155; line-height: 1.65; }
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <h1>{{ personal.name }}</h1>
  {% if personal.title %}<div class="title">{{ personal.title }}</div>{% endif %}
  <div class="contact-row">
    {% if personal.location %}<span>📍 {{ personal.location }}</span>{% endif %}
    {% if personal.email %}<span><a href="mailto:{{ personal.email }}">{{ personal.email }}</a></span>{% endif %}
    {% if personal.phone %}<span>{{ personal.phone }}</span>{% endif %}
    {% if personal.linkedin %}<span><a href="{{ personal.linkedin }}">LinkedIn ↗</a></span>{% endif %}
    {% if personal.github %}<span><a href="{{ personal.github }}">Github ↗</a></span>{% endif %}
    {% if personal.website %}<span><a href="{{ personal.website }}">{{ personal.website }}</a></span>{% endif %}
  </div>
</div>

{% for section in section_order %}

  {% if section == 'summary' and summary %}
  <div class="section">
    <div class="section-title">Summary</div>
    <p class="summary-text">{{ summary }}</p>
  </div>
  {% endif %}

  {% if section == 'experience' and experience %}
  <div class="section">
    <div class="section-title">Professional Experience</div>
    {% for exp in experience %}
    <div class="entry">
      <div class="entry-header">
        <div class="entry-title">{{ exp.company }}</div>
        <div class="entry-date">
          {{ exp.start_date | fmt_date }}{% if exp.current %} – Present{% elif exp.end_date %} – {{ exp.end_date | fmt_date }}{% endif %}
        </div>
      </div>
      <div class="entry-sub">
        <span class="company">{{ exp.role }}</span>
        {% if exp.location %} · {{ exp.location }}{% endif %}
      </div>
      {% if exp.bullets %}
      <ul class="bullets">
        {% for b in exp.bullets %}<li>{{ b }}</li>{% endfor %}
      </ul>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if section == 'skills' and skills %}
  <div class="section">
    <div class="section-title">Skills</div>
    <div class="skills-grid">
      {% for s in skills %}
      <div class="skill-row">
        <span class="skill-cat">{{ s.category }} —</span>
        <span class="skill-items">{{ s.tags | join(', ') }}</span>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if section == 'projects' and projects %}
  <div class="section">
    <div class="section-title">Technical Projects</div>
    {% for p in projects %}
    <div class="entry">
      <div class="entry-header">
        <div class="entry-title">{{ p.name }}</div>
      </div>
      {% if p.tech_stack %}
      <div class="tech-stack">
        {% for t in p.tech_stack %}<span class="tech-tag">{{ t }}</span>{% endfor %}
      </div>
      {% endif %}
      {% if p.bullets %}
      <ul class="bullets">
        {% for b in p.bullets %}<li>{{ b }}</li>{% endfor %}
      </ul>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if section == 'education' and education %}
  <div class="section">
    <div class="section-title">Education</div>
    {% for edu in education %}
    <div class="edu-entry">
      <div class="entry-header">
        <div class="entry-title">{{ edu.degree }}{% if edu.field %} in {{ edu.field }}{% endif %}</div>
        <div class="entry-date">
          {{ edu.start_date | fmt_date }}{% if edu.current %} – Present{% elif edu.end_date %} – {{ edu.end_date | fmt_date }}{% endif %}
        </div>
      </div>
      <div class="entry-sub">
        {{ edu.institution }}{% if edu.grade %} · {{ edu.grade }}{% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if section == 'certifications' and certifications %}
  <div class="section">
    <div class="section-title">Certifications</div>
    {% for c in certifications %}
    <div class="entry">
      <div class="entry-header">
        <div class="entry-title">{{ c.name }}</div>
        <div class="entry-date">{{ c.date }}</div>
      </div>
      {% if c.issuer %}<div class="entry-sub">{{ c.issuer }}</div>{% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if section == 'languages' and languages %}
  <div class="section">
    <div class="section-title">Languages</div>
    <div class="skills-grid">
      {% for l in languages %}
      <div class="skill-row">
        <span class="skill-cat">{{ l.language }}</span>
        <span class="skill-items">{{ l.proficiency }}</span>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  {% if section == 'volunteering' and volunteering %}
  <div class="section">
    <div class="section-title">Volunteering</div>
    {% for v in volunteering %}
    <div class="entry">
      <div class="entry-header">
        <div class="entry-title">{{ v.role }} — {{ v.org }}</div>
        <div class="entry-date">{{ v.date }}</div>
      </div>
      {% if v.description %}<div class="entry-sub">{{ v.description }}</div>{% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}

{% endfor %}

</body>
</html>
"""

# ─── Render HTML ─────────────────────────────────────────────────────────────
def render_html(resume):
    from jinja2 import Environment
    env = Environment()
    env.filters["fmt_date"] = fmt_date
    tmpl = env.from_string(RESUME_HTML)
    meta = resume["meta"]
    return tmpl.render(
        personal=resume["personal"],
        summary=resume["summary"],
        experience=resume["experience"],
        education=resume["education"],
        skills=resume["skills"],
        projects=resume["projects"],
        certifications=resume["certifications"],
        languages=resume["languages"],
        volunteering=resume["volunteering"],
        section_order=meta["section_order"],
        accent_color=meta["accent_color"],
        font_family=meta["font_family"],
        spacing=meta["spacing"],
        ats_mode=meta["ats_mode"]
    )

# ─── Generate PDF ─────────────────────────────────────────────────────────────
def generate_pdf(html_content):
    import pdfkit

    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": "",
        "margin-top": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "margin-right": "0mm",
        "disable-smart-shrinking": "",
        "zoom": "1.0"
    }

    return pdfkit.from_string(html_content, False, options=options, configuration=config)

# ════════════════════════════════════════════════════════════════════════════
#  UI
# ════════════════════════════════════════════════════════════════════════════

st.title("📄 Resume Builder")

left_col, right_col = st.columns([1, 1])

r = st.session_state.resume

# ══════════════════════════════
#  LEFT COLUMN — EDITOR
# ══════════════════════════════
with left_col:

    # ── Customization Bar ──────────────────────────────────────────────────
    with st.expander("🎨 Customization", expanded=False):
        meta = r["meta"]
        meta["accent_color"] = st.color_picker("Accent Color", value=meta["accent_color"], key="meta_color")
        meta["font_family"]  = st.selectbox("Font", ["Inter", "Georgia", "Roboto", "Lato", "Merriweather"], key="meta_font",
                                             index=["Inter", "Georgia", "Roboto", "Lato", "Merriweather"].index(meta["font_family"]))
        meta["spacing"]      = st.select_slider("Spacing", options=["compact", "normal", "spacious"], value=meta["spacing"], key="meta_spacing")
        meta["ats_mode"]     = st.checkbox("ATS Friendly Mode", value=meta["ats_mode"], key="meta_ats")

        st.markdown("**Section Order** (edit the list to reorder)")
        all_sections = ["summary", "experience", "skills", "projects", "education", "certifications", "languages", "volunteering"]
        for idx, sec in enumerate(meta["section_order"]):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"`{sec}`")
            if c2.button("▲", key=f"ord_up_{idx}") and idx > 0:
                meta["section_order"][idx], meta["section_order"][idx-1] = meta["section_order"][idx-1], meta["section_order"][idx]
                st.rerun()
            if c3.button("▼", key=f"ord_dn_{idx}") and idx < len(meta["section_order"]) - 1:
                meta["section_order"][idx], meta["section_order"][idx+1] = meta["section_order"][idx+1], meta["section_order"][idx]
                st.rerun()

    # ── Personal Info ──────────────────────────────────────────────────────
    with st.expander("👤 Personal Info", expanded=True):
        p = r["personal"]
        p["name"]     = st.text_input("Full Name",     value=p["name"],     key="p_name")
        p["title"]    = st.text_input("Job Title",     value=p["title"],    key="p_title")
        col1, col2   = st.columns(2)
        p["email"]    = col1.text_input("Email",       value=p["email"],    key="p_email")
        p["phone"]    = col2.text_input("Phone",       value=p["phone"],    key="p_phone")
        p["location"] = st.text_input("Location",      value=p["location"], key="p_location")
        col3, col4   = st.columns(2)
        p["linkedin"] = col3.text_input("LinkedIn URL", value=p["linkedin"], key="p_linkedin")
        p["github"]   = col4.text_input("GitHub URL",   value=p["github"],   key="p_github")
        p["website"]  = st.text_input("Website",        value=p["website"],  key="p_website")

    # ── Summary ────────────────────────────────────────────────────────────
    with st.expander("📝 Summary", expanded=False):
        r["summary"] = st.text_area("Professional Summary", value=r["summary"], height=130, key="summary", placeholder="Write a short 2-3 line summary...")

    # ── Experience ─────────────────────────────────────────────────────────
    with st.expander("💼 Work Experience", expanded=False):
        for i, exp in enumerate(r["experience"]):
            st.markdown(f"**Entry {i+1}** — {exp['company'] or 'New Entry'}")
            exp["role"]    = st.text_input("Job Title", value=exp["role"],    key=f"exp_{i}_role")
            exp["company"] = st.text_input("Company",   value=exp["company"], key=f"exp_{i}_company")
            exp["location"]= st.text_input("Location",  value=exp["location"],key=f"exp_{i}_location")

            col1, col2 = st.columns(2)
            exp["start_date"] = date_input_field("Start Date", f"exp_{i}_start", exp["start_date"])
            exp["current"]    = st.checkbox("Currently working here", value=exp["current"], key=f"exp_{i}_current")
            if not exp["current"]:
                exp["end_date"] = date_input_field("End Date", f"exp_{i}_end", exp["end_date"] or exp["start_date"])

            bullets_text = st.text_area("Responsibilities (one per line)", value="\n".join(exp["bullets"]), key=f"exp_{i}_bullets", height=150)
            exp["bullets"] = [l for l in bullets_text.split("\n") if l.strip()]

            if st.button("🗑 Remove Entry", key=f"exp_{i}_remove"):
                r["experience"].pop(i); st.rerun()
            st.markdown("---")

        if st.button("＋ Add Experience", key="add_exp"):
            r["experience"].append({"role":"","company":"","location":"","start_date":"","end_date":"","current":False,"bullets":[]})
            st.rerun()

    # ── Education ──────────────────────────────────────────────────────────
    with st.expander("🎓 Education", expanded=False):
        for i, edu in enumerate(r["education"]):
            st.markdown(f"**Entry {i+1}** — {edu['institution'] or 'New Entry'}")
            edu["institution"] = st.text_input("Institution",    value=edu["institution"], key=f"edu_{i}_inst")
            edu["degree"]      = st.text_input("Degree",         value=edu["degree"],      key=f"edu_{i}_deg")
            edu["field"]       = st.text_input("Field of Study",  value=edu["field"],       key=f"edu_{i}_field")
            edu["grade"]       = st.text_input("Grade / GPA",     value=edu["grade"],       key=f"edu_{i}_grade")
            edu["start_date"]  = date_input_field("Start Date",  f"edu_{i}_start", edu["start_date"])
            edu["current"]     = st.checkbox("Currently studying", value=edu["current"],    key=f"edu_{i}_current")
            if not edu["current"]:
                edu["end_date"] = date_input_field("End Date",   f"edu_{i}_end", edu["end_date"] or edu["start_date"])

            if st.button("🗑 Remove", key=f"edu_{i}_remove"):
                r["education"].pop(i); st.rerun()
            st.markdown("---")

        if st.button("＋ Add Education", key="add_edu"):
            r["education"].append({"institution":"","degree":"","field":"","grade":"","start_date":"","end_date":"","current":False})
            st.rerun()

    # ── Skills ─────────────────────────────────────────────────────────────
    with st.expander("🛠 Skills", expanded=False):
        for i, sk in enumerate(r["skills"]):
            if "tags" not in sk or not isinstance(sk["tags"], list):
                sk["tags"] = []
            col1, col2 = st.columns([1, 2])
            sk["category"] = col1.text_input("Category", value=sk["category"], key=f"sk_{i}_cat")
            items_text  = col2.text_input("Items (comma separated)", value=", ".join(sk.get("tags", [])), key=f"sk_{i}_tags")
            sk["tags"] = [x.strip() for x in items_text.split(",") if x.strip()]
            if st.button("🗑 Remove", key=f"sk_{i}_remove"):
                r["skills"].pop(i); st.rerun()

        if st.button("＋ Add Skill Category", key="add_skill"):
            r["skills"].append({"category":"","tags":[]})
            st.rerun()

    # ── Projects ───────────────────────────────────────────────────────────
    with st.expander("🚀 Projects", expanded=False):
        for i, proj in enumerate(r["projects"]):
            st.markdown(f"**Project {i+1}** — {proj['name'] or 'New Project'}")
            proj["name"]        = st.text_input("Project Name", value=proj["name"],  key=f"pr_{i}_name")
            proj["link"]        = st.text_input("Link (optional)", value=proj["link"], key=f"pr_{i}_link")
            tech_text           = st.text_input("Tech Stack (comma separated)", value=", ".join(proj["tech_stack"]), key=f"pr_{i}_tech")
            proj["tech_stack"]  = [x.strip() for x in tech_text.split(",") if x.strip()]
            bullets_text        = st.text_area("Details (one per line)", value="\n".join(proj["bullets"]), key=f"pr_{i}_bullets", height=120)
            proj["bullets"]     = [l for l in bullets_text.split("\n") if l.strip()]

            if st.button("🗑 Remove", key=f"pr_{i}_remove"):
                r["projects"].pop(i); st.rerun()
            st.markdown("---")

        if st.button("＋ Add Project", key="add_proj"):
            r["projects"].append({"name":"","description":"","link":"","tech_stack":[],"bullets":[]})
            st.rerun()

    # ── Certifications ─────────────────────────────────────────────────────
    with st.expander("📜 Certifications", expanded=False):
        for i, cert in enumerate(r["certifications"]):
            cert["name"]   = st.text_input("Certification Name", value=cert["name"],   key=f"cert_{i}_name")
            cert["issuer"] = st.text_input("Issuer",             value=cert["issuer"], key=f"cert_{i}_issuer")
            cert["date"]   = st.text_input("Date (e.g. Jan 2024)", value=cert["date"], key=f"cert_{i}_date")
            if st.button("🗑 Remove", key=f"cert_{i}_remove"):
                r["certifications"].pop(i); st.rerun()
            st.markdown("---")

        if st.button("＋ Add Certification", key="add_cert"):
            r["certifications"].append({"name":"","issuer":"","date":""})
            st.rerun()

    # ── Languages ──────────────────────────────────────────────────────────
    with st.expander("🌐 Languages", expanded=False):
        for i, lang in enumerate(r["languages"]):
            col1, col2 = st.columns(2)
            lang["language"]    = col1.text_input("Language",    value=lang["language"],    key=f"lang_{i}_lang")
            lang["proficiency"] = col2.text_input("Proficiency", value=lang["proficiency"], key=f"lang_{i}_prof")
            if st.button("🗑 Remove", key=f"lang_{i}_remove"):
                r["languages"].pop(i); st.rerun()

        if st.button("＋ Add Language", key="add_lang"):
            r["languages"].append({"language":"","proficiency":""})
            st.rerun()

    # ── Volunteering ───────────────────────────────────────────────────────
    with st.expander("🤝 Volunteering", expanded=False):
        for i, vol in enumerate(r["volunteering"]):
            vol["org"]         = st.text_input("Organization", value=vol["org"],         key=f"vol_{i}_org")
            vol["role"]        = st.text_input("Role",         value=vol["role"],         key=f"vol_{i}_role")
            vol["date"]        = st.text_input("Date",         value=vol["date"],         key=f"vol_{i}_date")
            vol["description"] = st.text_area("Description",   value=vol["description"],  key=f"vol_{i}_desc", height=80)
            if st.button("🗑 Remove", key=f"vol_{i}_remove"):
                r["volunteering"].pop(i); st.rerun()
            st.markdown("---")

        if st.button("＋ Add Volunteering", key="add_vol"):
            r["volunteering"].append({"org":"","role":"","date":"","description":""})
            st.rerun()

    # ── Reset ──────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🔄 Reset to Default", key="reset"):
        st.session_state.resume = json.loads(json.dumps(DEFAULT_RESUME))
        st.rerun()

# ══════════════════════════════
#  RIGHT COLUMN — PREVIEW + EXPORT
# ══════════════════════════════
with right_col:
    st.subheader("Preview")

    html_output = render_html(r)

    # Live HTML preview via iframe
    encoded = base64.b64encode(html_output.encode()).decode()
    iframe_html = f"""
    <iframe
        src="data:text/html;base64,{encoded}"
        width="100%"
        height="900"
        style="border: 1px solid #e2e8f0; border-radius: 8px;"
        scrolling="yes">
    </iframe>
    """
    st.components.v1.html(iframe_html, height=920, scrolling=False)

    st.markdown("---")

    # ── Export ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬇️ Export PDF", key="export_pdf", use_container_width=True):
            with st.spinner("Generating PDF..."):
                try:
                    pdf_bytes = generate_pdf(html_output)
                    name = r["personal"]["name"].replace(" ", "_") or "resume"
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_bytes,
                        file_name=f"{name}_resume.pdf",
                        mime="application/pdf",
                        key="dl_pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    with col2:
        resume_json = json.dumps(r, indent=2)
        st.download_button(
            label="💾 Save as JSON",
            data=resume_json,
            file_name="resume.json",
            mime="application/json",
            key="dl_json",
            use_container_width=True
        )