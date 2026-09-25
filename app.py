import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="VinUni Academic RAG Assistant",
    page_icon="🎓",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🎓 VinUni RAG Chatbot")
    st.caption("Hệ thống hỏi đáp học vụ, tuyển sinh và đào tạo VinUniversity")
    top_k = st.slider("Số chunks (Top-K)", min_value=1, max_value=10, value=5)
    st.markdown("---")
    st.markdown(
        "**Tính năng nổi bật:**\n"
        "- Hybrid Retrieval (Dense + BM25)\n"
        "- Reciprocal Rank Fusion (RRF)\n"
        "- Fallback pipeline khi score thấp\n"
        "- Trả lời có citation & kiểm chứng nguồn"
    )
    if st.button("Xóa lịch sử hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.title("VinUniversity Academic & Admissions Assistant")
st.caption(
    "Hỏi đáp thông tin về quy chế đăng ký tín chỉ, chương trình đào tạo BSDS/BAE, "
    "học phí, học bổng và cuộc sống sinh viên."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(
                f"📚 Nguồn trích dẫn ({len(message['sources'])} tài liệu - "
                f"Phương thức: {message.get('retrieval_source', 'N/A')})"
            ):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"**[{idx}] {meta.get('title', 'Tài liệu')}** "
                        f"(`{src.get('retrieval_method', 'dense')}` | Score: `{src.get('score', 0.0):.4f}`)"
                    )
                    st.markdown(f"> *Nguồn: {meta.get('source', '')}*")
                    if meta.get("url"):
                        st.markdown(f"🔗 [Liên kết nguồn]({meta['url']})")
                    st.text(src.get("content", "").strip())
                    st.markdown("---")

query = st.chat_input("Nhập câu hỏi của bạn về VinUni...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result["sources"]
            retrieval_source = result["retrieval_source"]

            st.markdown(answer)

            if sources:
                with st.expander(
                    f"📚 Nguồn trích dẫn ({len(sources)} tài liệu - "
                    f"Phương thức: {retrieval_source})"
                ):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(
                            f"**[{idx}] {meta.get('title', 'Tài liệu')}** "
                            f"(`{src.get('retrieval_method', 'dense')}` | Score: `{src.get('score', 0.0):.4f}`)"
                        )
                        st.markdown(f"> *Nguồn: {meta.get('source', '')}*")
                        if meta.get("url"):
                            st.markdown(f"🔗 [Liên kết nguồn]({meta['url']})")
                        st.text(src.get("content", "").strip())
                        st.markdown("---")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
