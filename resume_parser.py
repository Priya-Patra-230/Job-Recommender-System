import re
import io
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s-]{8,14}\d")

#  PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?[\d\s-]{6,15}")

def extract_text_from_file(path):
    """
    Supports PDF, DOCX, TXT.
    """
    path = path.lower()
    if path.endswith(".pdf"):
        text = pdf_extract_text(path)
        return text
    elif path.endswith(".docx"):
        doc = Document(path)
        full = []
        for p in doc.paragraphs:
            full.append(p.text)
        return "\n".join(full)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def parse_resume_fields(text):
    """
    Heuristic extraction of email, phone, skills lines, education blocks etc.
    This is intentionally simple; you can replace with spaCy NER for better results.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full = " ".join(lines)

    
    emails = EMAIL_RE.findall(full)
    email = emails[0] if emails else None

   
    phone = None
    for match in PHONE_RE.finditer(full):
        candidate = match.group()
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 15:
            phone = candidate
            break


    
    name = None
    for line in lines[:6]:
        if email and email in line: 
            continue
        if phone and phone in line:
            continue
        
        if re.search(r"resume|curriculum|cv", line, re.I):
            continue
        
        if re.match(r"^[A-Za-z .,'-]{2,50}$", line):
            name = line
            break

   
    education = []
    experience = []
    skills = []

  
    content = "\n".join(lines)
  
    for sec_name in ["education", "academic", "qualification", "experience", "work experience", "projects", "skills", "technical skills"]:
        pattern = r"(?i){}[:\n]".format(sec_name)
        if re.search(pattern, content):
            
            idx = re.search(pattern, content).start()
            snippet = content[idx: idx+800]
            if "skill" in sec_name:
                skills.append(snippet)
            elif "educ" in sec_name:
                education.append(snippet)
            else:
                experience.append(snippet)

   
    COMMON_SKILLS = ["python","java","c++","sql","nlp","machine learning","tensorflow","pytorch","react","node","flask","django","excel","tableau","aws","docker","kubernetes","spacy","scikit-learn","pandas","numpy"]
    found_skills = set()
    fl = full.lower()
    for s in COMMON_SKILLS:
        if s in fl:
            found_skills.add(s)
    skills = list(found_skills)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": skills,
        "raw_text_snippet": full[:2000]
    }
