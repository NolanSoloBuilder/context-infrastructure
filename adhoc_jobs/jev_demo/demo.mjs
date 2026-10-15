// Node.js 20+，无需安装依赖。
const apiKey = process.env.AI_GATEWAY_API_KEY;
if (!apiKey?.trim()) {
  console.error('请先设置环境变量 AI_GATEWAY_API_KEY，填入 Vercel AI Gateway API Key。');
  process.exit(1);
}

try {
  const response = await fetch('https://ai-gateway.vercel.sh/v1/evaluate', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'typesafe-ai/jev',
      state: process.argv.slice(2).join(' ') || '客服已经向客户完成了全额退款。',
      questions: {
        refunded: {
          type: 'boolean',
          instructions: '是否已经完成退款？仅申请退款或承诺退款不算完成。',
        },
      },
    }),
    signal: AbortSignal.timeout(60_000),
  });

  const body = await response.text();
  if (!response.ok) {
    // 仅打印响应状态和正文，不打印请求头或 Key。
    throw new Error(`HTTP ${response.status}: ${body}`);
  }
  console.log(JSON.stringify(JSON.parse(body), null, 2));
} catch (error) {
  console.error(String(error.message).split(apiKey).join('[REDACTED]'));
  process.exitCode = 1;
}
