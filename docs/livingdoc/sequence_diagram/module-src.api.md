@startuml
title handle_request 时序图（模块 src.api，文件 src/api/routes.py）

actor 调用方
participant handle_request
participant build_service
participant health_check
participant stats
participant create_user
participant delete_user
participant user_id_from
participant get_user
participant to_payload
participant UserService
participant Response

调用方 -> handle_request : handle_request(request, service=None)
activate handle_request

alt service 为空
  handle_request -> build_service : build_service()
  activate build_service
  build_service --> handle_request : svc: UserService
  deactivate build_service
else service 已传入
  note right of handle_request : svc = service，不调用 build_service()
end

group 异常处理 try 块
  alt request.path == "/health"
    handle_request -> health_check : health_check(request)
    activate health_check
    health_check -> Response : Response(status=200, payload=...)
    activate Response
    Response --> health_check : 健康检查响应
    deactivate Response
    health_check --> handle_request : Response
    deactivate health_check
  else request.path == "/stats"
    handle_request -> stats : stats(request, svc)
    activate stats
    stats -> UserService : stats()
    activate UserService
    UserService --> stats : counts
    deactivate UserService
    alt counts["total"] == 0
      stats -> Response : Response(status=200, payload={"total": 0, "empty": True})
      activate Response
      Response --> stats : 空面板响应
      deactivate Response
    else counts["total"] != 0
      stats -> Response : Response(status=200, payload={"total": ..., "active": ...})
      activate Response
      Response --> stats : 计数面板响应
      deactivate Response
    end
    stats --> handle_request : Response
    deactivate stats
  else request.path == "/users" 且 request.method == "POST"
    handle_request -> create_user : create_user(request, svc)
    activate create_user
    create_user -> UserService : register(...)
    activate UserService
    UserService --> create_user : user
    deactivate UserService
    alt 注册结果满足条件
      create_user -> to_payload : to_payload(user)
      activate to_payload
      alt user 存在
        to_payload --> create_user : dict
      else user 为空
        to_payload --> create_user : 空 dict
      end
      deactivate to_payload
      create_user -> Response : Response(status=201, payload=...)
      activate Response
      Response --> create_user : 创建成功响应
      deactivate Response
    else 注册结果不满足条件
      create_user -> Response : Response(status=400, payload=...)
      activate Response
      Response --> create_user : 创建失败响应
      deactivate Response
    end
    create_user --> handle_request : Response
    deactivate create_user
  else request.path 以 "/users/" 开头 且 request.method == "DELETE"
    handle_request -> delete_user : delete_user(request, svc)
    activate delete_user
    delete_user -> user_id_from : user_id_from(request)
    activate user_id_from
    group 异常处理 try/except
      alt 解析成功
        user_id_from --> delete_user : user_id: int
      else 解析失败
        user_id_from --> delete_user : 抛出异常
      end
    end
    deactivate user_id_from
    delete_user -> UserService : deactivate(user_id)
    activate UserService
    UserService --> delete_user : 无返回值
    deactivate UserService
    delete_user -> Response : Response(status=200, payload=...)
    activate Response
    Response --> delete_user : 删除响应
    deactivate Response
    delete_user --> handle_request : Response
    deactivate delete_user
  else request.path 以 "/users/" 开头
    handle_request -> user_id_from : user_id_from(request)
    activate user_id_from
    group 异常处理 try/except
      alt 解析成功
        user_id_from --> handle_request : user_id: int
      else 解析失败
        user_id_from --> handle_request : 抛出异常
      end
    end
    deactivate user_id_from
    handle_request -> get_user : get_user(user_id, svc)
    activate get_user
    get_user -> UserService : load(user_id)
    activate UserService
    UserService --> get_user : user
    deactivate UserService
    get_user -> to_payload : to_payload(user)
    activate to_payload
    alt user 存在
      to_payload --> get_user : dict
    else user 为空
      to_payload --> get_user : 空 dict
    end
    deactivate to_payload
    get_user -> Response : Response(status=200, payload=...)
    activate Response
    Response --> get_user : 查询响应
    deactivate Response
    get_user --> handle_request : Response
    deactivate get_user
  else 其他路径
    handle_request -> Response : Response(status=404, payload={"error": "not found"})
    activate Response
    Response --> handle_request : 404 响应
    deactivate Response
  end
end

alt 抛出 NotFound
  handle_request -> Response : Response(status=404, payload={"error": str(exc)})
  activate Response
  Response --> handle_request : 404 响应
  deactivate Response
else 抛出 ServiceError 或 DomainError
  handle_request -> handle_request : logger.warning("request failed: %s", exc)
  handle_request -> Response : Response(status=500, payload={"error": str(exc)})
  activate Response
  Response --> handle_request : 500 响应
  deactivate Response
end

handle_request --> 调用方 : Response
deactivate handle_request

note over handle_request : create_user 与 delete_user 内部的 if 条件、以及 register/load 的参数细节在输入中未给出
@enduml
