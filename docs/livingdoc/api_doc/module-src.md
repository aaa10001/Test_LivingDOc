## src

### Calculator.__init__

- 签名：`def __init__(self, history=None)`
- 说明：构造 `Calculator` 实例，将传入的 `history` 保存到 `self.history`；当 `history` 为假值（例如 `None`）时改用空列表。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `history` | 代码中未体现 | 否 | 初始历史记录，默认值为 `None`；为假值时使用 `[]` 初始化 `self.history` |

- 返回值：无返回值。
- 异常：无。

### Calculator.add

- 签名：`def add(self, a: float, b: float) -> float`
- 说明：计算 `a` 与 `b` 之和，并把 `("add", a, b, result)` 追加到 `self.history` 后返回结果。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `a` | `float` | 是 | 加数 |
| `b` | `float` | 是 | 被加数 |

- 返回值：`float`，即 `a + b` 的计算结果。
- 异常：无。

### Calculator.divide

- 签名：`def divide(self, a: float, b: float) -> float`
- 说明：当 `b` 为 `0` 时抛出异常；否则计算 `a / b`，并把 `("divide", a, b, result)` 追加到 `self.history` 后返回结果。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `a` | `float` | 是 | 被除数 |
| `b` | `float` | 是 | 除数，不能为 `0` |

- 返回值：`float`，即 `a / b` 的计算结果。
- 异常：当 `b == 0` 时抛出 `ZeroDivisionError`，消息为 `cannot divide by zero`。

### format_result

- 签名：`def format_result(value: float) -> str`
- 说明：将数值按保留两位小数的格式拼接为字符串返回。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `value` | `float` | 是 | 需要格式化的数值 |

- 返回值：`str`，即形如 `f"{value:.2f}"` 的两位小数字符串。
- 异常：无。
