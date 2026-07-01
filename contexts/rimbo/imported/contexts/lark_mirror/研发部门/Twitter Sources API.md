<!-- lark-mirror obj_token=Dt6Hdh3C0ougsrxHqmrjrcTNpLh space=研发部门 synced=2026-05-18T07:53:01Z -->

# Twitter Sources API

## 一、基础说明

- **Base Path**  
 后端对外路径统一以 `/api` 或 `/api/v1` 开头（下文均为完整路径）
- **鉴权**  
 除 Twitter OAuth callback 外，其余接口均需：
- Authorization: Bearer <token>
- **user_id**  
 前端无需传递，后端根据登录态自动注入
- **透传规则**  
 以下接口直接返回 ML 原生 payload，不做二次封装：

  - followings/sources
  - subscribe
  - channel sources
- **推荐创建频道接口**
- POST /api/v1/source-discovery/v1/subscribe

---

## 二、推荐流程

1. 获取 Twitter 授权地址
2. 用户完成授权（回调）
3. 获取关注列表（sources）
4. 用户选择 sources 创建频道
5. 管理频道信源

---

## 三、API 详情

### 发起 Twitter 授权

- **Method**: `GET`
- **Path**: `/api/twitter-io/v1/auth/login`
- **Auth**: 需要

#### 请求参数

<sheet sheet-id="ISfM5l" token="UeYHsgLxbhoTdUtyo8ojqCTIpLd"></sheet>

#### 响应示例

{

  "code": 0,

  "msg": "Success",

  "success": true,

  "data": {

    "authorization_url": "https://x.com/i/oauth2/authorize?...",

    "state": "xxxxx"

  }

}

---

### Twitter 授权回调

- **Method**: `GET`
- **Path**: `/api/twitter/v1/auth/callback`
- **Auth**: 不需要

> 说明：由 Twitter 自动回调

#### 请求参数

<sheet sheet-id="jVh219" token="UeYHsgLxbhoTdUtyo8ojqCTIpLd"></sheet>

#### 响应示例

{

  "code": 0,

  "msg": "Success",

  "success": true,

  "data": {

    "provider": "twitter",

    "user_id": "xxx",

    "account_email": null,

    "account_name": "Sam Altman",

    "metadata": {

      "username": "sama",

      "profile_image_url": "https://..."

    },

    "scopes": ["users.read", "tweet.read"],

    "ingested_documents": 0,

    "sync_status": "authorization_completed"

  }

}

---

### 获取关注列表（sources）

- **Method**: `POST`
- **Path**: `/api/twitter-io/v1/followings/sources`
- **Auth**: 需要

> 首次请求无需传 `twitter_username`

#### 请求示例

**首次请求**

{

  "page_size": 20

}

**分页请求**

{

  "cursor": "20",

  "page_size": 20

}

#### 响应示例

{

  "code": 0,

  "data": {

    "items": [

      {

        "source_id": "source-1",

        "name": "Sam Altman",

        "username": "sama",

        "icon_url": "https://...",

        "description": "OpenAI",

        "twitter_url": "https://x.com/sama"

      }

    ],

    "next_cursor": "20",

    "has_more": true,

    "total": 126

  }

}

---

### 创建频道

- **Method**: `POST`
- **Path**: `/api/v1/channel/subscribe/twitter`
- **Auth**: 需要

#### 请求体

{

  "topic": "科技博主论点",

  "source_ids": ["source-1", "source-2"],

  "description": "总结AI与创业观点"

}

#### 响应示例

{

  "code": 200,

  "data": {

    "channel_id": "xxx",

    "channel_name": "科技博主论点",

    "subscribed_count": 3,

    "twitter_source_ids": ["source-1", "source-2"]

  }

}

---

### 4.1 获取频道概览

- **Method**: `GET`
- **Path**: `/api/v1/channel/overview/twitter`
- **Auth**: 需要

{

  "code": 200,

  "data": {

    "channels": [

      {

        "channel_id": "ch_1",

        "title": "科技博主论点",

        "brief_summaries": ["...", "..."],

        "digest_state": "ready"

      }

    ]

  }

}

---

### 4.2 获取频道洞察

- **Method**: `GET`
- **Path**: `/api/v1/channel/{channel_id}/insights/twitter`

{

  "code": 200,

  "data": {

    "channel": {

      "channel_id": "ch_1",

      "title": "科技博主论点"

    },

    "signals": [

      {

        "order": 1,

        "brief_summary": "...",

        "detail_summary": "...",

        "grouped_feeds": []

      }

    ]

  }

}

---

### 4.3 获取作者分组（item_objects）

- **Method**: `GET`
- **Path**: `/api/v1/channel/{channel_id}/item-objects/twitter`

{

  "code": 200,

  "data": {

    "item_objects": [

      { "item_object": "@xxx", "count": 8 }

    ]

  }

}

---

### 4.4 获取作者下帖子

- **Method**: `GET`
- **Path**: `/api/v1/channel/{channel_id}/item-objects/twitter/items`

{

  "code": 200,

  "data": {

    "items": [

      {

        "item_id": "tweet_1",

        "content": "...",

        "media_urls": []

      }

    ]

  }

}

---

### 获取频道信源

- **Method**: `GET`
- **Path**:  
`/api/v1/source-discovery/v1/channels/{channel_id}/sources`

{

  "code": 200,

  "data": {

    "items": [

      {

        "source_id": "source-1",

        "name": "Sam Altman",

        "username": "sama"

      }

    ]

  }

}

---

### 批量添加信源

- **Method**: `POST`
- **Path**:  
`/api/v1/source-discovery/v1/channels/{channel_id}/sources/batch`

{

  "source_ids": ["source-1"]

}

{

  "code": 200,

  "data": {

    "added_count": 2,

    "invalid_source_ids": [],

    "already_attached_source_ids": []

  }

}

---

### 删除信源

- **Method**: `DELETE`
- **Path**:  
`/api/v1/source-discovery/v1/channels/{channel_id}/sources/{source_id}`

{

  "code": 200,

  "data": {

    "deleted": true

  }

}