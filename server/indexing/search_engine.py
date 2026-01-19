"""Functional approach to search engine - replaces search_engine.py class"""
from typing import List, Dict, Any, Optional, Tuple

from indexing.similarity import cosine_similarity, dot_product_sparse
from indexing.text import l2_norm, term_frequencies, tokenize, vector_weights
from database.repositories import (
    search_publications,
    find_publication_by_id,
    find_all_publications,
    count_publications,
    find_author_by_id,
    find_all_authors,
    count_authors,
    get_publication_stats_by_year,
    get_publication_stats_by_type
)
from models.schemas import SearchQuery
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _get_publication_text(pub: Dict[str, Any]) -> str:
    """Extract searchable text from publication"""
    parts: List[str] = []
    title = pub.get("title")
    if title:
        parts.append(str(title))
    abstract = pub.get("abstract")
    if abstract:
        parts.append(str(abstract))

    keywords = pub.get("keywords") or []
    if isinstance(keywords, list):
        parts.extend(str(k) for k in keywords if k)
    else:
        parts.append(str(keywords))

    authors = pub.get("authors") or []
    if isinstance(authors, list):
        for a in authors:
            if isinstance(a, dict):
                name = a.get("name")
                if name:
                    parts.append(str(name))
            elif a:
                parts.append(str(a))

    return "\n".join(parts)


def _calculate_cosine_similarity(query: str, pub: Dict[str, Any]) -> float:
    """Calculate cosine similarity between query and publication"""
    q_tokens = tokenize(query)
    q_tf = term_frequencies(q_tokens)
    q_w = vector_weights(q_tf)
    q_norm = l2_norm(q_w)
    if q_norm <= 0.0 or not q_w:
        return 0.0

    doc_text = _get_publication_text(pub)
    d_tokens = tokenize(doc_text)
    d_tf = term_frequencies(d_tokens)
    d_w = vector_weights(d_tf)
    d_norm = l2_norm(d_w)
    if d_norm <= 0.0 or not d_w:
        return 0.0

    dot = float(dot_product_sparse(q_w, d_w))
    return float(cosine_similarity(dot, q_norm, d_norm))


async def search(query: SearchQuery) -> Tuple[List[Dict[str, Any]], int]:
    """Search publications"""
    logger.info(f"Searching for: {query.q}")
    
    # Build filters
    filters = {}
    
    if query.year_from or query.year_to:
        filters["year_from"] = query.year_from
        filters["year_to"] = query.year_to
    
    if query.author:
        filters["author"] = query.author
    
    if query.publication_type:
        filters["publication_type"] = query.publication_type
    
    filters["sort"] = query.sort
    
    # If no query, return all matching documents with pagination
    if not (query.q or "").strip():
        skip = (query.page - 1) * query.limit
        results, total = await search_publications(
            query=query.q,
            filters=filters,
            skip=skip,
            limit=query.limit
        )
        for doc in results:
            doc["cosine_similarity"] = 0.0
        logger.info(f"Found {total} results")
        return results, total

    page = max(1, int(query.page))
    limit = max(1, int(query.limit))
    fetch_size = min(max(page * limit * 10, limit * 10), 5000)

    # Fetch candidate documents
    candidates, _ = await search_publications(
        query=query.q,
        filters=filters,
        skip=0,
        limit=fetch_size
    )

    scored: List[Dict[str, Any]] = []
    for doc in candidates:
        try:
            score = _calculate_cosine_similarity(query.q, doc)
        except Exception as e:
            logger.warning(f"Failed to compute cosine similarity for doc {doc.get('_id')}: {e}")
            score = 0.0
        if score > 0.0:
            doc["cosine_similarity"] = score
            scored.append(doc)

    # Sort by cosine similarity
    scored.sort(key=lambda d: float(d.get("cosine_similarity") or 0.0), reverse=True)

    total = len(scored)
    start = (page - 1) * limit
    end = start + limit
    results = scored[start:end]

    logger.info(f"Found {total} results")
    return results, total


async def get_publication_by_id(pub_id: str) -> Optional[Dict[str, Any]]:
    """Get publication by ID"""
    return await find_publication_by_id(pub_id)


async def get_all_publications(page: int = 1, limit: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    """Get all publications with pagination"""
    skip = (page - 1) * limit
    results = await find_all_publications(skip=skip, limit=limit)
    total = await count_publications()
    return results, total


async def get_publications_by_author(
    author_pure_id: str, 
    page: int = 1, 
    limit: int = 10
) -> Tuple[List[Dict[str, Any]], int]:
    """Get publications by author"""
    filters = {"author": author_pure_id}
    skip = (page - 1) * limit
    results, total = await search_publications(
        query="",
        filters=filters,
        skip=skip,
        limit=limit
    )
    return results, total


async def get_statistics() -> Dict[str, Any]:
    """Get search index statistics"""
    total_pubs = await count_publications()
    total_auth = await count_authors()
    pubs_by_year = await get_publication_stats_by_year()
    pubs_by_type = await get_publication_stats_by_type()
    
    return {
        "total_publications": total_pubs,
        "total_authors": total_auth,
        "publications_by_year": pubs_by_year,
        "publications_by_type": pubs_by_type
    }


async def get_author_by_id(author_id: str) -> Optional[Dict[str, Any]]:
    """Get author by ID"""
    return await find_author_by_id(author_id)


async def get_all_authors(page: int = 1, limit: int = 50) -> Tuple[List[Dict[str, Any]], int]:
    """Get all authors with pagination"""
    skip = (page - 1) * limit
    results = await find_all_authors(skip=skip, limit=limit)
    total = await count_authors()
    return results, total
