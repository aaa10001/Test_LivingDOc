## src.api

### stats

- 签名：`def stats(request: Request, service: UserService) -> Response`
- 说明：运维面板接口，调用 `service.stats()` 获取计数并返回用户总数与活跃数；当用户总数为 0 时返回空状态标记。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| request | Request | 是 | 当前请求对象，函数体中未直接使用 |
| service | UserService | 是 | 用户服务实例，用于调用 `stats()` 获取计数 |

- 返回值：返回 `Response`，状态码固定为 200；`payload` 在总数为 0 时为 `{"total": 0, "empty": True}`，否则为 `{"total": counts["total"], "active": counts["active"]}`。
- 异常：代码中未显式抛出异常；若 `service.stats()` 内部抛出 `ServiceError` 或 `DomainError`，由调用方 `handle_request` 捕获处理。

### handle_request

- 签名：`def handle_request(request: Request, service: UserService | None = None) -> Response`
- 说明：请求入口，按 `request.path` 与 `request.method` 分派到 `health_check`、`stats`、`create_user`、`delete_user`、`get_user` 等具体处理器；未匹配到任何路由时返回 404。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| request | Request | 是 | 待处理的请求对象，依据其 `path` 与 `method` 进行路由分派 |
| service | UserService \| None | 否 | 用户服务实例；未提供时调用 `build_service()` 构建 |

- 返回值：返回 `Response`。`/health` 返回健康检查结果；`/stats` 返回统计信息；`POST /users` 创建用户；`DELETE /users/` 前缀路径删除用户；其他 `/users/` 前缀路径按用户 ID 查询用户；无匹配路由时返回状态码 404 与 `{"error": "not found"}`。
- 异常：捕获 `NotFound` 并返回状态码 404 与错误信息；捕获 `ServiceError`、`DomainError`，记录 `logger.warning` 后返回状态码 500 与错误信息。
