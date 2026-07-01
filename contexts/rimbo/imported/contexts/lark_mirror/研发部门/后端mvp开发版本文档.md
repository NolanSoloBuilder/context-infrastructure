<!-- lark-mirror obj_token=OI1odzrjpofw8fx2S2Oju4vBpnf space=研发部门 synced=2026-05-18T07:53:01Z -->

# 后端mvp开发版本文档

以下接口都需要:

auth token (用户登录获取)

base_url (https://mindspace.click)

### 确定名字的路由 

POST /api/v1/m/user/profile/update

请求：

```Plain Text
{
    "username": "xxx" #更新的名字
}
```

返回：

```Plain Text
    {
      "code": 0,
      "success": true,
      "msg": "Update user profile success",
      "data": {
        "id": "680df3a962b2171f53edb535",
        "email": "user@example.com",
        "avatar": "http://motherfucker/podnoteresource/default-avatar.jpeg",
        "username": "newusername",
        "connectedAccounts": [],
        "onboardingAnswers": []
      }
    }
```

### 开启卡片生成

POST /api/card/task/create

```Plain Text
{
    "user_name": "这个还是需要前端传过来的"
}
```

返回：

```JSON
{
  "code": 0,
  "msg": "accepted",
  "data": {
    "task_id": "task_20251114_001",
    "status": "pending" 
  }
}

```

### 获取卡片生成完成的任务。 

GET /api/card/task/status?task_id=xxx

返回：

```JSON
{    ## 这里面可以直接获取卡片详情
    "code": 0,
    "msg": "success",
    "data": {
      "job_id": "a5f7e8d0-1c2b-4d3e-8f9a-0123456789ab",
      "group_id": "card_group_20251114_ab1234",
      "user_id": "user_xxx",
      "user_name": "Ethan",
      "date": "2025-11-14",
      "status": "success",
      "welcome_message": "Good morning, Ethan…",
      "sections": [
        {
          "section_id": "page_title",
          "blocks": [
            { "component": "PageTitle", "data": { "context": "Fri, Nov 14" } }
          ]
        },
        {
          "section_id": "persona_article",
          "blocks": [
            {
              "component": "PageText",
              "data": { "context": "每个版块的导语" }
            },
            {
              "component": "ArticleCardList",
              "data": {
                "context": [
                  {
                    "card_id": "persona_article_001",              
                    "card_type": "persona-article",
                    "chat_session_id": "当创建对话的时候更新这个字段",
                    "cover": "https://…",
                    "title": "How AI Will Transform Your Workflow in 2026",
                    "brief": "A personalized insight based on your activity and interests.",
                    "artical": "AI-driven automation…",
                    "sources": [
                      {
                        "title": "McKinsey: Future of Knowledge Work",
                        "source_name": "这里是指site name",
                        "url": "https://example.com/mckinsey…",
                        "snippet": "AI is expected to automate…",
                        "full_text": "来源全文…",
                        "referenceId": "slink_1_1",
                        "icon": "mckinsey",
                        "image_list": ["里面是图片列表"]
                        "receivedAt": "2025-11-14T02:34:00Z"
                      }
                    ]
                  }
                ]
              }
            }
          ]
        },
        {
          "section_id": "gmail_article",
          "blocks": [
            {
              "component": "PageText",
              "data": { "context": "Good morning, Ethan…" }
            },
            {
              "component": "ArticleCardList",
              "data": {
                "context": [
                  {
                    "card_id": "gmail_digest_20251114_001",
                    "card_type": "gmail-digest",
                    "chat_session_id": "当创建对话的时候更新这个字段",
                    "cover": "https://…",
                    "title": "8 viral hits you missed this week…",
                    "brief": null,
                    "artical": "Your inbox this period mainly contains…",
                    "sources": [
                      {
                        "title": "8 viral hits you missed this week",
                        "source_name": "",
                        "url": null,
                        "snippet": "Weekly curation…",
                        "full_text": "Full email content…",
                        "referenceId": null,
                        "icon": null,
                        "image_list": ["里面是图片列表"]，
                        "receivedAt": "2025-11-14T02:34:00Z"
                      }
                    ]
                  }
                ]
              }
            }
          ]
        },
        {
          "section_id": "follow_recommended",
          "blocks": [
            {
              "component": "PageText",
              "data": {
                "context": "Here are the key sources to follow…"
              }
            },
            {
              "component": "FollowList",
              "data": { "context": [] }
            }
          ]
        },
        {
          "section_id": "chat_input",
          "blocks": [
            {
              "component": "PageText",
              "data": {
                "context": "That’s a wrap for today…"
              }
            },
            {
              "component": "AIChatInput",
              "data": { "placeholderText": "I want to know more about..." }
            }
          ]
        }
      ],
      "persona_cards_count": 3,
      "gmail_emails_count": 1,
      "error_msg": null,
      "created_at": "2025-11-14T01:00:00+00:00",
      "updated_at": "2025-11-14T01:04:00+00:00",
      "finished_at": "2025-11-14T01:04:00+00:00"
    }
  }
```

### 获取卡片组列表的接口

POST /api/card/task/list

参数：

```Plain Text
{
    "page":1,
    "page_size": 20
}
```

返回：

```Plain Text
    1 {
    2     "code": 0,
    3     "msg": "Success",
    4     "data": {
    5         "page": 1,
    6         "page_size": 20,
    7         "total": 5,
    8         "items": [
    9             {
   10                 "task_id": "95e3b8f2-1234-4567-8901-abcdef123456",
   11                 "card_group_id": "card_group_20251120_a1b2c3",
   12                 "user_id": "user_12345",
   13                 "user_name": "User Name",
   14                 "date": "2025-11-20",
   15                 "status": "SUCCESS",
   16                 "welcome_message": "Here is your summary for today...",
   17                 "cards": [  
   18                     // 这里的结构取决于 sections 字段原本存的 JSON 内容
   19                     {
   20                         "title": "Gmail Summary",
   21                         "summary": "You have 5 new emails...",
   22                         "items": [...]
                           ...
   23                     },
   24                     {
   25                         "title": "Twitter Updates",
   26                         "summary": "Top tweets from your network..."
                              ...
   27                     }
   28                 ],
   29                 "persona_cards_count": 3,
   30                 "gmail_emails_count": 10,
   31                 "error_msg": null,
   32                 "created_at": "2025-11-20T10:00:00+00:00",
   33                 "updated_at": "2025-11-20T10:05:00+00:00",
   34                 "finished_at": "2025-11-20T10:05:00+00:00"
   35             },
   36             {
   37                 "task_id": "...",
   38                 "card_group_id": "...",
   39                 "status": "PROCESSING",
   40                 // ... 其他字段
   41                 "cards": null // 处理中可能为空
   42             }
   43         ]
   44     },
   45     "success": true
   46 }   
```

### 获取某一张卡片的详情接口

GET /api/card/detail

请求：

```Plain Text
card_id
```

返回：

```Plain Text
    1 {
    2   "code": 200,
    3   "msg": "success",
    4   "data": {
    5     "card_id": "dyn-3a6cf478-xxxx...",
    6     "card_type": "persona-article",
    7     "title": "构建更可持续的第二大脑",
    8     "brief": "围绕 Mindspace 用户的人设...",
    9     "artical": "### 1. 正文内容\n这里是具体的 Markdown 内容...", 
   10     "cover": "https://cdn.mindspace.com/image.png",
   11     "chat_session_id": "session-12345",
   12     "metadata": {
   13       "queryLabel": "知识管理",
   14       "queryText": "second brain workflow",
   15       "layout": "persona-article"
   16     },
   17     "sources": [
   18       {
   19         "referenceId": "slink_1_1",
   20         "title": "How to maintain...",
   21         "source_name": "Cloudsway",
   22         "url": "https://...",
   23         "snippet": "摘要内容...",
   24         "full_text": "完整内容...",
   25         "receivedAt": "2025-11-11T10:00:00Z",
   26         "icon": "https://...",
   27         "image_list": ["http://..."]
   28       }
   29     ]
   30   }
   31 }

```

### 创建新会话接口

GET /api/chat/session/create?type=chat

type 设置为chat的时候就是普通对话

type 设置为chat-card的时候就是卡片对话

type 设置为chat-guide的时候就是引导对话

创建卡片会话的时候：

GET /api/chat/session/create?type=chat-card&card_id=dyn-123456...

返回：

```Plain Text
{
    "code":0,
    "msg": "success",
    "data":
        {
        chat_session_id: "xxxx"
    }
    
}
```

### 通过对话更新用户画像

POST /api/chat//update_profile_from_converstion

请求：

```Plain Text
{
    "chat_session_id": "xxxx"
}
```

返回：

```JSON
{
    "code": 200,
    "msg": "Profile updated successfully",
    "data": {
      "message": "Profile updated successfully"
    },
    "success": true
}
```

### 每日卡片历史记录管理

POST /api/card/task/list

请求：

```Plain Text
{
  "page": 1,
  "page_size": 20
}
```

返回：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "page": 1,
    "page_size": 20,
    "total": 53,
    "items": [
      {
        "task_id": "…",          // 即 task_id，用这个去获取卡片的具体信息，
        "group_id": "card_group_…",
        "user_id": "…",
        "user_name": "…",
        "date": "2025-11-14",
        "status": "success",
        "welcome_message": "…",
        "sections": [ ... ],    // 成功时已经包含完整卡片协议
        "persona_cards_count": 3,
        "gmail_emails_count": 1,
        "error_msg": null,
        "created_at": "…",
        "updated_at": "…",
        "finished_at": "…"
      },
      ...
    ]
  }
