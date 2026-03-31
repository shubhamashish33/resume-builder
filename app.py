import base64
import json
import os
import re
import shutil
import zlib
from datetime import date

import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Environment

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
        "section_order": ["summary", "experience", "skills", "projects", "education", "certifications", "languages", "volunteering"],
        "hidden_sections": []
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

SECTION_LABELS = {
    "summary": "Summary",
    "experience": "Experience",
    "skills": "Skills",
    "projects": "Projects",
    "education": "Education",
    "certifications": "Certifications",
    "languages": "Languages",
    "volunteering": "Volunteering",
}

FONT_OPTIONS = ["Inter", "Georgia", "Roboto", "Lato", "Merriweather", "Poppins", "Source Sans 3"]
COOKIE_PREFIX = "resume_builder_state_"
COOKIE_CHUNK_SIZE = 3200
COOKIE_CHUNK_COUNT = 12


def clone_resume(data):
    return json.loads(json.dumps(data))


def normalize_resume(data):
    resume = clone_resume(DEFAULT_RESUME)
    if isinstance(data, dict):
        if isinstance(data.get("meta"), dict):
            resume["meta"].update(data["meta"])
        if isinstance(data.get("personal"), dict):
            resume["personal"].update(data["personal"])
        for key in ["summary", "experience", "education", "skills", "projects", "certifications", "languages", "volunteering"]:
            if key in data:
                resume[key] = data[key]

    order = [sec for sec in resume["meta"].get("section_order", []) if sec in SECTION_LABELS]
    for sec in SECTION_LABELS:
        if sec not in order:
            order.append(sec)
    resume["meta"]["section_order"] = order
    resume["meta"]["hidden_sections"] = [sec for sec in resume["meta"].get("hidden_sections", []) if sec in SECTION_LABELS]
    if resume["meta"]["font_family"] not in FONT_OPTIONS:
        resume["meta"]["font_family"] = "Inter"
    if resume["meta"]["template"] not in ["classic", "sidebar", "minimal"]:
        resume["meta"]["template"] = "classic"
    if resume["meta"]["spacing"] not in ["compact", "normal", "spacious"]:
        resume["meta"]["spacing"] = "normal"
    return resume


