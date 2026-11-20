FROM node:22-bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global --no-audit --no-fund lunar-javascript@1.7.7 pinyin-pro@3.28.0 pdfkit@0.17.2 \
    && npm cache clean --force
WORKDIR /app
COPY server.mjs public-catalog.json ./
COPY bazi ./bazi
COPY data ./data
COPY local ./local
COPY public ./public
USER node
CMD ["node", "server.mjs"]
