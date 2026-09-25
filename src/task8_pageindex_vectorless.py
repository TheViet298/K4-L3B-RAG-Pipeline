"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY not configured. Skipping upload.")
        return

    try:
        from pageindex import PageIndexClient

        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
        doc_ids = {}
        if CACHE_FILE.exists():
            try:
                doc_ids = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                doc_ids = {}

        for path in STANDARDIZED_DIR.rglob("*.md"):
            if path.name.startswith(".") or str(path) in doc_ids:
                continue
            response = client.submit_document(file_path=str(path))
            if response and "doc_id" in response:
                doc_ids[str(path)] = response["doc_id"]

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(doc_ids, indent=2), encoding="utf-8")
        print(f"Uploaded documents to PageIndex. Cached in {CACHE_FILE}")
    except Exception as e:
        print(f"Error uploading documents to PageIndex: {e}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query.strip() or top_k <= 0 or not PAGEINDEX_API_KEY:
        return []

    try:
        from pageindex import PageIndexClient

        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
        doc_ids = []
        if CACHE_FILE.exists():
            try:
                cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                doc_ids = list(cache.values())
            except Exception:
                doc_ids = []

        response = client.submit_query(query=query, doc_ids=doc_ids)
        results = []
        items = response.get("results", []) if isinstance(response, dict) else []
        for index, item in enumerate(items[:top_k]):
            item_id = item.get("id", f"pageindex-{index}")
            content = item.get("content", item.get("text", ""))
            score = float(item.get("score", 1.0 - (index * 0.1)))
            metadata = item.get(
                "metadata",
                {
                    "source": "pageindex",
                    "title": "PageIndex Result",
                    "doc_type": "legal",
                    "url": None,
                    "chunk_index": index,
                },
            )
            if "chunk_index" not in metadata:
                metadata["chunk_index"] = index
            results.append({
                "id": str(item_id),
                "content": content,
                "score": score,
                "metadata": metadata,
                "retrieval_method": "pageindex",
            })
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
    except Exception as e:
        raise RuntimeError(f"PageIndex retrieval failed: {e}") from e


if __name__ == "__main__":
    upload_documents()
