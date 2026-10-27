---
name: vps-tls-vision-setup
description: 为自有或获授权的 VPS 配置、核验或排障 VLESS over TCP with TLS and Vision，并生成 Clash Verge/Mihomo 本地配置与国内直连规则。适用于普通 TLS 自有域名证书方案；不把 REALITY 参数混入该方案，不承诺住宅 IP 或账号安全。
---

# VPS TLS/Vision 配置与交接

先判断任务属于新建、已有服务修复、仅生成客户端，还是文档复盘。按用户授权执行相应部分，不因为读到本 Skill 就操作现有网络。

## 成功基线与不可混淆项

参考案例最终使用 mack-a/v2ray-agent 管理 Xray/Nginx、VLESS/TCP/TLS/Vision、自有域名证书和 Clash Verge。案例的用户曾回报可用，但不是新机器可用性或长期稳定性的保证。

普通 TLS 方案需要服务端证书、客户端 `servername`、`tls: true`、`flow: xtls-rprx-vision` 与 `skip-cert-verify: false`；不添加 `reality-opts`、公钥、Short ID 或 SpiderX。节点 UUID 必须取自同一服务器入站，不能自行换值后只更新客户端。

阅读路径：
- 实施或迁移：先读 [references/deployment.md](references/deployment.md)。
- Timeout、握手、导入或分流问题：读 [references/troubleshooting.md](references/troubleshooting.md)。
- 需要核对版本和能力：读 [references/sources.md](references/sources.md)，访问官方资料。

## 任务输入

复用已知信息；缺少的必要项才询问：授权的 VPS、SSH 访问方式、系统版本、自己的域名和 DNS 权限、已有服务/数据、客户端版本、要走代理的业务、最终启用由谁执行。密码、UUID、私钥只留在本地受限文件，不写入对外文档。

## 进行方式

1. 只读识别真实环境：`systemctl cat/show` 确认服务和实际配置路径；查 80/443 所有者、A/AAAA、证书和客户端当前导入配置。旧备份不替代运行态。
2. 把将改的对象与已获授权范围对齐。备份相关服务文件、配置、证书及客户端配置，记录恢复路径。新建或常规修复不包含重装系统、清空磁盘、删除其他业务。必要的破坏性迁移需单独明确授权。
3. 实施普通 TLS/Vision 链路。端口有占用先识别所属服务，获准切换后才停旧管理服务；不循环杀子进程。DNS、证书和服务器静态检查通过后再生成客户端。
4. 把 `assets/params.example.json` 复制为本地私有参数文件，填写同一入站参数。运行 `python3 scripts/prepare_client.py --params params.private.json --out generated-YYYYMMDD`。脚本只创建新目录和配置，不连接 VPS，不导入、不重载、不切换系统代理/TUN。
5. 在目标 Mihomo 版本用 `-t -f` 做语义检查；检查所需 GeoSite/GeoIP 数据存在。`geo_cn:false` 只使用内置显式国内域名，不能声称覆盖所有国内网站。导入为新本地配置后，回读应用导入副本和实际核心加载配置，不能只看源 YAML。
6. 尊重用户保留的最后启用/测试步骤。若用户保留开关，就停在交接；否则在授权范围内完成测试。只有目标业务成功、出口和连接链路符合目标，才记业务验收。

## 分流默认

已知国内直连，其他默认走唯一 `US-FIXED` 组。组里只有本次 VPS 节点，不放 DIRECT/自动回退节点。用户明确的例外优先，但冲突需说清。全局模式会跳过规则，不是分流模式。客户端配置只管被该客户端接管的流量，不等于系统全应用防泄漏保证。

模板 DNS 把普通海外解析指定到代理，国内规则采用国内解析；节点地址使用已知 IPv4，避免节点域名解析递归。必须分别核对 DNS 路径、连接出口、IPv6 和应用代理行为。不要把第三方风险评分当作 Claude 官方账号安全结论。

## 失败与交付

发现认证材料不一致、证书校验失败、未知端口占用或权限拒绝时，停在该层记录证据；不关闭证书校验、不绕过权限、不盲目重装。一次改变一层。不要把安装器中的 `read` 全局替换为自动应答，也不固定套菜单数字。

按以下状态回报：`prepared_offline` → `server_static_ok` → `client_import_verified` → `user_business_verified`。记录版本、配置哈希、备份路径、待测项；不得跳过中间证据。维护优先查询真实 unit/路径；证书续期菜单可能停服务，不当只读检查运行。
