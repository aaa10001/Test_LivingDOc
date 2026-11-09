@startuml
title src.api 模块类图（src/api/routes.py）

class Response {
  +status: int
  +payload: dict
  +render(self): str
}

class Request <<外部模块类型>> {
}

class UserService <<外部模块类型>> {
}

class health_check <<function>> {
  +health_check(request: Request): Response
}

class user_id_from <<function>> {
  +user_id_from(request: Request): int
}

class delete_user <<function>> {
  +delete_user(request: Request, service: UserService): Response
}

class handle_request <<function>> {
  +handle_request(request: Request, service: UserService | None = None): Response
}

handle_request ..> health_check : 依赖（调用）
handle_request ..> delete_user : 依赖（调用）
handle_request ..> user_id_from : 依赖（调用）
delete_user ..> user_id_from : 依赖（调用）
handle_request ..> Request : 依赖（参数）
handle_request ..> UserService : 依赖（参数）
handle_request ..> Response : 依赖（返回值）
delete_user ..> Request : 依赖（参数）
delete_user ..> UserService : 依赖（参数）
delete_user ..> Response : 依赖（返回值）
health_check ..> Request : 依赖（参数）
health_check ..> Response : 依赖（返回值）
user_id_from ..> Request : 依赖（参数）

note right of handle_request
  控制流: try / if 多分支 / except 两处
  分派到 health_check, create_user, delete_user, get_user, user_id_from
end note

note right of user_id_from
  控制流: try / except ValueError
  解析失败时抛出 NotFound
end note

note right of delete_user
  控制流: 无分支, 调用 user_id_from 与 service.deactivate
end note

note right of health_check
  控制流: 无分支, 不访问仓储
end note

note bottom of Response
  本次改动仅涉及 health_check, user_id_from, delete_user, handle_request
  未改动的 build_service, create_user, get_user, to_payload, promote_user, handle_sync
  以及类型 User, SyncService 未在图中展开
end note
@enduml
