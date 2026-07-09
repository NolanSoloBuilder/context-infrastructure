# Podnote 服务器迁移参考

记录时间：2026-07-07  
用途：未来迁移 Podnote 服务时，快速还原当前阿里云轻量应用服务器上的运行拓扑、代码来源和关键检查点。

## 控制台入口

- 阿里云产品：轻量应用服务器 SWAS
- 控制台地址：`https://swasnext.console.aliyun.com/servers/cn-hongkong`
- 登录账号界面显示：`xuhao@1118317675020997.onaliyun.com`，RAM 用户
- 区域：中国香港，`cn-hongkong`

当前页面显示 2 台香港轻量服务器：

| 实例名 | 实例 ID | 公网 IP | 私网 IP | 镜像 | 规格 | 磁盘 | 到期时间 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Ubuntu-application` | `21ef73212560401ea9ae69db57c666ac` | `8.210.253.48` | `172.19.26.253` | Ubuntu 24.04 | 4 vCPU / 16 GiB | ESSD 80 GiB | 2026-08-12 23:59:59 | Podnote 当前主机 |
| `Ubuntu-camq` | `f4e3b525dbea469db3fde466e3c6e2ef` | `47.239.4.148` | `172.17.42.245` | Ubuntu 24.04 | 4 vCPU / 8 GiB | ESSD 70 GiB | 2026-07-26 23:59:59 | 非本次 Podnote 主机 |

## 域名和访问

本地解析确认：

```bash
dig +short dev.podnote.com www.podnote.com podnote.com
```

三者均解析到：

```text
8.210.253.48
```

公网访问行为：

- `http://8.210.253.48/` 返回 301 到 `https://ai.dev.aws.podnote.com/`
- `https://www.podnote.com/` 返回 Next.js 页面，根路径 307 到 `/home`
- `http://8.210.253.48:3000/` 和 `:3001` 从本机访问超时，说明前端容器端口虽映射，但公网链路主要走 Nginx / 域名入口

## 登录方式

可用方式：

- 阿里云控制台 `Ubuntu-application` -> `远程连接` -> `Workbench 一键连接`
- Workbench 默认进入用户：`admin`
- Workbench 终端显示主机名：`iZj6c4t9bvxrho2ge8bu6kZ`
- 登录后 home：`/home/admin`

本机直接 SSH 情况：

- 本机已有 `~/.ssh/mindspace.pem` 对这台机器的常见用户无效
- 曾测试 `root / ubuntu / admin / ecs-user / mindspace`，均 `Permission denied (publickey)`
- 后续临时给 `admin` 加过一次临时 key，但本机 `scp` 到 `8.210.253.48:22` 返回 `Connection refused`
- 服务器内 `sshd` 监听正常，`fail2ban` 当时未封本机出口 IP；更像是轻量防火墙 / 安全组 / 网络策略导致公网 22 不可直连
- 临时 SSH key 已删除，服务器上只保留了 `~/.ssh/authorized_keys.bak_podnote_recovery_20260707` 作为当时备份

如果未来要迁移，优先通过 Workbench 登录。若希望本机可直接 `scp`，需要在 SWAS 防火墙 / 安全组里确认 22 端口策略，并配置新的 SSH key。

## 宿主机目录

主要部署目录：

```text
/home/admin/podnote
```

这个目录里有当前部署编排、源码快照、备份和运维脚本。关键条目：

```text
/home/admin/podnote/docker-compose.yml
/home/admin/podnote/PodNote-main
/home/admin/podnote/podnotebackend-main
/home/admin/podnote/podcast_algorithm_backend-main
/home/admin/podnote/tmp_exports/
/home/admin/podnote/runtime/
/home/admin/podnote/ops/
/home/admin/podnote/openviking-sidecar/
/home/admin/podnote/earnings-sync/
```

源码恢复包仍保留在服务器：

```text
/home/admin/podnote/tmp_exports/podnote_source_snapshots_20260707.tgz
```

本地恢复目录：

```text
/Users/xuhao/Documents/Other/podnote_recovered_20260707
```

已上传到个人 GitHub 私有仓库：

```text
https://github.com/NolanSoloBuilder/podnote-source-recovered
```

## Docker 运行拓扑

2026-07-07 查到的容器：

```text
podnote-frontend               podnote-frontend                 0.0.0.0:3000->3000/tcp
podnote-frontend-canary        podnote-frontend-canary          0.0.0.0:3001->3000/tcp
podnote-assistant-upstream     podnote-assistant-upstream       8010/tcp
podnote-openviking-server      podnote-openviking-server        1933/tcp
podnote-backend                podnote-backend                  0.0.0.0:15823->8080/tcp
podnote-algorithm              podnote-algorithm                0.0.0.0:8081->8080/tcp
earnings-api                   21ec7ee991ab                     0.0.0.0:8088->8000/tcp
redis-prod                     redis:7-alpine                   6379/tcp
pod-note-aigo-worker-llm       pod-note-aigo-develop:20260221_024000
pod-note-aigo-beat             pod-note-aigo-develop:20260221_024000
pod-note-aigo-worker-bg        pod-note-aigo-develop:20260221_024000
pod-note-aigo-worker-llm-user  pod-note-aigo-develop:20260221_024000
pod-note-aigo-worker-llm-2     pod-note-aigo-develop:20260220_184200
pod-note-aigo-worker-llm-3     pod-note-aigo-develop:20260220_184200
pod-note-aigo-worker-llm-4     pod-note-aigo-develop:20260220_184200
podnote-backend-admin-stats-beat
podnote-backend-admin-stats-worker
podnote-backend-process-worker
rabbitmq-local                 rabbitmq:3.12-management         5672/tcp, 15672/tcp
mongo-prod-restored            mongo:6.0                        0.0.0.0:27017->27017/tcp
```

