import os
from pathlib import Path
from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates


def get_root_path(request: Request | None = None) -> str:
    # 1. Explicit ROOT_PATH environment variable
    env_root = os.getenv("ROOT_PATH", "").strip().rstrip("/")
    if env_root:
        return env_root

    if request:
        # 2. X-Forwarded-Prefix header sent by Nginx / Traefik / Caddy
        forwarded_prefix = request.headers.get("x-forwarded-prefix", "").strip().rstrip("/")
        if forwarded_prefix:
            return forwarded_prefix

        # 3. ASGI scope root_path (FastAPI root_path)
        scope_root = request.scope.get("root_path", "").strip().rstrip("/")
        if scope_root:
            return scope_root

    return ""


class DynamicJinja2Templates(Jinja2Templates):
    def TemplateResponse(self, *args: Any, **kwargs: Any):
        request: Request | None = None

        if args:
            if isinstance(args[0], Request):
                request = args[0]
            elif len(args) > 1 and isinstance(args[1], dict):
                request = args[1].get("request")
        if not request:
            if "request" in kwargs:
                request = kwargs["request"]
            elif "context" in kwargs and isinstance(kwargs["context"], dict):
                request = kwargs["context"].get("request")

        root_path = get_root_path(request)

        if len(args) >= 3 and isinstance(args[2], dict):
            args[2]["root_path"] = root_path
        elif len(args) == 2 and isinstance(args[1], dict):
            args[1]["root_path"] = root_path
        elif "context" in kwargs and isinstance(kwargs["context"], dict):
            kwargs["context"]["root_path"] = root_path
        else:
            kwargs.setdefault("context", {})["root_path"] = root_path

        return super().TemplateResponse(*args, **kwargs)


templates = DynamicJinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.globals["root_path"] = get_root_path()


def redirect_to(path: str, status_code: int = 303, request: Request | None = None):
    from fastapi.responses import RedirectResponse
    root = get_root_path(request)
    target = f"{root}{path}" if path.startswith("/") else f"{root}/{path}"
    return RedirectResponse(target, status_code=status_code)

