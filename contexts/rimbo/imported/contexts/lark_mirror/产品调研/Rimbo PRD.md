<!-- lark-mirror obj_token=EPZXd5ABsoGS3cxFXcAjOYJmplc space=产品调研 synced=2026-05-18T07:54:44Z -->

# Rimbo PRD

 GET /onboarding/welcome

```Plain Text
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "欢迎使用系统，有什么可以帮您的？"
  }
}
```

GET /onboarding/example

```Plain Text
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      "如何快速上手？",
      "产品定价策略",
      "联系技术支持"
    ]
  }
}
```

POST /onboarding/message

```Plain Text
{
    "query": "用户输入的语句"
}
```

```Plain Text
{
  "code": 200,
  "message": "success",
  "data": {
    "reply": "Quick check:this helps me tunesources and briefs."
  }
}
```

GET /onboarding/choices

```Plain Text
{
  "code": 200,
  "message": "success",
  "data": {
    "roles": ["engineer","student"],
    "sources": ["website","podcast"]
  }
}
```

POST /onboarding/channels

需要token

```Plain Text
{
    "topic": "用户发送的话",
    "roles": ["",""],
    "sources": ["",""] 
}
```

```Plain Text
{
  "code": 200,
  "data": {
    "total": 52,
    "category_name": "AI Search Products",
    "sources": [
      { "id": "s1", "name": "OpenAI Developer", "icon": "https://xxxaws.com" },
      { "id": "s2", "name": "Product Hunt", "icon": "https://xxxaws.com" },
      { "id": "s3", "name": "Hugging Face Trending Papers", "icon": "https://xxxaws.com }
    ]
  }
}
```

POST /channel/subscribe

需要token

```JSON
{
      "topic": "AI Search Products",
      "source_ids": ["uuid-1", "uuid-2", "uuid-3"]  # 这里的就是上面sources里面的id
}
```

```JSON
  {
      "code": 200,
      "message": "success",
      "data": {
          "channelId": "channel-uuid",
          "channelName": "AI Search Products",
          "subscribedCount": 3
      }
  }
```

GET /channel/rss/search?url=https://sspai.com   #检测改网站url下是否有rss url

需要token

```JSON
  {
      "code": 200,
      "message": "success",
      "data": [
          {
              "url": "https://sspai.com/feed",
              "siteUrl": "https://sspai.com",
              "siteName": "少数派",
              "title": "少数派 RSS",
              "description": "高品质数字消费指南",
              "favicon": "https://cdn.sspai.com/..."
          }
      ]
 }

{
  "code": 400,
  "message": "We couldn't detect a feed at this URL, please check the link or try again."
}
```

POST /channel/{channel_id}/sources    # 这里前端好像还没出图，我也不知道要展示啥

需要token

```JSON
  {
      "rssUrl": "https://sspai.com/feed",  
      "name": "少数派",
      "iconUrl": "https://cdn.sspai.com/favicon.ico",
      "siteUrl": "https://sspai.com",
      "description": "高品质数字消费指南"  #可选
  }
```

```JSON
  {
      "code": 200,
      "message": "success",
      "data": {
          "channelId": "abc-123",
          "sourceId": "src-456",
          "sourceName": "少数派",
          "rssUrl": "https://sspai.com/feed",
          "isNew": true
      }
  }
```

GET /channel/get_channel?lang=zh   # 可选语言目前只有zh，en

需要token

```JSON
{
    "code": 200,
    "data": {
        "channels": [
            {
                "channel_id": "3fb03e6a-8a87-487d-abe5-1e6498d14158",
                "title": "AI Search Products",
                "update_count": 0,
                "sources": [
                    {
                        "source_id": "1be43409-8250-4825-9e10-cefdbaf0fcbb",
                        "name": "Google Research Blog",
                        "icon_url": "https://www.blogger.com/about/favicon/favicon.ico"
                    },
                    {
                        "source_id": "c3a78b64-efaf-4d77-af24-dd706a223730",
                        "name": "Production Engineering Archives - Engineering at Meta",
                        "icon_url": "https://engineering.fb.com/wp-content/themes/code-fb-com/favicon.ico"
                    }
                ],
                "content": {
                    "published_at": "2026-01-13T20:57:16Z",
                    "bullets": [
                        "Google Research releases MedGemma 1.5 4B and MedASR, improving multimodal medical imaging interpretation and medical ASR with notable benchmark gains.",
                        "Google demonstrates dynamic surface-code circuits on Willow, using hexagonal, walking, and iSWAP designs to improve QEC flexibility and reduce errors.",
                        "DeepMind's Veo 3.1 adds 'ingredients' controls for more consistent, creative, and vertically-formatted AI-generated videos.",
                        "Meta open-sources StyleX, a performance-focused CSS system used across Meta and adopted by Figma and Snowflake.",
                        "Meta open-sources StyleX, blending CSS-in-JS ergonomics with static CSS performance for scalable atomic component styling.",
                        "Google Research's NeuralGCM uses AI trained on NASA satellite data to better simulate global precipitation, improving daily cycle and extreme-event realism."
                    ]
                }
            }
        ]
    }
}
```

