@startuml
title 接口模块类图（src/api/routes.py）

class Response {
  +status: int
  +payload: dict
  +render(self): str
}

class "handle_request" as handle_request <<function>> {
  +handle_request(request: Request, service: UserService | None = None): Response
}

class "stats" as stats <<function>> {
  +stats(request: Request, service: UserService): Response
}

class "build_service" as build_service <<function>> {
  +build_service(): UserService
}

class "delete_user" as delete_user <<function>> {
  +delete_user(request: Request, service: UserService): Response
}

class "user_id_from" as user_id_from <<function>> {
  +user_id_from(request: Request): int
}

class "health_check" as health_check <<function>> {
  +health_check(request: Request): Response
}

class "get_user" as get_user <<function>> {
  +get_user(user_id: int, service: UserService): Response
}

class "create_user" as create_user <<function>> {
  +create_user(request: Request, service: UserService): Response
}

class "promote_user" as promote_user <<function>> {
  +promote_user(user_id: int, scopes: list[str], service: UserService): Response
}

class "to_payload" as to_payload <<function>> {
  +to_payload(user: User): dict
}

class "handle_sync" as handle_sync <<function>> {
  +handle_sync(ids: list[int], service: SyncService): Response
}

class UserService <<external>> {
}

class Request <<external>> {
}

class User <<external>> {
}

class SyncService <<external>> {
}

handle_request ..> UserService : 依赖
handle_request ..> build_service : 依赖
handle_request ..> health_check : 依赖
handle_request ..> stats : 依赖
handle_request ..> create_user : 依赖
handle_request ..> delete_user : 依赖
handle_request ..> user_id_from : 依赖
handle_request ..> get_user : 依赖
handle_request ..> Response : 依赖
handle_request ..> Request : 依赖

stats ..> UserService : 依赖
stats ..> Response : 依赖
stats ..> Request : 依赖

build_service ..> UserService : 依赖
delete_user ..> UserService : 依赖
delete_user ..> Response : 依赖
delete_user ..> Request : 依赖
delete_user ..> user_id_from : 依赖
user_id_from ..> Request : 依赖
health_check ..> Response : 依赖
health_check ..> Request : 依赖
get_user ..> UserService : 依赖
get_user ..> Response : 依赖
get_user ..> to_payload : 依赖
create_user ..> UserService : 依赖
create_user ..> Response : 依赖
create_user ..> Request : 依赖
create_user ..> to_payload : 依赖
promote_user ..> UserService : 依赖
promote_user ..> Response : 依赖
to_payload ..> User : 依赖
handle_sync ..> SyncService : 依赖
handle_sync ..> Response : 依赖

note right of handle_request
  按请求路径分派到具体处理器；
  未匹配路径返回 404。
  UserService、Request、User、SyncService
  定义在其它模块，此处只作为空类框引用。
end note

note bottom of stats
  新增函数：调用 service.stats() 统计，
  total 为 0 时返回 empty 标记。
end note
@enduml
