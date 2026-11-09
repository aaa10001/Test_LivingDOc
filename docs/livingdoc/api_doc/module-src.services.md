## src.services

### UserService.stats

- 签名：`def stats(self) -> dict[str, int]`
- 说明：返回当前用户总数与最近审计条数，供运维面板使用。方法通过 `self.repo.count()` 统计活跃用户数、通过 `self.repo.count(only_active=False)` 统计全部用户数，并用 `len(self.audit.recent(limit=5))` 取得最近 5 条审计记录的数量。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| 无 | 无 | 否 | 该方法除 `self` 外不接受任何参数 |

- 返回值：返回 `dict[str, int]`，包含三个键：`active`（活跃用户数）、`total`（全部用户数）、`recent`（最近审计条数，取自 `self.audit.recent(limit=5)` 的长度）。
- 异常：当 `active < 0` 时抛出 `ServiceError("negative active count")`。