镜像 label 显示核心服务来自 Docker Compose project：

```text
com.docker.compose.project=podnote
```

服务名：

```text
frontend
backend
algorithm
```

## Nginx

Nginx 主配置入口：

```text
/etc/nginx/sites-enabled/podnote
```

关键片段和端口关系：

- `server_name www.podnote.com podnote.com`
- `location /` -> `proxy_pass http://podnote_frontend_pool`
- `location /api/` -> `proxy_pass http://127.0.0.1:15823`
- `location = /api/v1/pod_note/process/episodes` -> `127.0.0.1:15823`
- `location /v1/earnings/` -> `127.0.0.1:8088`
- `/.well-known/acme-challenge/` -> `root /var/www/html`
- SSL 证书路径：
  - `/etc/letsencrypt/live/www.podnote.com/fullchain.pem`
  - `/etc/letsencrypt/live/www.podnote.com/privkey.pem`
- 日志：
  - `/var/log/nginx/podnote-access.log`
  - `/var/log/nginx/podnote-error.log`

迁移时要复制或重新生成 Let’s Encrypt 证书，并确认 DNS 切换后 `/.well-known/acme-challenge/` 能正常验证。

## 代码快照

容器内 `/app` 有源码，但没有 `.git` 历史：

```bash
docker exec podnote-backend sh -lc 'ls -la /app'
docker exec podnote-frontend sh -lc 'ls -la /app'
docker exec podnote-algorithm sh -lc 'ls -la /app'
```

宿主机也保留了对应源码快照：

```text
/home/admin/podnote/PodNote-main
/home/admin/podnote/podnotebackend-main
/home/admin/podnote/podcast_algorithm_backend-main
```

注意：

- 原始 Git 历史不在服务器快照里
- `*.yaml`、`.env`、`docker-compose.yml`、临时脚本中含真实生产配置和密钥
- 上传到 GitHub 私有仓库时按用户授权保留了原始恢复目录内容
- 后续如果仓库权限有变化，建议先轮换这些密钥

## 数据和状态

需要迁移的数据状态至少包括：

- MongoDB：容器 `mongo-prod-restored`，端口映射 `27017`
- Redis：容器 `redis-prod`
- RabbitMQ：容器 `rabbitmq-local`，管理端口映射 `15672`
- 后端日志：`podnotebackend-main/logs` 和容器内 `/app/logs`
- 算法日志：`podcast_algorithm_backend-main/logs`
- 运行状态文件：
  - `podnotebackend-main/pod_note/scheduler/*_progress.json`
  - `podnotebackend-main/pod_note/scheduler/podcast_updates.json`
  - `podnotebackend-main/pod_note/script/sync_progress.json`

迁移时不要只复制源码。需要单独处理数据库 dump、RabbitMQ 队列状态、Redis 临时状态和对象存储配置。

## 当前服务进程特征

宿主机 `ps aux` 中看到大量 Celery worker 从容器内 `/app/.venv/bin/python` 启动，主要模块：

```text
pod_note.task.podnote_worker.celery_app
pod_note.task.episode_process_celery.celery_app
```

队列名包括：

```text
llm_task
llm_task_user
update_rss
get_top_podcast
process_episodes
```

迁移后要重点确认：

```bash
docker ps
docker logs podnote-backend --tail 100
docker logs podnote-algorithm --tail 100
docker logs podnote-frontend --tail 100
docker logs rabbitmq-local --tail 100
docker logs mongo-prod-restored --tail 100
```

## 迁移建议顺序

1. 在新机器上准备 Docker / Docker Compose / Nginx / certbot。
2. 从 GitHub 私有仓库拉代码快照，或从服务器内部包恢复：

   ```bash
   /home/admin/podnote/tmp_exports/podnote_source_snapshots_20260707.tgz
   ```

3. 从旧服务器备份 `docker-compose.yml` 和各服务 `resources/*.yaml` / `.env`。这些文件含敏感值，迁移时用安全通道传输。
4. 对 MongoDB 做完整 dump，并在新机器 restore。
5. 评估 RabbitMQ 是否需要迁移队列中未消费任务；如果可以接受重新投递，可只迁移配置。
6. 配置 OSS、邮件、Google OAuth、ASR / LLM provider 等外部依赖。
7. 在新机器启动 Compose，先不切 DNS，通过 hosts 或临时域名验证：

   ```bash
   curl -I http://127.0.0.1:15823/
   curl -I http://127.0.0.1:8081/
   curl -I http://127.0.0.1:3000/
   ```

8. 配置 Nginx，验证 `www.podnote.com` / `podnote.com` 的 HTTPS。
9. 切 DNS 到新公网 IP。
10. 观察 Celery、Mongo、RabbitMQ、Nginx、前端和核心 API 日志。

## 迁移风险点

- 当前 GitHub 仓库是从服务器快照恢复的源码，缺少原始 commit history。
- 当前部署目录含大量 `.bak`、临时脚本和运行进度文件；迁移时要区分源码、配置、运行数据和历史备份。
- MongoDB 对公网有端口映射 `0.0.0.0:27017->27017/tcp`，迁移时建议改为内网访问或收紧防火墙。
- 服务器里有真实生产密钥；如果未来仓库权限、人员或部署方式变化，建议轮换：
  - MongoDB 用户密码
  - Aliyun OSS AccessKey
  - 邮件 sender password
  - Google OAuth client secret
  - ASR / LLM provider key
  - JWT secret
- Workbench 可用，但本机直连 SSH 当时不可用；迁移前最好建立稳定 SSH 通道和备份下载方式。

