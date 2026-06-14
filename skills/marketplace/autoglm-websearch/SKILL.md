---
name: autoglm-websearch
description: >
  使用 AutoGLM Web Search 接口进行网络信息搜索。当用户需要联网搜索、查询最新资讯、检索网页内容或获取实时信息时使用此 skill。
  Token 通过本地服务 http://127.0.0.1:53699/get_token 自动获取，无需手动配置环境变量。
compatibility:
  requires:
    - Python 3、hashlib（内置）
---

# AutoGLM WebSearch Skill

调用 AutoGLM Web Search API 进行网络搜索。

---

## Token 获取

脚本启动时自动向本地服务发起 HTTP GET 请求获取 token：

| 项目 | 内容 |
|------|------|
| 地址 | `http://127.0.0.1:53699/get_token` |
| 方式 | GET |
| 返回 | `Bearer xxx`（直接作为 Authorization 头使用） |

> 若返回值不含 `Bearer` 前缀，脚本会自动补全。

---

## Search API

| 项目 | 内容 |
|------|------|
| 地址 | `https://autoglm-api.zhipuai.cn/agentdr/v1/assistant/skills/web-search` |
| 方式 | POST |
| 请求体 | `{"queries": [{"query": "<搜索词>"}]}` |

**签名 Headers（每次动态生成）：**

- `X-Auth-Appid`: `100003`
- `X-Auth-TimeStamp`: 当前秒级 Unix 时间戳
- `X-Auth-Sign`: MD5(`100003 + "&" + timestamp + "&" + 38d2391985e2369a5fb8227d8e6cd5e5`)

---

## 执行脚本

使用同目录下的 `websearch.py`：

```bash
python websearch.py "搜索关键词"
```

---

## 返回结果处理

### 响应结构

```json
{
  "code": 0,
  "msg": "SUCCESS",
  "data": {
    "results": [
      {
        "webPages": {
          "value": [
            {
              "name": "页面标题",
              "url": "页面链接",
              "snippet": "摘要内容"
            }
          ]
        }
      }
    ]
  }
}
```

### 输出要求

**1. 总结搜索内容**
基于所有条目的 `snippet` 字段，提炼出与用户 query 相关的核心信息，用自然语言组织成简洁的回答。

**2. 附加引用列表**
在回答末尾附上参考来源：

```
**参考来源：**
1. [页面标题](页面链接)
2. [页面标题](页面链接)
```