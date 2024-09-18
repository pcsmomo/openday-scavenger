from fastapi import APIRouter

from .demo.views import router as puzzle_demo_router
from .finder.views import router as puzzle_finder_router

router = APIRouter()

# Include puzzle routes. Name entered into database should match the prefix.
router.include_router(puzzle_demo_router, prefix="/demo")
router.include_router(puzzle_finder_router, prefix="/finder")
router.include_router(puzzle_finder_router, prefix="/finder1")
router.include_router(puzzle_finder_router, prefix="/finder2")
router.include_router(puzzle_finder_router, prefix="/finder3")


# Include a route to catch all invalid puzzle routes so we can throw a custom 404.
@router.get("/{path:path}/")
async def catch_all(path: str):
    pass