GET /channel/detail?channel_id=xxxxx&lang=zh

需要token

```JSON
{
    "code": 200,
    "data": {
        "channel": {
            "channel_id": "3fb03e6a-8a87-487d-abe5-1e6498d14158",
            "title": "AI Search Products",
            "status": "live",
            "last_updated_at": "2026-01-13T20:57:16Z",
            "sources": {
                "visible": [
                    {
                        "source_id": "a65a205a-f981-474c-9383-8d750d8caa4e",
                        "name": "AI Research Archives - Engineering at Meta",
                        "icon_url": "https://engineering.fb.com/wp-content/themes/code-fb-com/favicon.ico"
                    }
                ],
                "total_count": 18
            },
            "signals": {
                "signal_count": 3,
                "items": [
                    {
                        "order": 1,
                        "source_id": "a2ce12cd-4449-497c-89f2-0a5f9ab631b0",
                        "item_id": "ef410153ad8a6773c07902cc7eda8b2c",
                        "headline": "Google Research releases MedGemma 1.5 4B and MedASR, improving multimodal medical imaging interpretation and medical ASR with notable benchmark gains.",
                        "detail": "Google Research announced MedGemma 1.5 4B—an updated open multimodal medical LLM with expanded support for high-dimensional imaging (CT, MRI, whole-slide histopathology), longitudinal imaging, anatomical localization and lab-report extraction—and MedASR, an open medical speech-to-text model fine-tuned for clinical dictation. Both models show measurable improvements over prior versions and general baselines across internal benchmarks, are freely available on Hugging Face and Vertex AI, and are supported by tutorials, DICOM integration, and a $100,000 MedGemma Impact Challenge on Kaggle to encourage developer adoption."
                    },
                    {
                        "order": 2,
                        "source_id": "a2ce12cd-4449-497c-89f2-0a5f9ab631b0",
                        "item_id": "ef410153ad8a6773c07902cc7eda8b2c",
                        "headline": "Google demonstrates dynamic surface-code circuits on Willow, using hexagonal, walking, and iSWAP designs to improve QEC flexibility and reduce errors.",
                        "detail": "Google Quantum AI experimentally demonstrated dynamic surface-code quantum error correction on its Willow superconducting processor, alternating detecting-region tilings to enable hexagonal, walking, and iSWAP circuit families. The hexagonal design achieves three couplers per qubit while matching static performance, walking circuits greatly suppress leakage-induced time-correlated errors, and an iSWAP-based code shows viable error suppression—together expanding hardware‑software co-design options and advancing toward long-lived logical qubits."
                    },
                    {
                        "order": 3,
                        "source_id": "a2ce12cd-4449-497c-89f2-0a5f9ab631b0",
                        "item_id": "ef410153ad8a6773c07902cc7eda8b2c",
                        "headline": "DeepMind's Veo 3.1 adds 'ingredients' controls for more consistent, creative, and vertically-formatted AI-generated videos.",
                        "detail": "DeepMind's Veo 3.1 update improves generative video quality by producing more lively, dynamic clips with better temporal and subject consistency while introducing modular \"ingredients\" controls. The release explicitly supports vertical video generation and gives creators more control over elements like subject, motion, camera and style, making outputs feel more natural and easier to steer. These changes aim to broaden practical use for creators and applications that need coherent short-form video content."
                    }
                ],
                "is_like": false
            },
            "grouped_feeds_next_cursor": "<base64 cursor or null>",  #翻页下拉
            "grouped_feeds": [
                {
                    "item_object": "Google Research",
                    "items": [
                        {
                            "source_id": "4a0ed4ed-8a89-4a19-9a5b-1f40d9665597",
                            "item_id": "5302e42ac0a1b8c04fcbf7139947e308",
                            "source_icon": "https://www.gstatic.com/images/branding/googleg_gradient/1x/googleg_gradient_standard_20dp.png",
                            "item_url": "https://research.google/blog/next-generation-medical-image-interpretation-with-medgemma-15-and-medical-speech-to-text-with-medasr/",
                            "item_title": "Next generation medical image interpretation with MedGemma 1.5 and medical speech to text with MedASR",
                            "item_published_at": "2026-01-13T20:57:16Z"
                        }
                    ]
                },
                {
                    g: "Google",
                    "items": [
                        {
                            "source_id": "4a0ed4ed-8a89-4a19-9a5b-1f40d9665597",
                            "item_id": "5302e42ac0a1b8c04fcbf7139947e308",
                            "source_icon": "https://www.gstatic.com/images/branding/googleg_gradient/1x/googleg_gradient_standard_20dp.png",
                            "item_url": "https://research.google/blog/dynamic-surface-codes-open-new-avenues-for-quantum-error-correction/",
                            "item_title": "Dynamic surface codes open new avenues for quantum error correction",
                            "item_published_at": "2026-01-13T17:32:00Z"
                        }
                    ]
                },
                {
                    "item_object": "DeepMind",
                    "items": [
                        {
                            "source_id": "4a0ed4ed-8a89-4a19-9a5b-1f40d9665597",
                            "item_id": "5302e42ac0a1b8c04fcbf7139947e308",
                            "source_icon": "https://storage.googleapis.com/gdm-deepmind-com-prod-public/icons/google_deepmind_32dp.ico",
                            "item_url": "https://deepmind.google/blog/veo-3-1-ingredients-to-video-more-consistency-creativity-and-control/",
                            "item_title": "Veo 3.1 Ingredients to Video: More consistency, creativity and control",
                            "item_published_at": "2026-01-13T17:00:18Z"
                        }
                    ]
                },
                {
                    "item_object": "Meta",
                    "items": [
                        {
                            "source_id": "4a0ed4ed-8a89-4a19-9a5b-1f40d9665597",
                            "item_id": "5302e42ac0a1b8c04fcbf7139947e308",
                            "source_icon": "https://engineering.fb.com/wp-content/themes/code-fb-com/favicon.ico",
                            "item_url": "https://engineering.fb.com/2026/01/12/web/css-at-scale-with-stylex/",
                            "item_title": "CSS at Scale With StyleX",
                            "item_published_at": "2026-01-12T18:34:59Z"
                        },
                        {
                            "source_icon": "https://engineering.fb.com/wp-content/themes/code-fb-com/favicon.ico",
                            "item_url": "https://engineering.fb.com/2026/01/12/web/css-at-scale-with-stylex/",
                            "item_title": "CSS at Scale With StyleX",
                            "item_published_at": "2026-01-12T18:34:59Z"
                        }
                    ]
                },
                {
                    "item_object": "NeuralGCM",
                    "items": [
                        {    
                            "source_id": "4a0ed4ed-8a89-4a19-9a5b-1f40d9665597",
                            "item_id": "5302e42ac0a1b8c04fcbf7139947e308",
                            "source_icon": "https://www.gstatic.com/images/branding/googleg_gradient/1x/googleg_gradient_standard_20dp.png",
                            "item_url": "https://research.google/blog/neuralgcm-harnesses-ai-to-better-simulate-long-range-global-precipitation/",
                            "item_title": "NeuralGCM harnesses AI to better simulate long-range global precipitation",
                            "item_published_at": "2026-01-12T17:52:00Z"
                        }
                    ]
                }
            ]
        }
    }
}
```

