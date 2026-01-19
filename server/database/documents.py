from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from pymongo import UpdateOne


@dataclass(frozen=True)
class StoredDocument:
    id: ObjectId
    url: str
    title: str
    text: str
    metadata: dict[str, Any]
    term_weights: dict[str, float]
    norm: float


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_document_indexes(db) -> None:
    await db.documents.create_index("url", unique=True)
    await db.documents.create_index([("title", "text"), ("text", "text")])
    await db.inverted_index.create_index("_id", unique=True)


async def get_document_by_url(db, url: str) -> Optional[dict[str, Any]]:
    return await db.documents.find_one({"url": url})


async def delete_document_and_postings(db, doc_id: ObjectId) -> None:
    doc = await db.documents.find_one({"_id": doc_id})
    if not doc:
        return
    terms = list((doc.get("term_weights") or {}).keys())
    if terms:
        await db.inverted_index.update_many(
            {"_id": {"$in": terms}},
            {"$pull": {"postings": {"doc_id": doc_id}}},
        )
        await db.inverted_index.delete_many({"postings": {"$size": 0}})
    await db.documents.delete_one({"_id": doc_id})


async def upsert_document(db, *, url: str, title: str, text: str, metadata: dict[str, Any], term_weights: dict[str, float], norm: float) -> StoredDocument:
    existing = await get_document_by_url(db, url)
    if existing:
        await delete_document_and_postings(db, existing["_id"])

    payload = {
        "url": url,
        "title": title,
        "text": text,
        "metadata": metadata,
        "term_weights": term_weights,
        "norm": norm,
        "created_at": _now(),
        "updated_at": _now(),
    }
    result = await db.documents.insert_one(payload)
    return StoredDocument(
        id=result.inserted_id,
        url=url,
        title=title,
        text=text,
        metadata=metadata,
        term_weights=term_weights,
        norm=norm,
    )


async def upsert_postings(db, *, doc_id: ObjectId, term_weights: dict[str, float]) -> None:
    if not term_weights:
        return
    ops: list[UpdateOne] = []
    for term, weight in term_weights.items():
        ops.append(
            UpdateOne(
                {"_id": term},
                {
                    "$push": {"postings": {"doc_id": doc_id, "w": float(weight)}},
                    "$setOnInsert": {"created_at": _now()},
                    "$set": {"updated_at": _now()},
                },
                upsert=True,
            )
        )
    if ops:
        await db.inverted_index.bulk_write(ops, ordered=False)


async def get_terms_postings(db, terms: list[str]) -> list[dict[str, Any]]:
    if not terms:
        return []
    cursor = db.inverted_index.find({"_id": {"$in": terms}})
    return await cursor.to_list(length=len(terms))


async def get_documents_by_ids(db, doc_ids: list[ObjectId]) -> list[dict[str, Any]]:
    if not doc_ids:
        return []
    cursor = db.documents.find({"_id": {"$in": doc_ids}})
    docs = await cursor.to_list(length=len(doc_ids))
    by_id = {d["_id"]: d for d in docs}
    return [by_id[i] for i in doc_ids if i in by_id]

