"""接口层：真实入口。

`handle_request` 是 HTTP 处理器（有路由装饰器），它把请求分派给服务层，
整个仓库的时序图应该从这里开始画。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from ..domain.base import AdminUser, DomainError, NotFound, TTLCache, User, UserRepository
from ..services.user_service import ServiceError, SyncService, UserService

logger = logging.getLogger(__name__)


@dataclass
class Request:
    path: str
    method: str = "GET"
    body: str = ""


@dataclass
class Response:
    status: int
    payload: dict

    def render(self) -> str:
        return json.dumps(self.payload, ensure_ascii=False)


def build_service() -> UserService:
    """组装依赖：仓储 + 缓存。"""
    cache = TTLCache(ttl_seconds=45)
    repo = UserRepository(cache=cache)
    return UserService(repo=repo, cache=cache)


def handle_request(request: Request, service: UserService | None = None) -> Response:
    """入口：按路径分派到具体处理器。"""
    svc = service or build_service()
    try:
        if request.path == "/users" and request.method == "POST":
            return create_user(request, svc)
        if request.path.startswith("/users/"):
            user_id = int(request.path.rsplit("/", 1)[-1])
            return get_user(user_id, svc)
        return Response(status=404, payload={"error": "not found"})
    except NotFound as exc:
        return Response(status=404, payload={"error": str(exc)})
    except (ServiceError, DomainError) as exc:
        logger.warning("request failed: %s", exc)
        return Response(status=500, payload={"error": str(exc)})


def get_user(user_id: int, service: UserService) -> Response:
    """读单个用户。"""
    user = service.load(user_id)
    return Response(status=200, payload=to_payload(user))


def create_user(request: Request, service: UserService) -> Response:
    """创建用户；body 里必须带 email。"""
    data = json.loads(request.body or "{}")
    email = data.get("email", "")
    if not email:
        return Response(status=400, payload={"error": "email is required"})
    user = service.register(email=email, display_name=data.get("display_name", ""))
    return Response(status=201, payload=to_payload(user))


def promote_user(user_id: int, scopes: list[str], service: UserService) -> Response:
    """提升权限；普通用户会被拒绝。"""
    admin = service.promote(user_id, scopes)
    service.require(admin, "admin")
    return Response(status=200, payload=to_payload(admin))


def to_payload(user: User) -> dict:
    data = {"id": user.id, "email": user.email, "display_name": user.display_name}
    if isinstance(user, AdminUser):
        data["scopes"] = list(user.scopes)
    return data


async def handle_sync(ids: list[int], service: SyncService) -> Response:
    """异步入口：批量同步。"""
    stats = await service.sync_with_retry(ids)
    return Response(status=200, payload=stats)