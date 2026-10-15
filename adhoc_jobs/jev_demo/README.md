# Jev 调用 Demo

2026-09-21 核对官方文档。模型 ID 为 `typesafe-ai/jev`，用于分类、评分、布尔概率判断。使用 AI Gateway 创建的 API Key，通过服务端 Node.js 调用。

## 直接运行

Node.js 20+，无需安装依赖。在 macOS 默认 zsh 中执行，输入 Key 时不回显，也不写进命令历史：

```zsh
read -rs 'AI_GATEWAY_API_KEY?粘贴 Vercel AI Gateway Key 后按回车: '; echo
export AI_GATEWAY_API_KEY
node /Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/jev_demo/demo.mjs
```

替换待判断的文本：

```zsh
node /Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/jev_demo/demo.mjs '客户申请退款，客服正在审核，尚未退款。'
```

脚本发送 `POST https://ai-gateway.vercel.sh/v1/evaluate`，请求由 `model`、`state`、`questions` 组成。修改 `questions` 可以增加多个独立问题。不要使用聊天模型的 `/chat/completions` 接口调用此模型。

输出中的 `answers.refunded.probability` 表示完成退款的概率，范围为 0 到 1；不是确定的事实证明。脚本也保留 `usage` 和 `providerMetadata`，方便查看用量及费用。概率、耗时和费用都应以真实返回为准。

## AI SDK 写法

本机已全局安装 `ai@7.0.107`；下面是等价 SDK 示例（保存为 `.cjs`，通过 `NODE_PATH="$(npm root -g)" node 文件名.cjs` 运行）。SDK 自动读取 `AI_GATEWAY_API_KEY`：

```js
const { experimental_evaluate: evaluate } = require('ai');

async function main() {
  const result = await evaluate({
    model: 'typesafe-ai/jev',
    state: '客服已经向客户完成了全额退款。',
    questions: {
      refunded: {
        type: 'boolean',
        instructions: '是否已经完成退款？',
      },
    },
  });
  console.log(result.answers);
}

main().catch(() => { console.error('调用失败，请检查 Key 和账户状态。'); process.exitCode = 1; });
```

## 价格与验证边界

模型页面注明免费推广到 2026-09-25；公开 `/v1/models` API 同时返回输入每 token `0.000000042` 美元、输出 `0` 的标准价。这不能证明特定账户的最终计费，实际看请求费用元数据和控制台账单。

已核对公开模型 ID、HTTP 请求协议及 SDK 导出，并检查脚本语法与缺少 Key 的提示。尚未拿到用户 Key，因此没有完成真实认证推理调用，也没有实际模型结果。

- [Jev 模型及限时价格](https://vercel.com/ai-gateway/models/jev)
- [Evaluation 官方文档与 HTTP API](https://vercel.com/docs/ai-gateway/modalities/evaluation)
- [AI SDK 7.0.105 起支持 evaluate](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway)

## 账户验证拦截（2026-09-21）

用户实际执行后返回 HTTP 403，错误类型为 `customer_verification_required`，服务端要求给 Key 所属账户/团队添加有效信用卡以解锁调用和免费额度。此时请求已到达 Gateway，但没有完成模型推理；修改问题或重新设置环境变量不能解决账户验证要求。

在 Vercel 控制台切换到创建 Key 的团队，按响应中的添加信用卡入口完成验证后，再运行相同命令。模型限时免费和账户验证是两个独立条件；不要把模型页 Free 理解为该账户无需验证即可调用。
