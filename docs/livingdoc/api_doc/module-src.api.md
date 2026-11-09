## src.api

### health_check

- 签名：`health_check(request: Request) -> Response`
- 说明：健康检查处理器，直接返回 `200`，不访问任何仓储或服务对象。返回体包含固定的 `status` 字段与请求的 `path`。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| request | Request | 是 | 当前请求对象，仅使用其 `path` 属性填充返回体 |

- 返回值：`Response`，`status` 为 `200`，`payload` 为 `{"status": "ok", "path": request.path}`。
- 异常：无。

### user_id_from

- 签名：`user_id_from(request: Request) -> int`
- 说明：从 `/users/{id}` 形式的路径中取最后一段并转换为整数。转换失败时抛出 `NotFound`，并在消息中带上原始路径片段。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| request | Request | 是 | 当前请求对象，函数读取其 `path` 并用 `rstrip("/").rsplit("/", 1)[-1]` 取尾部片段 |

- 返回值：`int`，即路径尾部解析出的用户 id。
- 异常：`NotFound`，当尾部片段无法被 `int()` 解析时抛出，消息为 `bad user id {tail!r}`，并以原始 `ValueError` 作为 `__cause__`。

### delete_user

- 签名：`delete_user(request: Request, service: UserService) -> Response`
- 说明：停用指定用户，先通过 `user_id_from` 解析 id，再调用 `service.deactivate(user_id)`。重复停用不会报错，返回 `200` 且 `changed` 为 `false`。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| request | Request | 是 | 当前请求对象，用于解析路径中的用户 id |
| service | UserService | 是 | 用户服务实例，提供 `deactivate` 方法 |

- 返回值：`Response`，`status` 为 `200`，`payload` 为 `{"id": user_id, "changed": changed}`，其中 `changed` 为 `service.deactivate` 的返回结果。
- 异常：函数内部未捕获异常；`user_id_from` 抛出的 `NotFound` 会向上传播，由调用方 `handle_request` 捕获。

### handle_request

- 签名：`handle_request(request: Request, service: UserService | None = None) -> Response`
- 说明：请求入口，按路径与方法分派到具体处理器：`/health` 交给 `health_check`，`/users` 且方法为 `POST` 交给 `create_user`，以 `/users/` 开头且方法为 `DELETE` 交给 `delete_user`，其余以 `/users/` 开头的请求解析 id 后交给 `get_user`，都未命中时返回 `404`。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| request | Request | 是 | 当前请求对象，函数依据其 `path` 与 `method` 进行分派 |
| service | UserService \| None | 否 | 用户服务实例；不传时使用 `build_service()` 构建 |

- 返回值：`Response`，为被分派处理器的返回值；未匹配到任何路由时返回 `status` 为 `404`、`payload` 为 `{"error": "not found"}` 的响应。
- 异常：函数内捕获 `NotFound` 并返回 `404`（`payload` 为 `{"error": str(exc)}`）；捕获 `ServiceError`、`DomainError` 时先以 `logger.warning("request failed: %s", exc)` 记录，再返回 `500`（`payload` 为 `{"error": str(exc)}`）。

```python
resp = handle_request(request)          # 使用 build_service() 构建的服务
resp = handle_request(request, service) # 复用已有服务实例
```
