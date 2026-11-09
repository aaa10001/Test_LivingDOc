@startuml
title UserService.stats 时序图（模块 src.services，文件 src/services/user_service.py）

actor 调用方
participant UserService as svc
participant UserRepository as repo
participant AuditLog as audit

调用方 -> svc : stats()
activate svc
svc -> repo : count()
activate repo
repo --> svc : active
deactivate repo
svc -> repo : count(only_active=False)
activate repo
repo --> svc : total
deactivate repo
svc -> audit : recent(limit=5)
activate audit
audit --> svc : list[str]
deactivate audit
alt active < 0
  svc --> 调用方 : 抛出 ServiceError("negative active count")
else active >= 0
  svc --> 调用方 : {"active": active, "total": total, "recent": recent}
end
deactivate svc
note over svc : UserService 继承 BaseService，并以字段 repo、cache、audit 组合 UserRepository、TTLCache、AuditLog；本次 stats 只触达 repo 与 audit，未走 cache 与 retry。
@enduml