```

### chat对话接口

POST /api/chat/stream

请求：

```JSON
{
  "chat_session_id": "会话id",
  "messages": "用户输入的文本",
  "card_id": "卡片结构里面有"
}
```

<sheet sheet-id="PdbOI8" token="MWeys3F1qhmqpZtFwX6jfj4Tp6b"></sheet>

返回：

```ProtoBuf
SSE 返回格式（text/event-stream）：

event: message
data: {"type":"start", "session_id":"xxx"}

event: message
data: {"type":"assistant_chunk", "delta":"你好"}

event: message
data: {"type":"assistant_chunk", "delta":"啊"}

event: message
data: {"type":"references", "references":[ ... ]}

event: message
data: {"type":"assistant_message", "content":"你好，我是你的AI助手。"}


event: message
data: {"type":"done"}

```

引用references：

```JSON
{
  "type": "references",
  "references": [
    {
      "title": "McKinsey: Future of Knowledge Work",
      "url": "https://example.com/mckinsey",
      "chunk_text": "AI is expected to automate...",
      "referenceId": "slink_1_1",
      "icon": "mckinsey"
    },
    {
      "title": "OpenAI: Productivity 2025",
      "url": "https://example.com/openai",
      "chunk_text": "LLMs will influence...",
      "referenceId": "slink_2_1",
      "icon": "openai"
    }
  ]
}

