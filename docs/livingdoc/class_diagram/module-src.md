@startuml
title 模块 src 类图（含 Calculator 与 format_result）

class Calculator {
  +history
  +__init__(history=None)
  +add(a: float, b: float): float
  +divide(a: float, b: float): float
}

class format_result {
  +format_result(value: float): str
}

Calculator ..> format_result : 依赖
note right of Calculator
  __init__ 中 history 为可选参数，
  缺省时初始化为空列表，用于记录运算历史。
  add 与 divide 都会把 (运算名, a, b, 结果) 追加到 history。
  divide 在 b == 0 时抛出 ZeroDivisionError。
end note

note bottom of format_result
  输入中仅给出顶层函数 format_result，
  源码中未出现对它的调用关系，故依赖箭头为推断关系。
  返回值保留两位小数的字符串。
end note
@enduml