GET /channel/grouped-feeds?channel_id=xxx&limit=20&cursor=...&lang=zh

需要token

```JSON
  {
    "code": 200,
    "msg": "Success",
    "data": {
      "channel_id": "xxxx",
      "grouped_feeds": [
        {
          "item_object": "Group Name",
          "items": [
            {
              "source_icon": "https://.../icon.png",
              "item_url": "https://.../article",
              "item_title": "Article title",
              "item_published_at": "2026-01-08T22:56:00Z"
            }
          ]
        }
      ],
      "next_cursor": "opaque-cursor-for-next-page"   #翻页的请求cursor
    },
    "success": true
  }
```

GET /channel/{channel_id}/items/{item_id}?source_id=...&lang=...   # 获取单篇内容

需要token

```Plain Text
{
        "code": 200,
        "data": {
            "channel_id": channel_id,
            "source_id": source_id,
            "item_id": item_id,
            "title": item.title,
            "published_at": item.published_at,
            "link": item.link,
            "source": {
                "name": source_obj.name,
                "icon_url": source_obj.icon_url,
            },
            "content": item.content,
            "content_html": item.content_html,
            "ai": {
                "condensed_content": condensed_content,
            },
        },
 }
```

GET /channel/agent/session/create   #创建对话

```Plain Text
{
    "chatSessionId": "xxxxxxx"
}
```

