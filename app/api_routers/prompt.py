from sqlalchemy import text
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

import time
from typing import List

from config.base import settings

# Create an APIRouter instance
router = APIRouter(
    tags=["prompt"]
)

# Configure the location of the template files
templates = Jinja2Templates(directory="templates")

@router.get("/get_role_prompts_metadata", summary="Role prompt metadata")
def get_role_prompts_metadata(request: Request):

    engine = request.app.state.cloudsql_db.get_engine()  # sync Engine 반환
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT id, name, description
            FROM public.prompt_role
            ORDER BY id;
        """))
        # rows = [dict(r) for r in res.fetchall()]
        rows = res.mappings().all()
    # print('rows:', rows)

    return rows


# @router.get("/get_role_prompt_text", summary="Role prompt text")
# def get_role_prompt_text(request: Request, role_id: int):

#     engine = request.app.state.cloudsql_db.get_engine()  # sync Engine 반환
#     with engine.connect() as conn:
#         res = conn.execute(
#             text("SELECT id, text FROM public.prompt_role WHERE id = :id"),
#             {"id": role_id}
#         )
#         # mappings()로 dict 형태로 받음; first()로 첫 행(또는 None) 가져오기
#         row = res.mappings().first()

#     if not row:
#         raise HTTPException(status_code=404, detail="role prompt not found")

#     return {"text": row["text"]}
