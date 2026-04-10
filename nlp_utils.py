# import spacy
# from sentence_transformers import SentenceTransformer
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# import re

# nlp = spacy.load("en_core_web_sm")
#embed_model = SentenceTransformer("all-MiniLM-L6-v2")  

# def extract_entities(text):
#     doc = nlp(text)
#     people = []
#     orgs = []
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             people.append(ent.text)
#         if ent.label_ in ("ORG", "GPE", "LOC"):
#             orgs.append(ent.text)
#     return {"persons": people, "orgs": orgs}

#def build_job_index(jobs):
    # """
    # jobs: list of dicts {id,title,company,description,requirements,skills}
    # builds embeddings for job descriptions and returns index object
    # """
    # texts = []
    # for j in jobs:
    #     text = " ".join([j.get("title",""), j.get("company",""), j.get("description",""), " ".join(j.get("skills", []))])
    #     texts.append(text)
    # if texts:
    #     embeddings = embed_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # else:
    #     embeddings = np.zeros((0, embed_model.get_sentence_embedding_dimension()))
    # return {
    #     "jobs": jobs,
    #     "embeddings": embeddings
    # }

# def match_resume_to_jobs(resume_text, job_index, top_k=5):
#     """
#     returns top_k matched jobs sorted by similarity
#     """
#     if not job_index or len(job_index.get("jobs", [])) == 0:
#         return []

#     resume_emb = embed_model.encode([resume_text], convert_to_numpy=True)
#     sims = cosine_similarity(resume_emb, job_index["embeddings"])[0]
#     idx_sorted = np.argsort(-sims)[:top_k]
#     matched = []
#     for idx in idx_sorted:
#         score = float(sims[idx])
#         job = job_index["jobs"][idx].copy()
#         job["score"] = round(score, 4)
#         matched.append(job)
#     return matched

# def match_resume_to_jobs(resume_text, job_index, threshold=0.25):
    
#     if not job_index or len(job_index.get("jobs", [])) == 0:
#         return []

#     resume_emb = embed_model.encode([resume_text], convert_to_numpy=True)

#     sims = cosine_similarity(resume_emb, job_index["embeddings"])[0]

#     matched = []

#     for idx, score in enumerate(sims):

#         if np.isnan(score):
#             continue

#         if score >= threshold:

#             # keep score within 0–1
#             score = max(0, min(score, 1))

#             job = job_index["jobs"][idx].copy()

#             job["score"] = round(score * 100, 2)  # convert to percentage

#             matched.append(job)

#     # DESCENDING order
#     matched.sort(key=lambda x: x["score"], reverse=True)

#     return matched

# def summarize_profile(profile):
#     """
#     Very light summary: combine key fields
#     """
#     parts = []
#     if profile.get("name"):
#         parts.append(profile["name"])
#     if profile.get("skills"):
#         parts.append("Skills: " + ", ".join(profile["skills"][:10]))
#     if profile.get("education"):
#         parts.append("Education: " + (profile["education"][0] if profile["education"] else ""))
#     return " | ".join(parts)


from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def build_job_index(jobs):
    texts = []
    for j in jobs:
        text = " ".join([
            j.get("title",""),
            j.get("company",""),
            j.get("description",""),
            " ".join(j.get("skills", []))
        ])
        texts.append(text)

    if texts:
        embeddings = embed_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    else:
        embeddings = np.zeros((0, embed_model.get_sentence_embedding_dimension()))

    return {
        "jobs": jobs,
        "embeddings": embeddings
    }

def match_resume_to_jobs(resume_text, job_index, threshold=0.25):

    if not job_index or len(job_index.get("jobs", [])) == 0:
        return []

    resume_emb = embed_model.encode([resume_text], convert_to_numpy=True)
    sims = cosine_similarity(resume_emb, job_index["embeddings"])[0]

    matched = []

    for idx, score in enumerate(sims):
        if np.isnan(score):
            continue

        if score >= threshold:
            score = max(0, min(score, 1))
            job = job_index["jobs"][idx].copy()
            job["score"] = round(score * 100, 2)
            matched.append(job)

    matched.sort(key=lambda x: x["score"], reverse=True)
    return matched

def summarize_profile(profile):
    parts = []
    if profile.get("name"):
        parts.append(profile["name"])
    if profile.get("skills"):
        parts.append("Skills: " + ", ".join(profile["skills"][:10]))
    if profile.get("education"):
        parts.append("Education: " + (profile["education"][0] if profile["education"] else ""))
    return " | ".join(parts)