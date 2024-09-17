import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from .services import get_category_style

# Constants
OPTIONS = ["H", "Fe", "Ta", "Pb", "O"]

# QUESTION = "This element is essential for the production of hemoglobin in the human body and is often associated with red blood cells. What is it?"
# QUESTION = "Known for its use in steel production, this element has the atomic number 26. What is it?"
# QUESTION = 'The symbol for this element comes from its Latin name, "ferrum." Which element is this?'
# QUESTION = "This element is found in Earth's core and contributes to the planet's magnetic field. What is it?"
QUESTION = "In ancient times, this element was used to make weapons and tools, and it still forms the backbone of modern infrastructure. What is it?"
ANSWER = "Fe"

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "static")

# Load element_list
with open(Path(__file__).resolve().parent / "static" / "data" / "element_list.json") as f:
    elements = json.load(f)

# Load element_lookup map
with open(Path(__file__).resolve().parent / "static" / "data" / "element_lookup.json") as f:
    element_lookup = json.load(f)


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
async def index(
    request: Request, visitor: Annotated[VisitorAuth | None, Depends(get_auth_visitor)]
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "puzzle": "periodic",
            "visitor": visitor.uid,
            "elements": elements,
            "element_lookup": element_lookup,
            "get_category_style": get_category_style,
            "options": OPTIONS,
            "question": QUESTION,
        },
    )