```

### 会话历史记录列表接口

GET /api/chat/session/list

参数：

```Plain Text
"page": 1,
"page_size": 20
```

返回：

```JSON
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 3, 
    "sessions": [
      {
        "chat_session_id": "chat_20251113_001",
        "type": "chat", 
        "card_id": null,
        "image": "https://s3mindspace...aws.com". #用来在左边区分普通对话还是卡片对话
        "snippet": "好的，我已经为你总结如下……",
        "updated_at": "2025-11-13T08:30:00Z"
      },
      {
        "chat_session_id": "chat_20251112_002",
        "type": "chat-card",
        "card_id":"xxxx",
        "image": "https://s3mindspace...aws.com"
        "snippet": "你的 Gmail digest 已更新，本期主要内容包括……",
        "updated_at": "2025-11-12T07:15:00Z"
      },
      {
        "chat_session_id": "chat_20251110_005",
        "type": "chat",
        "card_id": null,
        "image": "https://s3mindspace...aws.com"
        "snippet": "当然可以，我来继续回答你的问题。",
        "updated_at": "2025-11-10T13:21:44Z"
      }
    ]
  }
}

```

### 会话历史记录接口(普通的chat和带卡片的chat共用一个历史会话记录)

GET /api/chat/session/{chat_session_id}/messages

返回

```JSON
{
    "code": 0,
    "msg": "Success",
    "data": {
        "chat_session_id": "14726477df5844348805a60cd3816aec",
        "type": "chat",
        "image": "https://s3mindspace.s3.amazonaws.com/assets/chat_icon.png",
        "updated_at": "2025-11-20T05:13:01Z",
        "context": {
            "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
            "group_id": "card_group_20251120_8ef259"
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "需要你提供要总结的内容。",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "请提供需要总结的内容。",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "我需要你给出要总结的内容，才能进行总结。",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "需要被总结的内容。请发给我。",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "请提供要总结的内容。",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "总结一下",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "内容总结：\n\n• 有人建议苹果加入“我是高级用户”模式，让用户在电脑上获得更高自由度。  \n• 后半部分是苹果开发者计划的流程：提交组织信息、等待审核、通过后在 Apple Developer app 中完成注册、同意协议、支付年费；年费自动续订，礼品卡余额不能用于支付，可使用组织信用卡；订阅可在续期前一天取消，已付年费不退。",
                        "type": "text"
                    }
                ],
                "card_id": "dyn-8dc55cc972fc4cbab4bef57dc581839d",
                "group_id": "card_group_20251120_8ef259"
            }
        ]
    },
    "success": true
}
```