POST  /channel/agent/chat

需要token

```Plain Text
{    
    "chatSessionId": "xxxxxxx"，
    "query" : "用户提出的问题",
    "user_choice": # optional
    {
      "action": "subscribe_channel",
      "topic": "世界模型",
      "source_ids": ["src_1", "src_2"],
      "selected_names": ["World Models 博客", "某RSS源"]
    }
}
```

```Plain Text
SSE返回：
# 调用工具
{
    "type": "tool_start",
    "tool": "recommend_sources_tool". # 调用推荐频道工具
}
# 调用工具结束展示信源
{
    "type": "tool_end",
    "tool": "recommend_sources_tool",
    "result": {
        "success": true,
        "topic": "世界模型（World Models）最新动态",
        "recommended_count": 46,
        "sources": [
            {
                "id": "4d3a8e8c-2435-47c5-8d73-da277cc1ef2a",
                "name": "OpenAI News",
                "icon_url": null,
                "url": null
            },
            {
                "id": "1ef5cdcb-3f84-4204-9551-33b21390f4f3",
                "name": "Google DeepMind News",
                "icon_url": "https://storage.googleapis.com/gdm-deepmind-com-prod-public/icons/google_deepmind_32dp.ico",
                "url": null
            }
        ]
    }
}
# 订阅频道开始
{
    "type": "tool_start",
    "tool": "subscribe_channel_tool"
}
# 订阅频道结束
{
    "type": "tool_end",
    "tool": "subscribe_channel_tool",
    "result": {
        "success": true,
        "channel_id": "90475577-b678-42e8-8e10-23cddc497cde",
        "channel_name": "世界模型（World Models）最新动态",
        "subscribed_count": 9
    }
}

# 对话chunk
{
    "type": "chunk",
    "content": "已"
}


```



---

---

---

GET /channel/item-objects

参数：channel_id（必填）、cursor、limit、lang

需要token

```JSON
  {
    "code": 200,
    "data": {
      "channel_id": "ch_123",
      "item_objects": [
        { "item_object": "OpenAI", "count": 3 },
        { "item_object": "Anthropic", "count": 2 },
        { "item_object": "TechCrunch", "count": 1 }
      ],
      "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wMS0xNlQxMjozNDowMFoiLCJzb3VyY2VfaWQiOiIuLi4iLCJpdGVtX2lkIjoiLi4uIn0"
    }
  }
```

GET /api/v1/channel/item-objects/items

参数 channel_id/item_object/lang/cursor/limit

需要token

```JSON
 {
    "code": 200,
    "data": {
      "channel_id": "ch_123",
      "item_object": "OpenAI",
      "items": [
        { "source_id": "src_1", "item_id": "itm_001" },
        { "source_id": "src_2", "item_id": "itm_009" }
      ],
      "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wMS0xNlQxMjozNDowMFoiLCJzb3VyY2VfaWQiOiJzcmNfMiIsIml0ZW1faWQiOiJpdG1fMDA5In0"
    }
  }
```



---



下面的都暂时不做



POST /channel/modify_channel

需要token

```Plain Text
{
    "channel_id": "需要修改的channel id",
    "channel_name": "需要修改的名称", 
    "role": "",
    "filter":""
}
```

```Plain Text
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "你的修改将会在下次更新的时候生效"
  }
}
```



暂时不做！

POST /channel/tailor_brief

需要token

```Plain Text
{
    "style_choose":"",
    "brief_prompt":""
}
```

```JSON
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "你的修改将会在下次更新的时候生效"
  }
}
```