# 万相2.6参考生视频 (wan2.6-r2v-flash / wan2.6-r2v) HTTP异步调用 API参考

> 来源：https://help.aliyun.com/zh/model-studio/wan-video-to-video-api-reference

万相-参考生视频模型支持多模态输入（文本/图像/视频），可将人或物体作为主角，生成单角色表演或多角色互动视频。模型还支持智能分镜，生成多镜头视频。

## 模型信息

| 模型名称 | 默认分辨率 | 可选分辨率 | 说明 |
| --- | --- | --- | --- |
| wan2.6-r2v-flash | 1920*1080 | 720P、1080P | 支持自动配音；支持生成无声视频（需显式设置 `parameters.audio = false`） |
| wan2.6-r2v | 1920*1080 | 720P、1080P | 高质量版本，支持多角色互动与智能分镜 |

## 前提条件

已获取API Key并配置到环境变量 `DASHSCOPE_API_KEY`。

> **重要**：北京、新加坡和弗吉尼亚地域拥有独立的 API Key 与请求地址，不可混用。本文示例代码适用于北京地域。

## HTTP异步调用

参考生视频任务耗时较长（通常1-5分钟），API采用异步调用。流程包含 **"创建任务 → 轮询获取"** 两个步骤。

---

## 步骤1：创建任务获取任务ID

### Endpoint

- 北京地域：`POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- 新加坡地域：`POST https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- 弗吉尼亚地域：`POST https://dashscope-us.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`

> 创建成功后使用返回的 `task_id` 查询结果，task_id 有效期24小时。请勿重复创建任务。

### curl 示例

#### 多角色互动（参考图像和视频）

通过 `reference_urls` 传入图像和视频URL，同时设置 `shot_type` 为 `multi`，生成多镜头视频。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
  "model": "wan2.6-r2v-flash",
  "input": {
    "prompt": "Character2 坐在靠窗的椅子上，手持 character3，在 character4 旁演奏一首舒缓的美国乡村民谣。Character1 对Character2开口说道：\"听起来不错\"",
    "reference_urls": [
      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260129/hfugmr/wan-r2v-role1.mp4",
      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260129/qigswt/wan-r2v-role2.mp4",
      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260129/qpzxps/wan-r2v-object4.png",
      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260129/wfjikw/wan-r2v-backgroud5.png"
    ]
  },
  "parameters": {
    "size": "1280*720",
    "duration": 10,
    "audio": true,
    "shot_type": "multi",
    "watermark": true
  }
}'
```

#### 多角色互动（参考视频）

通过 `reference_urls` 传入多个视频URL，同时设置 `shot_type` 为 `multi`，生成多镜头视频。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
  "model": "wan2.6-r2v",
  "input": {
    "prompt": "character1对character2说: \"I'\''ll rely on you tomorrow morning!\" character2 回答: \"You can count on me!\"",
    "reference_urls": [
      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20251217/dlrrly/%E5%B0%8F%E5%A5%B3%E5%AD%A91%E8%8B%B1%E6%96%872.mp4",
      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20251217/fkxknn/%E9%93%83%E9%93%83.mp4"
    ]
  },
  "parameters": {
    "size": "1280*720",
    "duration": 10,
    "shot_type": "multi"
  }
}'
```

#### 单角色扮演

通过 `reference_urls` 传入单个视频URL，设置 `shot_type` 为 `multi`，生成多镜头视频。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
  "model": "wan2.6-r2v",
  "input": {
    "prompt": "character1一边喝奶茶，一边随着音乐即兴跳舞。",
    "reference_urls": ["https://cdn.wanx.aliyuncs.com/static/demo-wan26/vace.mp4"]
  },
  "parameters": {
    "size": "1280*720",
    "duration": 5,
    "shot_type": "multi"
  }
}'
```

#### 生成无声视频（仅 wan2.6-r2v-flash）

当生成无声视频时，必须显式设置 `parameters.audio = false`。

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
  "model": "wan2.6-r2v-flash",
  "input": {
    "prompt": "character1一边喝奶茶，一边随着音乐即兴跳舞。",
    "reference_urls": ["https://cdn.wanx.aliyuncs.com/static/demo-wan26/vace.mp4"]
  },
  "parameters": {
    "size": "1280*720",
    "duration": 5,
    "audio": false,
    "shot_type": "multi"
  }
}'
```

### 请求头（Headers）

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| Content-Type | string | 是 | 必须设置为 `application/json` |
| Authorization | string | 是 | 身份认证。示例值：`Bearer sk-xxxx` |
| X-DashScope-Async | string | **是** | 必须设置为 `enable`。缺少将报错 "current user api does not support synchronous calls" |

### 请求体（Request Body）

#### model (string, 必选)

模型名称。可选值：`wan2.6-r2v-flash`、`wan2.6-r2v`。

#### input (object, 必选)

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| prompt | string | 是 | 文本提示词。支持中英文，长度不超过1500个字符，超过自动截断。通过 "character1、character2" 等标识引用参考角色，每个参考（视频或图像）仅包含单一角色。 |
| negative_prompt | string | 否 | 反向提示词，描述不希望在视频中出现的内容。长度不超过500字符。示例：低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良等。 |
| reference_urls | array[string] | 是 | 参考文件URL数组，支持图像和视频，用于提取角色形象与音色。传入多个时按数组顺序定义角色（第1个对应 character1，第2个对应 character2，以此类推）。每个参考文件仅包含一个主体角色。 |

