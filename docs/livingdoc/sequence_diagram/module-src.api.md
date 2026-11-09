@startuml
title handle_request 时序图（模块 src/api/routes.py）

actor 调用方
participant handle_request as entry
participant build_service as bs
participant health_check as hc
participant create_user as cu
participant delete_user as du
participant user_id_from as uid
participant get_user as gu
participant to_payload as tp
participant Response as resp

调用方 -> entry : handle_request(request, service)
activate entry
entry -> entry : svc = service or build_service()
opt service 为空
  entry -> bs : build_service()
  activate bs
  bs --> entry : svc
  deactivate bs
end
group 异常处理
  alt request.path == "/health"
    entry -> hc : health_check(request)
    activate hc
    hc --> entry : Response(status=200, payload)
    deactivate hc
  else request.path == "/users" 且 request.method == "POST"
    entry -> cu : create_user(request, svc)
    activate cu
    cu -> tp : to_payload(user)
    activate tp
    tp --> cu : dict
    deactivate tp
    cu --> entry : Response
    deactivate cu
  else request.path 以 "/users/" 开头 且 request.method == "DELETE"
    entry -> du : delete_user(request, svc)
    activate du
    du -> uid : user_id_from(request)
    activate uid
    uid --> du : user_id
    deactivate uid
    du --> entry : Response(status=200, payload)
    deactivate du
  else request.path 以 "/users/" 开头
    entry -> uid : user_id_from(request)
    activate uid
    alt tail 可转为 int
      uid --> entry : user_id
    else ValueError
      uid --> entry : 抛出 NotFound
    end
    deactivate uid
    entry -> gu : get_user(user_id, svc)
    activate gu
    gu -> tp : to_payload(user)
    activate tp
    tp --> gu : dict
    deactivate tp
    gu --> entry : Response
    deactivate gu
  else 其他路径
    entry --> 调用方 : Response(status=404, payload)
  end
else 捕获 NotFound
  entry --> 调用方 : Response(status=404, payload)
else 捕获 ServiceError 或 DomainError
  entry -> entry : logger.warning("request failed: %s", exc)
  entry --> 调用方 : Response(status=500, payload)
end
deactivate entry
note over entry
  输入未给出 Response.render 的调用点与 ServiceError、DomainError、NotFound 的定义位置
  因此这些内容未画入时序图
end note
@enduml
