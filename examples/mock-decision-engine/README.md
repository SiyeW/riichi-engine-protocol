# 示例决策引擎

一个只依赖 Python 标准库的 `decision-v1` 最小实现，用于测试引擎包、合法候选动作和状态通知。它只用于协议测试，不提供实际的对局分析。

## 构建

在仓库根目录运行：

```powershell
.\setup-environment.ps1
.\examples\mock-decision-engine\build.ps1
```

输出目录：`examples/mock-decision-engine/runtime/`

构建后的目录可作为引擎包交给兼容的主程序加载。

## 行为

示例引擎会为每个合法候选生成固定的原始值和 Softmax 概率，并选择最后一个候选。它支持握手、初始化、状态查询、分析、会话重置、重新加载和关闭，可用于测试多会话隔离、合法动作校验、状态通知和缓存失效。