**reference_urls 数量限制：**
- 图像数量：0～5
- 视频数量：0～3
- 总数限制：图像 + 视频 ≤ 5

**支持输入的格式：**
- 公网URL：支持 HTTP 或 HTTPS 协议。示例：`https://cdn.translate.alibaba.com/xxx.png`
- 临时URL：支持OSS协议，须通过上传文件获取。示例：`oss://dashscope-instant/xxx/xxx.png`

**参考视频要求：**
- 格式：MP4、MOV
- 时长：1s～30s
- 文件大小：不超过100MB

**参考图像要求：**
- 格式：JPEG、JPG、PNG（不支持透明通道）、BMP、WEBP
- 分辨率：宽高均需在 [240, 5000] 像素之间
- 文件大小：不超过10MB

> **已废弃字段**：`reference_video_urls`（仅支持视频，最多3个），推荐使用 `reference_urls` 替代。

#### parameters (object, 可选)

| 参数 | 类型 | 必选 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| size | string | 否 | 1920*1080 | 视频分辨率，格式为 `宽*高`（如 `1280*720`），不可使用 `720P` 等别名。**size直接影响费用**，同一模型1080P > 720P。 |
| duration | integer | 否 | 5 | 视频时长（秒）。wan2.6-r2v-flash：[2, 10]；wan2.6-r2v：[2, 10]。**duration直接影响费用**。 |
| prompt_extend | bool | 否 | true | 是否开启提示词智能改写。 |
| shot_type | string | 否 | single | 镜头类型。`single`：连续单镜头；`multi`：智能分镜多镜头。 |
| audio | bool | 否 | true | 是否生成音频。仅 wan2.6-r2v-flash 支持此参数；设置 `false` 可生成无声视频。 |
| watermark | bool | 否 | false | 是否添加"AI生成"水印。 |
| seed | integer | 否 | 随机 | 随机数种子，取值 [0, 2147483647]。 |

**可选分辨率（size参数枚举值）：**

| 档位 | 分辨率 | 宽高比 |
| --- | --- | --- |
| 720P | 1280*720 | 16:9 |
| 720P | 720*1280 | 9:16 |
| 720P | 960*960 | 1:1 |
| 720P | 1088*832 | 4:3 |
| 720P | 832*1088 | 3:4 |
| 1080P | 1920*1080 | 16:9 |
| 1080P | 1080*1920 | 9:16 |
| 1080P | 1440*1440 | 1:1 |
| 1080P | 1632*1248 | 4:3 |
| 1080P | 1248*1632 | 3:4 |

### 创建任务响应

#### 成功响应示例

```json
{
  "request_id": "xxxxx-xxxxx",
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "PENDING"
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| request_id | string | 请求唯一标识 |
| output.task_id | string | 任务ID，用于轮询获取结果。有效期24小时。 |
| output.task_status | string | 任务状态：`PENDING` |

#### 异常响应

```json
{
  "request_id": "xxxxx",
  "code": "InvalidParameter",
  "message": "error details"
}
```

---

## 步骤2：轮询获取任务结果

### Endpoint

- 北京地域：`GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`
- 新加坡地域：`GET https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}`
- 弗吉尼亚地域：`GET https://dashscope-us.aliyuncs.com/api/v1/tasks/{task_id}`

### curl 示例

```bash
curl -X GET "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}" \
-H "Authorization: Bearer $DASHSCOPE_API_KEY"
```

### 请求头（Headers）

| 参数 | 类型 | 必选 | 说明 |
| --- | --- | --- | --- |
| Authorization | string | 是 | 身份认证。示例值：`Bearer sk-xxxx` |

### 成功响应示例（任务完成）

```json
{
  "request_id": "xxxxx-xxxxx",
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "SUCCEEDED",
    "task_metrics": {
      "TOTAL": 1,
      "SUCCEEDED": 1,
      "FAILED": 0
    },
    "video_url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/xxxx.mp4"
  },
  "usage": {
    "video_count": 1,
    "video_duration": 5,
    "video_ratio": "1080P"
  }
}
```

### 任务进行中响应示例

```json
{
  "request_id": "xxxxx-xxxxx",
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "RUNNING",
    "task_metrics": {
      "TOTAL": 1,
      "SUCCEEDED": 0,
      "FAILED": 0
    }
  }
}
```

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| request_id | string | 请求唯一标识 |
| output.task_id | string | 任务ID |
| output.task_status | string | 任务状态：`PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED` |
| output.task_metrics | object | 任务统计（TOTAL/SUCCEEDED/FAILED） |
| output.video_url | string | 生成视频的URL（仅SUCCEEDED时返回），有效期24小时，请及时下载 |
| output.code | string | 错误码（仅FAILED时返回） |
| output.message | string | 错误信息（仅FAILED时返回） |
| usage.video_count | integer | 生成视频数量 |
| usage.video_duration | integer | 视频时长（秒） |
| usage.video_ratio | string | 视频分辨率 |