def encode_resume(resume):
    payload = json.dumps(resume, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(zlib.compress(payload, 9)).decode("ascii")


def decode_resume(blob):
    data = zlib.decompress(base64.urlsafe_b64decode(blob.encode("ascii")))
    return normalize_resume(json.loads(data.decode("utf-8")))


def load_browser_resume():
    cookies = getattr(st.context, "cookies", {})
    chunks = []
    for index in range(COOKIE_CHUNK_COUNT):
        value = cookies.get(f"{COOKIE_PREFIX}{index}", "")
        if not value:
            break
        chunks.append(value)
    if not chunks:
        return None
    try:
        return decode_resume("".join(chunks))
    except Exception:
        return None


def persist_browser_resume(resume, clear=False):
    encoded = "" if clear else encode_resume(resume)
    parts = [encoded[i:i + COOKIE_CHUNK_SIZE] for i in range(0, len(encoded), COOKIE_CHUNK_SIZE)]
    script = [
        "<script>",
        "const root = window.parent.document;",
        f"const prefix = {json.dumps(COOKIE_PREFIX)};",
        f"const total = {COOKIE_CHUNK_COUNT};",
        f"const parts = {json.dumps(parts)};",
        "for (let i = 0; i < total; i += 1) {",
        "  if (parts[i]) {",
        "    root.cookie = `${prefix}${i}=${parts[i]}; path=/; max-age=31536000; SameSite=Lax`;",
        "  } else {",
        "    root.cookie = `${prefix}${i}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;",
        "  }",
        "}",
        "</script>",
    ]
    components.html("\n".join(script), height=0)


def parse_resume_text(text):
    resume = clone_resume(DEFAULT_RESUME)
    sections = {"personal": []}
    current = "personal"
    for raw_line in text.replace("\r\n", "\n").split("\n"):
        stripped = raw_line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip().lower()
            mapping = {
                "personal": "personal",
                "personal info": "personal",
                "summary": "summary",
                "profile": "summary",
                "experience": "experience",
                "work experience": "experience",
                "skills": "skills",
                "projects": "projects",
                "education": "education",
                "certifications": "certifications",
                "languages": "languages",
                "volunteering": "volunteering",
            }
            current = mapping.get(heading, current)
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw_line.rstrip())

    for line in sections.get("personal", []):
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key in resume["personal"]:
            resume["personal"][key] = value.strip()

    summary_lines = [line.strip() for line in sections.get("summary", []) if line.strip()]
    if summary_lines:
        resume["summary"] = " ".join(summary_lines)

    skills = []
    for line in sections.get("skills", []):
        item = line.lstrip("-* ").strip()
        if not item:
            continue
        if ":" in item:
            category, tags = item.split(":", 1)
            skills.append({"category": category.strip(), "tags": [x.strip() for x in tags.split(",") if x.strip()]})
        else:
            skills.append({"category": "Skills", "tags": [x.strip() for x in item.split(",") if x.strip()]})
    if skills:
        resume["skills"] = skills

    experience = []
    blocks = re.split(r"\n\s*\n", "\n".join(sections.get("experience", [])))
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        title = lines[0].lstrip("# ").strip()
        role, company = title, ""
        if " at " in title:
            role, company = [x.strip() for x in title.split(" at ", 1)]
        elif "|" in title:
            role, company = [x.strip() for x in title.split("|", 1)]
        bullets = [line.lstrip("-* ").strip() for line in lines[1:] if line.startswith(("-", "*"))]
        if role or company or bullets:
            experience.append({"role": role, "company": company, "location": "", "start_date": "", "end_date": "", "current": False, "bullets": bullets})
    if experience:
        resume["experience"] = experience

    projects = []
    blocks = re.split(r"\n\s*\n", "\n".join(sections.get("projects", [])))
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        name = lines[0].lstrip("# ").strip()
        bullets = [line.lstrip("-* ").strip() for line in lines[1:] if line.startswith(("-", "*"))]
        description = next((line for line in lines[1:] if not line.startswith(("-", "*"))), "")
        projects.append({"name": name, "description": description, "link": "", "tech_stack": [], "bullets": bullets})
    if projects:
        resume["projects"] = projects

    return normalize_resume(resume)


def import_resume_text(file_name, text):
    if file_name.lower().endswith(".json"):
        return normalize_resume(json.loads(text))
    return parse_resume_text(text)


