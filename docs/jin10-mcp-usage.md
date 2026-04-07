# 金十数据 MCP 服务使用指南

## 配置完成

✅ 金十数据 MCP 服务已成功添加到 deer-flow。

**配置文件**：`G:\docker\deer-flow\extensions_config.json`

**服务名称**：`jin10`

## 可用工具

### 1. 实时行情
- **工具名称**：`get_quote`
- **参数**：`{ code }`
- **示例**：查询现货黄金价格
  - 工具：`get_quote`
  - 参数：`{ "code": "XAUUSD" }`

**常用品种代码**：
- `XAUUSD`：现货黄金
- `XAGUSD`：现货白银
- `USOIL`：WTI 原油
- `UKOIL`：布伦特原油
- `COPPER`：现货铜
- `USDJPY`：美元/日元
- `EURUSD`：欧元/美元
- `USDCNH`：美元/人民币

### 2. 快讯列表
- **工具名称**：`list_flash`
- **参数**：`{ cursor? }`（可选分页参数）
- **示例**：获取最新快讯
  - 工具：`list_flash`
  - 参数：`{}`

### 3. 搜索快讯
- **工具名称**：`search_flash`
- **参数**：`{ keyword }`
- **示例**：搜索关于"黄金"的快讯
  - 工具：`search_flash`
  - 参数：`{ "keyword": "黄金" }`

### 4. 资讯列表
- **工具名称**：`list_news`
- **参数**：`{ cursor? }`（可选分页参数）
- **示例**：获取最新资讯
  - 工具：`list_news`
  - 参数：`{}`

### 5. 搜索资讯
- **工具名称**：`search_news`
- **参数**：`{ keyword, cursor? }`
- **示例**：搜索关于"美联储"的资讯
  - 工具：`search_news`
  - 参数：`{ "keyword": "美联储" }`

### 6. 资讯详情
- **工具名称**：`get_news`
- **参数**：`{ id }`
- **示例**：获取单篇资讯详情
  - 工具：`get_news`
  - 参数：`{ "id": "news_id" }`

### 7. 财经日历
- **工具名称**：`list_calendar`
- **参数**：`{}`
- **示例**：获取财经日历数据
  - 工具：`list_calendar`
  - 参数：`{}`

### 8. 获取支持的报价品种
- **资源名称**：`quote://codes`
- **说明**：获取所有支持的报价品种代码列表

## 推荐调用方式

### 场景 1：查询某个品种的实时价格
1. 如果需要，先读取 `quote://codes` 确认品种代码
2. 调用 `get_quote({ "code": "XAUUSD" })`

### 场景 2：获取某个主题的最新快讯
直接调用 `search_flash({ "keyword": "黄金" })`

如果要浏览最新快讯流，调用 `list_flash({})`，然后按 `next_cursor` 翻页

### 场景 3：获取某个主题的深度文章
1. 调用 `search_news({ "keyword": "美联储" })` 或 `list_news({})`
2. 拿到 `id` 后，再调用 `get_news({ "id": "news_id" })`

### 场景 4：查看财经日历
直接调用 `list_calendar({})`

## 关键词示例

- 黄金、原油、美联储、日元、通胀、非农
- 日本央行、欧佩克、欧洲央行、英国央行

## 数据返回格式

### 行情数据
```json
{
  "code": "XAUUSD",
  "name": "现货黄金",
  "time": "2026-03-31 12:00:00",
  "open": 2000.00,
  "close": 2010.00,
  "high": 2015.00,
  "low": 1995.00,
  "volume": 1000000,
  "ups_price": 10.00,
  "ups_percent": 0.50
}
```

### 快讯/资讯列表
```json
{
  "items": [...],
  "next_cursor": "next_page_token",
  "has_more": true
}
```

### 文章详情
```json
{
  "id": "news_id",
  "title": "文章标题",
  "introduction": "文章简介",
  "time": "2026-03-31 12:00:00",
  "url": "https://...",
  "content": "文章内容"
}
```

### 财经日历
```json
[
  {
    "pub_time": "2026-03-31 12:00:00",
    "star": 3,
    "title": "美国非农就业数据",
    "previous": "150000",
    "consensus": "155000",
    "actual": "152000",
    "revised": null,
    "affect_txt": "影响美元走势"
  }
]
```

## 错误处理

- 如果返回 `isError=true`，按工具业务错误处理
- 如果返回 JSON-RPC `error`，按协议错误处理
- 不要传未声明参数；例如分页请传 `cursor`，不要再传 `offset`

## 分页说明

所有列表工具都支持分页：
- 请求参数：`cursor`（上一页的 next_cursor）
- 响应字段：`data.next_cursor`（下一页的游标）
- 是否还有更多：`data.has_more`（布尔值）

## 测试建议

可以在 deer-flow 的智能体对话中尝试以下问题：
1. "现货黄金现在多少钱？"
2. "最新的黄金快讯有哪些？"
3. "搜索关于美联储的最新资讯"
4. "今天的财经日历有什么重要数据？"

## 注意事项

1. 该服务已按严格 MCP 客户端方式验证
2. 所有工具均返回 `structuredContent`
3. 推荐协议版本：`2025-11-25`
4. 结果读取时优先使用 `result.structuredContent`
5. `result.content` 只作为可读文本补充，不要作为主要机器解析来源

## 相关文档

- [MCP 官方文档](https://modelcontextprotocol.io)
- [DeerFlow MCP 配置文档](https://github.com/vincentsen1994/deer-flow/blob/main/backend/docs/MCP_SERVER.md)
