import os
from pathlib import Path
from fastapi.templating import Jinja2Templates

ROOT_PATH = os.getenv("ROOT_PATH", "")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.globals["root_path"] = ROOT_PATH

def redirect_to(path: str, status_code: int = 303):
    from fastapi.responses import RedirectResponse
    target = f"{ROOT_PATH}{path}" if path.startswith("/") else f"{ROOT_PATH}/{path}"
    return RedirectResponse(target, status_code=status_code)