def get_wkhtmltopdf_path():
    candidates = [
        shutil.which("wkhtmltopdf"),
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return None


if "resume" not in st.session_state:
    st.session_state.resume = load_browser_resume() or clone_resume(DEFAULT_RESUME)
if "raw_import_text" not in st.session_state:
    st.session_state.raw_import_text = ""
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

st.session_state.resume = normalize_resume(st.session_state.resume)

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
  @page { size: A4; margin: 4mm; }
  @import url('https://fonts.googleapis.com/css2?family={{ font_family | replace(' ', '+') }}:wght@300;400;500;600;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: '{{ font_family }}', sans-serif;
    font-size: {% if spacing == 'compact' %}11.5px{% elif spacing == 'spacious' %}13.5px{% else %}12.5px{% endif %};
    line-height: {% if spacing == 'compact' %}1.45{% elif spacing == 'spacious' %}1.75{% else %}1.6{% endif %};
    color: #0f172a;
    background: #ffffff;
    padding: 0;
  }
  .resume-shell {
    max-width: 100%;
    margin: 0 auto;
    background: #fff;
    border-radius: 0;
    box-shadow: none;
    border-top: {% if template == 'minimal' and not ats_mode %}7px solid {{ accent_color }}{% else %}none{% endif %};
    padding: {% if spacing == 'compact' %}14px 16px{% elif spacing == 'spacious' %}24px 26px{% else %}18px 20px{% endif %};
  }
  .header { margin-bottom: 18px; {% if template == 'minimal' %}padding-bottom:18px;border-bottom:1px solid rgba(15,23,42,0.08);{% endif %} }
  .header-top { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; }
  h1 { font-size: {% if template == 'minimal' %}34px{% else %}30px{% endif %}; line-height: 1; letter-spacing: -0.03em; }
  .title { margin-top: 6px; color: {% if ats_mode %}#0f172a{% else %}{{ accent_color }}{% endif %}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-size: 13px; }
  .contact-row { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px 10px; max-width: {% if template == 'sidebar' %}44%{% else %}48%{% endif %}; }
  .contact-row span, .contact-row a {
    color: #475569;
    text-decoration: none;
    font-size: 11px;
    {% if not ats_mode %}background: #f8fafc; border-radius: 999px; padding: 6px 10px;{% endif %}
  }
  .layout { {% if template == 'sidebar' and not ats_mode %}display:grid;grid-template-columns:minmax(0,1.85fr) minmax(220px,.95fr);gap:24px;{% endif %} }
  .sidebar { {% if template == 'sidebar' and not ats_mode %}background: rgba(37,99,235,0.05);border:1px solid rgba(37,99,235,0.12);border-radius:18px;padding:18px;{% endif %} }
  .section { margin-bottom: {% if spacing == 'compact' %}10px{% elif spacing == 'spacious' %}18px{% else %}13px{% endif %}; break-inside: avoid; page-break-inside: avoid; }
  .section-title {
    font-size: {% if template == 'minimal' %}12px{% else %}11px{% endif %};
    color: {% if ats_mode %}#0f172a{% else %}{{ accent_color }}{% endif %};
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: {% if template == 'minimal' %}0.18em{% else %}0.14em{% endif %};
    margin-bottom: 8px;
    {% if template != 'minimal' %}padding-bottom: 5px; border-bottom: 1px solid rgba(37,99,235,0.18);{% endif %}
  }
  .entry { margin-bottom: 12px; }
  .entry-header { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
  .entry-title { font-size: 13px; font-weight: 700; }
  .entry-sub, .entry-desc { color: #475569; margin-top: 3px; }
  .entry-date { color: #64748b; font-size: 11px; white-space: nowrap; }
  ul.bullets { margin: 7px 0 0 18px; color: #334155; }
  ul.bullets li { margin-bottom: 3px; }
  .skills-grid { display: grid; gap: 8px; }
  .skill-row { display:grid; grid-template-columns:minmax(120px,150px) 1fr; gap: 14px; align-items: start; }
  .skill-cat { font-weight: 700; }
  .skill-items { color: #334155; }
  .tech-stack { margin-top: 6px; display:flex; flex-wrap:wrap; gap:6px; }
  .tech-tag {
    {% if ats_mode %}padding:0;background:none;color:#334155;{% else %}padding:4px 9px;background:rgba(37,99,235,0.08);color:{{ accent_color }};border-radius:999px;{% endif %}
    font-size: 10px;
    font-weight: 700;
  }
  {% if ats_mode %}
  .tech-tag::after { content: ", "; }
  .tech-tag:last-child::after { content: ""; }
  {% endif %}
</style>
</head>
<body>
<div class="resume-shell">
  <div class="header">
    <div class="header-top">
      <div>
        <h1>{{ personal.name }}</h1>
        {% if personal.title %}<div class="title">{{ personal.title }}</div>{% endif %}
      </div>
      <div class="contact-row">
        {% if personal.location %}<span>{{ personal.location }}</span>{% endif %}
        {% if personal.email %}<a href="mailto:{{ personal.email }}">{{ personal.email }}</a>{% endif %}
        {% if personal.phone %}<span>{{ personal.phone }}</span>{% endif %}
        {% if personal.linkedin %}<a href="{{ personal.linkedin }}">LinkedIn</a>{% endif %}
        {% if personal.github %}<a href="{{ personal.github }}">GitHub</a>{% endif %}
        {% if personal.website %}<a href="{{ personal.website }}">{{ personal.website }}</a>{% endif %}
      </div>
    </div>
  </div>
  {% if template == 'sidebar' and not ats_mode %}
  <div class="layout">
    <div>
      {% for section in main_sections %}{{ section | safe }}{% endfor %}
    </div>
    <div class="sidebar">
      {% for section in side_sections %}{{ section | safe }}{% endfor %}
    </div>
  </div>
  {% else %}
  <div>{% for section in flat_sections %}{{ section | safe }}{% endfor %}</div>
  {% endif %}
</div>
</body>
</html>
"""


def render_html(resume):
    env = Environment()
    env.filters["fmt_date"] = fmt_date
    meta = resume["meta"]
    sections = []
    for section in meta["section_order"]:
        if section in meta.get("hidden_sections", []):
            continue
        block = ""
        if section == "summary" and resume["summary"]:
            block = f'<div class="section"><div class="section-title">Summary</div><p>{resume["summary"]}</p></div>'
        elif section == "experience" and resume["experience"]:
            items = []
            for exp in resume["experience"]:
                date_text = fmt_date(exp["start_date"])
                if exp.get("current"):
                    date_text = f"{date_text} - Present" if date_text else "Present"
                elif exp.get("end_date"):
                    date_text = f"{date_text} - {fmt_date(exp['end_date'])}" if date_text else fmt_date(exp["end_date"])
                bullets = "".join(f"<li>{b}</li>" for b in exp.get("bullets", []))
                items.append(f'<div class="entry"><div class="entry-header"><div><div class="entry-title">{exp.get("role","")}</div><div class="entry-sub">{exp.get("company","")}{(" · " + exp.get("location","")) if exp.get("location") else ""}</div></div><div class="entry-date">{date_text}</div></div>{"<ul class=\"bullets\">" + bullets + "</ul>" if bullets else ""}</div>')
            block = f'<div class="section"><div class="section-title">Work Experience</div>{"".join(items)}</div>'
        elif section == "skills" and resume["skills"]:
            items = "".join(f'<div class="skill-row"><span class="skill-cat">{s.get("category","")}</span><span class="skill-items">{", ".join(s.get("tags", []))}</span></div>' for s in resume["skills"])
            block = f'<div class="section"><div class="section-title">Skills</div><div class="skills-grid">{items}</div></div>'
        elif section == "projects" and resume["projects"]:
            items = []
            for proj in resume["projects"]:
                tags = "".join(f'<span class="tech-tag">{tag}</span>' for tag in proj.get("tech_stack", []))
                bullets = "".join(f"<li>{b}</li>" for b in proj.get("bullets", []))
                desc = f'<div class="entry-desc">{proj.get("description","")}</div>' if proj.get("description") else ""
                items.append(f'<div class="entry"><div class="entry-title">{proj.get("name","")}</div>{desc}{"<div class=\"tech-stack\">" + tags + "</div>" if tags else ""}{"<ul class=\"bullets\">" + bullets + "</ul>" if bullets else ""}</div>')
            block = f'<div class="section"><div class="section-title">Projects</div>{"".join(items)}</div>'
        elif section == "education" and resume["education"]:
            items = []
            for edu in resume["education"]:
                date_text = fmt_date(edu["start_date"])
                if edu.get("current"):
                    date_text = f"{date_text} - Present" if date_text else "Present"
                elif edu.get("end_date"):
                    date_text = f"{date_text} - {fmt_date(edu['end_date'])}" if date_text else fmt_date(edu["end_date"])
                detail = " · ".join([part for part in [edu.get("institution", ""), edu.get("grade", "")] if part])
                items.append(f'<div class="entry"><div class="entry-header"><div class="entry-title">{edu.get("degree","")}{(" in " + edu.get("field","")) if edu.get("field") else ""}</div><div class="entry-date">{date_text}</div></div><div class="entry-sub">{detail}</div></div>')
            block = f'<div class="section"><div class="section-title">Education</div>{"".join(items)}</div>'
        elif section == "certifications" and resume["certifications"]:
            items = "".join(f'<div class="entry"><div class="entry-title">{c.get("name","")}</div><div class="entry-sub">{" · ".join([part for part in [c.get("issuer",""), c.get("date","")] if part])}</div></div>' for c in resume["certifications"])
            block = f'<div class="section"><div class="section-title">Certifications</div>{items}</div>'
        elif section == "languages" and resume["languages"]:
            items = "".join(f'<div class="skill-row"><span class="skill-cat">{l.get("language","")}</span><span class="skill-items">{l.get("proficiency","")}</span></div>' for l in resume["languages"])
            block = f'<div class="section"><div class="section-title">Languages</div><div class="skills-grid">{items}</div></div>'
        elif section == "volunteering" and resume["volunteering"]:
            items = "".join(f'<div class="entry"><div class="entry-title">{v.get("role","")}{(" - " + v.get("org","")) if v.get("org") else ""}</div><div class="entry-sub">{" · ".join([part for part in [v.get("date",""), v.get("description","")] if part])}</div></div>' for v in resume["volunteering"])
            block = f'<div class="section"><div class="section-title">Volunteering</div>{items}</div>'
        if block:
            sections.append((section, block))

    sidebar_keys = {"skills", "education", "certifications", "languages", "volunteering"}
    flat_sections = [html for _, html in sections]
    main_sections = [html for key, html in sections if key not in sidebar_keys]
    side_sections = [html for key, html in sections if key in sidebar_keys]
    return env.from_string(RESUME_HTML).render(
        personal=resume["personal"],
        accent_color=meta["accent_color"],
        font_family=meta["font_family"],
        spacing=meta["spacing"],
        ats_mode=meta["ats_mode"],
        template=meta["template"],
        flat_sections=flat_sections,
        main_sections=main_sections,
        side_sections=side_sections,
    )

# ─── Generate PDF ─────────────────────────────────────────────────────────────
def generate_pdf(html_content):
    import pdfkit

    wkhtmltopdf = get_wkhtmltopdf_path()
    if not wkhtmltopdf:
        raise RuntimeError("wkhtmltopdf was not found on this machine.")
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf)

    options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": "",
        "margin-top": "3mm",
        "margin-bottom": "3mm",
        "margin-left": "3mm",
        "margin-right": "3mm",
        "disable-smart-shrinking": "",
        "zoom": "1.0"
    }

    return pdfkit.from_string(html_content, False, options=options, configuration=config)

# ════════════════════════════════════════════════════════════════════════════
#  UI
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top left, rgba(37,99,235,.12), transparent 30%), linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%); }
.hero-card { background: rgba(255,255,255,.82); border: 1px solid rgba(148,163,184,.2); border-radius: 22px; padding: 18px 20px; box-shadow: 0 18px 50px rgba(15,23,42,.08); margin-bottom: 14px; }
.hero-card h1 { font-size: 2rem; line-height: 1.05; margin-bottom: 6px; }
.hero-card p { color: #475569; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

r = st.session_state.resume
persist_browser_resume(r)

visible_sections = [sec for sec in r["meta"]["section_order"] if sec not in r["meta"].get("hidden_sections", [])]
completion = sum([
    bool(r["personal"]["name"]),
    bool(r["personal"]["email"]),
    bool(r["personal"]["title"]),
    bool(r["summary"]),
    bool(r["experience"]),
    bool(r["skills"]),
    bool(r["education"]),
    bool(r["projects"]),
]) * 100 // 8

st.markdown(f"""
<div class="hero-card">
  <h1>Resume Builder</h1>
  <p>Import markdown or text, edit everything in-place, choose a distinct template, and export print-ready PDFs with a live preview.</p>
  <p style="margin-top:10px;"><strong>{completion}% complete</strong> · <strong>{len(visible_sections)}</strong> visible sections · autosaves in this browser</p>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1.05, 0.95], gap="large")

with left_col:
    import_tab, edit_tab, customize_tab = st.tabs(["Import", "Content", "Customize"])

    with import_tab:
        st.subheader("Import Resume")
        uploaded = st.file_uploader("Upload JSON, Markdown, or text", type=["json", "md", "markdown", "txt"])
        if uploaded is not None:
            uploaded_text = uploaded.read().decode("utf-8", errors="ignore")
            if st.button("Import Uploaded File", use_container_width=True):
                st.session_state.resume = import_resume_text(uploaded.name, uploaded_text)
                st.session_state.raw_import_text = uploaded_text
                st.session_state.pdf_bytes = None
                st.rerun()

        st.text_area("Paste markdown or plain text", key="raw_import_text", height=220, placeholder="# Summary\nBrief overview here...")
        ic1, ic2, ic3 = st.columns(3)
        if ic1.button("Import Pasted Text", use_container_width=True):
            st.session_state.resume = parse_resume_text(st.session_state.raw_import_text)
            st.session_state.pdf_bytes = None
            st.rerun()
        if ic2.button("Reset to Default", use_container_width=True):
            st.session_state.resume = clone_resume(DEFAULT_RESUME)
            st.session_state.pdf_bytes = None
            st.rerun()
        if ic3.button("Clear Browser Draft", use_container_width=True):
            persist_browser_resume(r, clear=True)
            st.success("Browser draft cleared.")
        st.download_button("Download JSON Backup", data=json.dumps(r, indent=2), file_name="resume.json", mime="application/json", use_container_width=True)

    with edit_tab:
        with st.expander("Personal Info", expanded=True):
            p = r["personal"]
            p["name"] = st.text_input("Full Name", value=p["name"], key="p_name")
            p["title"] = st.text_input("Professional Title", value=p["title"], key="p_title")
            c1, c2 = st.columns(2)
            p["email"] = c1.text_input("Email", value=p["email"], key="p_email")
            p["phone"] = c2.text_input("Phone", value=p["phone"], key="p_phone")
            p["location"] = st.text_input("Location", value=p["location"], key="p_location")
            c3, c4 = st.columns(2)
            p["linkedin"] = c3.text_input("LinkedIn URL", value=p["linkedin"], key="p_linkedin")
            p["github"] = c4.text_input("GitHub URL", value=p["github"], key="p_github")
            p["website"] = st.text_input("Website", value=p["website"], key="p_website")

        with st.expander("Summary", expanded=True):
            r["summary"] = st.text_area("Professional Summary", value=r["summary"], key="summary", height=140)

        with st.expander("Experience", expanded=False):
            for i, exp in enumerate(r["experience"]):
                st.markdown(f"**Entry {i+1}**")
                exp["role"] = st.text_input("Role", value=exp["role"], key=f"exp_{i}_role")
                exp["company"] = st.text_input("Company", value=exp["company"], key=f"exp_{i}_company")
                exp["location"] = st.text_input("Location", value=exp["location"], key=f"exp_{i}_location")
                exp["start_date"] = date_input_field("Start Date", f"exp_{i}_start", exp["start_date"])
                exp["current"] = st.checkbox("Current Role", value=exp["current"], key=f"exp_{i}_current")
                exp["end_date"] = "" if exp["current"] else date_input_field("End Date", f"exp_{i}_end", exp["end_date"] or exp["start_date"])
                bullets_text = st.text_area("Bullets", value="\n".join(exp["bullets"]), key=f"exp_{i}_bullets", height=140)
                exp["bullets"] = [line.strip() for line in bullets_text.split("\n") if line.strip()]
                if st.button("Remove Experience", key=f"exp_remove_{i}", use_container_width=True):
                    r["experience"].pop(i); st.rerun()
                st.markdown("---")
            if st.button("Add Experience", use_container_width=True):
                r["experience"].append({"role":"","company":"","location":"","start_date":"","end_date":"","current":False,"bullets":[]}); st.rerun()

        with st.expander("Skills", expanded=False):
            for i, sk in enumerate(r["skills"]):
                c1, c2 = st.columns([1, 2])
                sk["category"] = c1.text_input("Category", value=sk["category"], key=f"sk_{i}_cat")
                tag_text = c2.text_input("Tags", value=", ".join(sk.get("tags", [])), key=f"sk_{i}_tags")
                sk["tags"] = [x.strip() for x in tag_text.split(",") if x.strip()]
                if st.button("Remove Skill Group", key=f"sk_remove_{i}", use_container_width=True):
                    r["skills"].pop(i); st.rerun()
            if st.button("Add Skill Group", use_container_width=True):
                r["skills"].append({"category":"","tags":[]}); st.rerun()

        with st.expander("Projects", expanded=False):
            for i, proj in enumerate(r["projects"]):
                proj["name"] = st.text_input("Project Name", value=proj["name"], key=f"pr_{i}_name")
                proj["description"] = st.text_area("Description", value=proj["description"], key=f"pr_{i}_desc", height=80)
                proj["link"] = st.text_input("Link", value=proj["link"], key=f"pr_{i}_link")
                tech_text = st.text_input("Tech Stack", value=", ".join(proj["tech_stack"]), key=f"pr_{i}_tech")
                proj["tech_stack"] = [x.strip() for x in tech_text.split(",") if x.strip()]
                bullets_text = st.text_area("Bullets", value="\n".join(proj["bullets"]), key=f"pr_{i}_bullets", height=120)
                proj["bullets"] = [line.strip() for line in bullets_text.split("\n") if line.strip()]
                if st.button("Remove Project", key=f"pr_remove_{i}", use_container_width=True):
                    r["projects"].pop(i); st.rerun()
                st.markdown("---")
            if st.button("Add Project", use_container_width=True):
                r["projects"].append({"name":"","description":"","link":"","tech_stack":[],"bullets":[]}); st.rerun()

        with st.expander("Education", expanded=False):
            for i, edu in enumerate(r["education"]):
                edu["institution"] = st.text_input("Institution", value=edu["institution"], key=f"edu_{i}_inst")
                edu["degree"] = st.text_input("Degree", value=edu["degree"], key=f"edu_{i}_deg")
                edu["field"] = st.text_input("Field", value=edu["field"], key=f"edu_{i}_field")
                edu["grade"] = st.text_input("Grade / GPA", value=edu["grade"], key=f"edu_{i}_grade")
                edu["start_date"] = date_input_field("Start Date", f"edu_{i}_start", edu["start_date"])
                edu["current"] = st.checkbox("Current Study", value=edu["current"], key=f"edu_{i}_current")
                edu["end_date"] = "" if edu["current"] else date_input_field("End Date", f"edu_{i}_end", edu["end_date"] or edu["start_date"])
                if st.button("Remove Education", key=f"edu_remove_{i}", use_container_width=True):
                    r["education"].pop(i); st.rerun()
                st.markdown("---")
            if st.button("Add Education", use_container_width=True):
                r["education"].append({"institution":"","degree":"","field":"","grade":"","start_date":"","end_date":"","current":False}); st.rerun()

        opt1, opt2, opt3 = st.tabs(["Certifications", "Languages", "Volunteering"])
        with opt1:
            for i, cert in enumerate(r["certifications"]):
                cert["name"] = st.text_input("Certification", value=cert["name"], key=f"cert_{i}_name")
                cert["issuer"] = st.text_input("Issuer", value=cert["issuer"], key=f"cert_{i}_issuer")
                cert["date"] = st.text_input("Date", value=cert["date"], key=f"cert_{i}_date")
                if st.button("Remove Certification", key=f"cert_remove_{i}", use_container_width=True):
                    r["certifications"].pop(i); st.rerun()
            if st.button("Add Certification", use_container_width=True):
                r["certifications"].append({"name":"","issuer":"","date":""}); st.rerun()
        with opt2:
            for i, lang in enumerate(r["languages"]):
                c1, c2 = st.columns(2)
                lang["language"] = c1.text_input("Language", value=lang["language"], key=f"lang_{i}_language")
                lang["proficiency"] = c2.text_input("Proficiency", value=lang["proficiency"], key=f"lang_{i}_prof")
                if st.button("Remove Language", key=f"lang_remove_{i}", use_container_width=True):
                    r["languages"].pop(i); st.rerun()
            if st.button("Add Language", use_container_width=True):
                r["languages"].append({"language":"","proficiency":""}); st.rerun()
        with opt3:
            for i, vol in enumerate(r["volunteering"]):
                vol["org"] = st.text_input("Organization", value=vol["org"], key=f"vol_{i}_org")
                vol["role"] = st.text_input("Role", value=vol["role"], key=f"vol_{i}_role")
                vol["date"] = st.text_input("Date", value=vol["date"], key=f"vol_{i}_date")
                vol["description"] = st.text_area("Description", value=vol["description"], key=f"vol_{i}_desc", height=90)
                if st.button("Remove Volunteering", key=f"vol_remove_{i}", use_container_width=True):
                    r["volunteering"].pop(i); st.rerun()
            if st.button("Add Volunteering", use_container_width=True):
                r["volunteering"].append({"org":"","role":"","date":"","description":""}); st.rerun()

    with customize_tab:
        meta = r["meta"]
        meta["template"] = st.radio("Template", ["classic", "sidebar", "minimal"], horizontal=True, index=["classic", "sidebar", "minimal"].index(meta["template"]))
        meta["accent_color"] = st.color_picker("Accent Color", value=meta["accent_color"])
        meta["font_family"] = st.selectbox("Font Family", FONT_OPTIONS, index=FONT_OPTIONS.index(meta["font_family"]))
        meta["spacing"] = st.select_slider("Density", options=["compact", "normal", "spacious"], value=meta["spacing"])
        meta["ats_mode"] = st.toggle("ATS-friendly mode", value=meta["ats_mode"])
        st.markdown("**Section Visibility & Order**")
        for idx, sec in enumerate(meta["section_order"]):
            c1, c2, c3, c4 = st.columns([2.2, 1, 1, 1])
            c1.markdown(f"**{SECTION_LABELS[sec]}**")
            visible = c2.checkbox("Show", value=sec not in meta.get("hidden_sections", []), key=f"show_{sec}")
            if visible and sec in meta["hidden_sections"]:
                meta["hidden_sections"].remove(sec)
            if not visible and sec not in meta["hidden_sections"]:
                meta["hidden_sections"].append(sec)
            if c3.button("Up", key=f"up_{idx}", use_container_width=True) and idx > 0:
                meta["section_order"][idx], meta["section_order"][idx - 1] = meta["section_order"][idx - 1], meta["section_order"][idx]
                st.rerun()
            if c4.button("Down", key=f"down_{idx}", use_container_width=True) and idx < len(meta["section_order"]) - 1:
                meta["section_order"][idx], meta["section_order"][idx + 1] = meta["section_order"][idx + 1], meta["section_order"][idx]
                st.rerun()

html_output = render_html(r)
encoded = base64.b64encode(html_output.encode()).decode()

with right_col:
    st.subheader("Live Preview")
    st.caption("Preview updates as you edit and stays close to the exported PDF.")
    pc1, pc2, pc3 = st.columns(3)
    if pc1.button("Generate PDF", use_container_width=True, type="primary"):
        with st.spinner("Generating PDF..."):
            try:
                st.session_state.pdf_bytes = generate_pdf(html_output)
            except Exception as e:
                st.session_state.pdf_bytes = None
                st.error(f"PDF generation failed: {e}")
    pc2.download_button("Download HTML", data=html_output, file_name="resume_preview.html", mime="text/html", use_container_width=True)
    pc3.download_button("Download JSON", data=json.dumps(r, indent=2), file_name="resume.json", mime="application/json", use_container_width=True)
    if st.session_state.pdf_bytes:
        st.download_button("Download PDF", data=st.session_state.pdf_bytes, file_name=f"{(r['personal']['name'] or 'resume').replace(' ', '_')}_resume.pdf", mime="application/pdf", use_container_width=True)

    iframe_html = f"""
    <iframe
        src="data:text/html;base64,{encoded}"
        width="100%"
        height="1060"
        style="border: 1px solid #dbeafe; border-radius: 16px; background: white;"
        scrolling="yes">
    </iframe>
    """
    components.html(iframe_html, height=1080, scrolling=True)
