from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.service import get_all as get_all_puzzles
from openday_scavenger.api.visitors.schemas import VisitorCreate, VisitorPoolCreate
from openday_scavenger.api.visitors.service import (
    check_out,
    create,
    create_visitor_pool,
    get_visitor_pool,
)
from openday_scavenger.api.visitors.service import get_all as get_all_visitors
from openday_scavenger.config import get_settings

router = APIRouter()
config = get_settings()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


@router.get("/static/{path:path}")
async def get_static_files(
    path: Path,
):
    """Serve files from a local static folder"""
    # This route is required as the current version of FastAPI doesn't allow
    # the mounting of folders on APIRouter. This is an open issue:
    # https://github.com/fastapi/fastapi/discussions/9070
    parent_path = Path(__file__).resolve().parent / "static"
    file_path = parent_path / path

    # Make sure the requested path is a file and relative to this path
    if file_path.is_relative_to(parent_path) and file_path.is_file():
        return FileResponse(file_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested file does not exist"
        )


@router.get("/")
async def render_visitor_page(request: Request):
    """Render the puzzle admin page"""
    return templates.TemplateResponse(
        request=request, name="visitors.html", context={"active_page": "visitors"}
    )


@router.post("/")
async def create_visitor(
    visitor_in: VisitorCreate, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Create a new visitor"""
    _ = create(db, visitor_uid=visitor_in.uid)
    return await _render_visitor_table(request, db)


@router.post("/{visitor_uid}/checkout")
async def update_visitor(
    visitor_uid: str, request: Request, db: Annotated["Session", Depends(get_db)]
):
    """Update a single puzzle and re-render the table"""
    _ = check_out(db, visitor_uid=visitor_uid)
    return await _render_visitor_table(request, db)


@router.get("/table")
async def render_visitor_table(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    uid_filter: str | None = None,
    still_playing: bool | None = None,
):
    """Render the table of visitors on the admin page"""
    return await _render_visitor_table(request, db, uid_filter, still_playing)


@router.post("/pool")
async def initialise_visitor_pool(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    pool_in: VisitorPoolCreate = VisitorPoolCreate(),
):
    create_visitor_pool(db, pool_in=pool_in)
    return await _render_visitor_pool_table(request, db)


@router.get("/pool")
async def render_visitor_pool_table(
    request: Request, db: Annotated["Session", Depends(get_db)], limit: int = 10
):
    """Render the table of possible visitor uids on the admin page"""
    return await _render_visitor_pool_table(request, db, limit)


async def _render_visitor_table(
    request: Request,
    db: Annotated["Session", Depends(get_db)],
    uid_filter: str | None = None,
    still_playing: bool | None = None,
):
    visitors = get_all_visitors(db, uid_filter=uid_filter, still_playing=still_playing)
    number_enabled_puzzles = len(get_all_puzzles(db, only_active=True))

    return templates.TemplateResponse(
        request=request,
        name="visitors_table.html",
        context={
            "visitors": visitors,
            "number_enabled_puzzles": number_enabled_puzzles,
            "now": datetime.now(),
        },
    )


async def _render_visitor_pool_table(
    request: Request, db: Annotated["Session", Depends(get_db)], limit: int = 10
):
    visitor_pool = get_visitor_pool(db, limit=limit)

    return templates.TemplateResponse(
        request=request,
        name="visitor_pool_table.html",
        context={"visitor_pool": visitor_pool, "base_url": config.BASE_URL},
    )
