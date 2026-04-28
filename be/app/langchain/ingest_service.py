# import asyncio
# from typing import List

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import text, select
# from sqlalchemy.orm import selectinload, joinedload

# from app.db.models.event import Event
# from app.db.models.ai_docs import AIDoc

# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# # =========================
# # EMBEDDING
# # =========================
# embedding_model = HuggingFaceEmbeddings(
#     model_name="intfloat/multilingual-e5-base"
# )

# def embed_text(text: str):
#     return embedding_model.embed_documents([f"passage: {text}"])[0]


# # =========================
# # SEMANTIC CHUNKING
# # =========================
# splitter = RecursiveCharacterTextSplitter(
#     chunk_size=300,
#     chunk_overlap=50
# )


# # =========================
# # MAIN INGEST
# # =========================
# async def refresh_ai_docs_for_event(db: AsyncSession, event_id: str):
#     async with db.begin():

#         await db.execute(
#             text("DELETE FROM ai_docs WHERE event_id = :event_id"),
#             {"event_id": event_id}
#         )

#         stmt = (
#             select(Event)
#             .options(joinedload(Event.venue), selectinload(Event.showtimes))
#             .where(Event.id == event_id)
#         )
#         result = await db.execute(stmt)
#         event = result.unique().scalar_one_or_none()

#         if not event:
#             return

#         raw_text = f"""
#         Tên sự kiện: {event.name}
#         Mô tả: {event.description or ""}
#         Thể loại: {event.category or ""}
#         """

#         if event.venue:
#             raw_text += f"\nĐịa điểm: {event.venue.name}, {event.venue.address}"

#         if event.showtimes:
#             raw_text += "\nLịch diễn: " + ", ".join([
#                 st.start_time.strftime('%H:%M %d/%m/%Y')
#                 for st in event.showtimes if st.start_time
#             ])

#         # CHUNK
#         chunks = splitter.split_text(raw_text)

#         # EMBEDDING SONG SONG
#         vectors = await asyncio.gather(*[
#             asyncio.to_thread(embed_text, chunk)
#             for chunk in chunks
#         ])

#         docs = []
#         for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
#             docs.append(AIDoc(
#                 event_id=event_id,
#                 content=chunk,
#                 embedding=vector,
#                 type="event_info",
#                 chunk_order=idx,
#                 language="vi",
#                 metadata_info={
#                     "event_name": event.name
#                 }
#             ))

#         db.add_all(docs)
#         await db.commit()
import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload, joinedload

from app.db.models.event import Event
from app.db.models.ai_docs import AIDoc

from langchain_huggingface import HuggingFaceEmbeddings

# =========================
# EMBEDDING
# =========================
embedding_model = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

def embed_text(text: str):
    return embedding_model.embed_documents(
        [f"passage: {text}"]
    )[0]


# =========================
# BUILD TEXT (NATURAL LANGUAGE)
# =========================
def build_event_chunks(event: Event) -> List[str]:
    chunks = []

    # 1. Mô tả sự kiện
    if event.description:
        chunks.append(
            f"Sự kiện '{event.name}'. {event.description}"
        )

    # 2. Thể loại
    if event.category:
        chunks.append(
            f"Sự kiện '{event.name}' thuộc thể loại {event.category}"
        )

    # 3. Địa điểm
    if event.venue:
        chunks.append(
            f"Sự kiện '{event.name}' được tổ chức tại {event.venue.name}, {event.venue.address}"
        )

    # 4. Lịch diễn
    if event.showtimes:
        times = ", ".join([
            st.start_time.strftime('%H:%M %d/%m/%Y')
            for st in event.showtimes if st.start_time
        ])
        chunks.append(
            f"Lịch diễn của sự kiện '{event.name}': {times}"
        )

    return chunks


# =========================
# MAIN INGEST
# =========================
async def refresh_ai_docs_for_event(db: AsyncSession, event_id: str):
    # 1. XÓA DOC CŨ
    await db.execute(
        text("DELETE FROM ai_docs WHERE event_id = :event_id"),
        {"event_id": event_id}
    )

    # 2. LOAD EVENT + RELATION
    stmt = (
        select(Event)
        .options(
            joinedload(Event.venue),
            selectinload(Event.showtimes)
        )
        .where(Event.id == event_id)
    )

    result = await db.execute(stmt)
    event = result.unique().scalar_one_or_none()

    if not event:
        return

    # 3. BUILD CHUNKS (semantic)
    chunks = build_event_chunks(event)

    if not chunks:
        return

    # 4. EMBEDDING SONG SONG
    vectors = await asyncio.gather(*[
        asyncio.to_thread(embed_text, chunk)
        for chunk in chunks
    ])

    # 5. BUILD DOCS
    docs = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        docs.append(AIDoc(
            event_id=event_id,
            content=chunk,
            embedding=vector,
            chunk_order=idx,
            type="event_info",
            language="vi",
            metadata_info={
                "event_id": str(event.id),
                "event_name": event.name,
                "category": event.category,
                "venue": event.venue.name if event.venue else None,
                "address": event.venue.address if event.venue else None
            }
        ))

    # 6. SAVE
    db.add_all(docs)
    await db.commit()