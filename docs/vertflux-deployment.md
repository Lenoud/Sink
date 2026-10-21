# Vertflux 部署

生产地址：https://go.vertflux.com/

本仓库保存当前上线版本的源码和定制。生产分支为 `master`，上游为 [miantiao-me/Sink](https://github.com/miantiao-me/Sink)。

## 构建与发布

- 推送到生产分支，或合并 PR 后，`Vertflux 构建检查与部署` 会先安装锁定依赖并构建，成功后部署到现有 Cloudflare 项目。
- PR 和手动运行默认只检查代码。手动发布需要在生产分支运行并勾选 `deploy`。
- `CLOUDFLARE_API_TOKEN` 仅保存在 GitHub Actions 加密 Secret，且只在部署步骤中传入。模型 Key、Sink 站点令牌和统计令牌继续保存在各自服务的 Secret 中。
- 保留现有域名、数据库及资源绑定，不自动创建新数据库或付费服务。
- 原有上游工作流在此仓库中保持禁用，避免触发其 Docker、Vercel、桌面客户端或上游专属发布任务。

## 同步上游

- 每天 UTC 02:57（北京时间 10:57）检查上游分支，也可以手动运行 `Vertflux 同步上游并创建 PR`。
- 存在更新时，维护 `updates/upstream` 分支和一个待审核 PR，并显式启动构建检查。
- PR 通过检查后，由仓库所有者确认合并，合并后才会发布。不会自动合并上游代码。
- `.github/vertflux-preserve-paths.txt` 中的工作流和站点配置会保留；其他源码通过 Git 合并。发生冲突时流程停止，不修改生产部署。

仅重新运行旧版本工作流不会回滚数据库迁移。代码回退应提交到生产分支并重新部署。

## 统一认证

生产入口通过现有 Casdoor 和 OAuth2-Proxy 登录，使用 `vertflux` 组织的账号。登录会话采用每个主机独立的 Secure、HttpOnly Cookie；成功鉴权只在 Worker 实例内缓存 15 秒。Pages 默认域名跳转正式域名，业务 Worker 关闭 workers.dev 和预览地址。所有鉴权失败均拒绝访问，登录回调使用固定上游并校验返回域名。

`/dashboard`、`/api` 和 `/_docs` 需要认证，公共短链接继续开放。入口使用加密 Secret `SINK_SITE_TOKEN` 调用内部 API，浏览器只持有 SSO Cookie，不接收内部令牌。GitHub Actions 的 `VERTFLUX_SINK_SITE_TOKEN` 仅供部署步骤同步该 Secret。后台退出会清除当前应用的认证会话。
