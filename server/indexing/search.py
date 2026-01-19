from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bson import ObjectId

from database.documents import get_documents_by_ids, get_terms_postings
from indexing.similarity import cosine_similarity
from indexing.text import l2_norm, term_frequencies, tokenize, vector_weights


@dataclass(frozen=True)
class SearchHit:
    doc_id: ObjectId
    score: float


def _accumulate_scores(
    *,
    query_weights: dict[str, float],
    term_docs: list[dict[str, Any]],
) -> dict[ObjectId, float]:
    scores: dict[ObjectId, float] = {}
    for term_doc in term_docs:
        term = term_doc.get("_id")
        q_w = float(query_weights.get(term, 0.0))
        if q_w <= 0.0:
            continue
        for posting in term_doc.get("postings") or []:
            doc_id = posting.get("doc_id")
            d_w = float(posting.get("w") or 0.0)
            if not doc_id or d_w <= 0.0:
                continue
            scores[doc_id] = scores.get(doc_id, 0.0) + (d_w * q_w)
    return scores


async def search_documents(
    db,
    *,
    query: str,
    page: int,
    limit: int,
) -> tuple[list[dict[str, Any]], int]:
    tokens = tokenize(query)
    q_tf = term_frequencies(tokens)
    q_weights = vector_weights(q_tf)
    q_norm = l2_norm(q_weights)
    if q_norm <= 0.0 or not q_weights:
        return [], 0

    terms = list(q_weights.keys())
    term_docs = await get_terms_postings(db, terms)
    dot_by_doc = _accumulate_scores(query_weights=q_weights, term_docs=term_docs)
    if not dot_by_doc:
        return [], 0

    candidate_ids = list(dot_by_doc.keys())
    docs = await get_documents_by_ids(db, candidate_ids)
    by_id = {d["_id"]: d for d in docs}

    hits: list[SearchHit] = []
    for doc_id, dot in dot_by_doc.items():
        doc = by_id.get(doc_id)
        if not doc:
            continue
        score = cosine_similarity(float(dot), float(doc.get("norm") or 0.0), q_norm)
        if score > 0.0:
            hits.append(SearchHit(doc_id=doc_id, score=score))

    hits.sort(key=lambda h: h.score, reverse=True)
    total = len(hits)
    start = (page - 1) * limit
    end = start + limit

    page_hits = hits[start:end]
    page_doc_ids = [h.doc_id for h in page_hits]
    page_docs = await get_documents_by_ids(db, page_doc_ids)
    score_by_id = {h.doc_id: h.score for h in page_hits}

    results: list[dict[str, Any]] = []
    for d in page_docs:
        doc_id = d.get("_id")
        results.append(
            {
                "_id": str(doc_id),
                "url": d.get("url"),
                "title": d.get("title"),
                "metadata": d.get("metadata") or {},
                "score": float(score_by_id.get(doc_id, 0.0)),
                "created_at": d.get("created_at"),
                "updated_at": d.get("updated_at"),
            }
        )

    return results, total

