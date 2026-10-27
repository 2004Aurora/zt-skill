# 从授权到交付

本流程面向自己拥有或明确获授权管理的 Debian/Ubuntu VPS 与 Clash Verge/Mihomo 客户端。它复用历史成功架构，不保证任意发行版、安装脚本新版本或目标业务都兼容。

## 1. 冻结任务卡

记录 `server_label / server_ip / ssh_host / ssh_port / os / domain / dns_provider / server_stack / client_version / final_switch_owner`。凭据放私有文件；不用聊天日志当凭据存储。SSH 首次连接时核对主机指纹，不因为连接困难自动跳过校验。

在现有机器上只读运行：
```bash
cat /etc/os-release
uname -m
ss -ltnp
systemctl status x-ui xray nginx --no-pager
systemctl show xray -p FragmentPath -p ExecStart
systemctl cat xray
```
某个 unit 不存在并不等于失败，先识别实际部署名称。读取结果仅在必要范围保存，命令行可能含私有参数。

确认旧服务归属和备份范围。可用云快照保存远端磁盘，同时备份发现的配置、unit 和证书；备份应权限受限并可回读。只复制配置不能称完整服务器恢复。不要为使用本流程重装本机电脑或自动重装 VPS。

## 2. DNS 与证书前置

用自己的域名指向该 VPS；历史提供商为 Spaceship，不要求迁移到 Cloudflare。普通 TLS 直连节点不要放在不支持该协议的 HTTP CDN 代理后。

```bash
# 按真实值设置这两个变量；不是直接复制示例域名。
dig "$DOMAIN" A
dig "$DOMAIN" AAAA
dig @1.1.1.1 "$DOMAIN" A
dig @8.8.8.8 "$DOMAIN" A
```
A 应指向所用 IPv4。存在 AAAA 时确认 IPv6 服务和路由确实可用；不要留错误 AAAA。SERVFAIL 先查权威解析、DS/DNSKEY 与注册商 DNSSEC 配置，不把关闭 DNSSEC 当通用修复。

HTTP-01 签证需要公网 TCP 80；服务端代理使用 TCP 443。云防火墙与系统防火墙都需核对，保留真实 SSH 端口，不一键清空规则。若使用 DNS-01，所需 DNS API 权限应限于当前域名，并保护 token。

## 3. 选择和审核安装来源

历史安装器为 mack-a/v2ray-agent v3.5.26，固定提交见 sources.md。新部署应核对上游当前支持和安全更新；固定旧提交用于复现和审计，不自动意味着适合长期新部署。安装器可能再下载可变版本的核心，固定安装器不等于所有依赖固定。

以下仅下载和查看，不会安装：
```bash
curl --fail --location --proto '=https' --tlsv1.2 \
  'https://raw.githubusercontent.com/mack-a/v2ray-agent/d8926406b333442d8d2dc9f0c9e68678949a70de/install.sh' \
  -o install.reviewed.sh
sha256sum install.reviewed.sh
less install.reviewed.sh
```
本包保存固定源码哈希以便比对。只有来源、备份、变更范围已经核验且部署授权明确，才在目标服务器运行 `sudo bash install.reviewed.sh`。这是有副作用的安装命令，不属于文档生成或只读检查。

按当前菜单文字选择 Xray 和 VLESS/TCP/TLS/Vision，填写自己的域名/证书信息。不要选 REALITY 后继续用本模板；不要因为菜单数字以前是某个值就盲选。保留日志，不全局覆盖 Bash `read`。脚本提示与预计不符就停止核查。

如旧 x-ui 持有 443：先查它是否还有其他用户/入站，确定迁移及回退后再停止、禁用对应管理服务。直接杀 Xray 子进程可能被管理器拉起。若端口属于其他网站，先设计共存或单独服务器；不要为方便抢占。

## 4. 服务端核验

使用 `systemctl show/cat` 找到真实二进制和配置目录，再依该版本帮助执行配置测试。例子是结构，路径必须换成实际值：
```bash
/path/to/xray run -test -confdir /actual/config/directory
/path/to/nginx -t -c /actual/nginx.conf
systemctl is-active xray nginx
systemctl is-enabled xray nginx
ss -ltnp
openssl x509 -in /actual/fullchain.pem -noout -subject -issuer -dates
```
证书名称覆盖客户端 `servername`；服务监听地址和443所有者正确；静态检查通过不等于外部可达。保留返回码，不能只截取一行绿色字。

## 5. 生成、检查和导入客户端

从同一入站读取 server IP、port、UUID、TLS域名，填写参数。示例 IP 与 UUID仅用于离线演示，不可拿去连接。
```bash
cp assets/params.example.json params.private.json
chmod 600 params.private.json
# 在本地编辑 params.private.json，使用真实参数；不要贴入公开文档。
python3 scripts/prepare_client.py --params params.private.json --out generated-YYYYMMDD
# 使用真实 Mihomo 二进制；GeoSite/GeoIP 数据须可用。
/path/to/mihomo -t -f generated-YYYYMMDD/Clash-TLS-Vision.yaml
```
生成器输出 JSON 语法的完整 YAML 配置，这是 YAML 子集。不是把单个 vless:// URI 当 YAML 订阅。支持具体版本以目标核心语义检查为准。

默认规则：局域网/节点 IP直连 → 明确海外业务 → 明确国内域名 → 可选 GeoSite/GEOIP 国内 → MATCH唯一代理。`geo_cn` 为 false 时不依赖地理库，但国内覆盖只限显式域名，不可宣称全面国内识别。

在 Clash Verge 新建本地配置并导入文件，保留旧配置。检查新卡片被选择、核心实际载入新节点；修改原文件不保证导入副本更新。不要编辑 `profiles.yaml` 指针来绕过界面权限。

## 6. 交接测试

若用户保留启用，交付文件和下面的检查表，不替用户开关。测试时只有一个客户端接管系统代理/TUN；另一个客户端的退出由用户或当前授权执行。

- 选择规则模式；确认唯一固定出口节点，没有落到 DIRECT。
- 本机通过指定代理端口查询出口；出口与本次 VPS 对应。
- 在客户端连接页验证 Claude/ChatGPT/X走固定节点，国内样例走DIRECT。
- 分别验证浏览器、桌面应用与终端；它们不一定共享系统代理设置。
- 使用本人有权访问的业务完成一次真实请求；HTTP403/登录/订阅错误单独分类，不一概归因网络。
- 检查 DNS/IPv6路径。浏览器检测页看到国内DNS不等于所有海外请求泄漏；需要域名级链路证据。

只有用户实测通过才登记业务完成。生成器 receipt 始终标为 prepared_offline，不会自行晋级。

## 7. 维护与回退

保存成功版本 SHA、安装器提交、实际核心版本、证书名称/到期日和续期入口；每台设备使用自己的凭据更便于撤销。

续期菜单可能停止服务，先查看脚本行为与真实 cron/timer。预约允许中断的维护时段再试续期，不把 RenewTLS 作为只读巡检。失败时先保留故障日志，恢复已验证副本；未演练的远端备份不称可恢复性已验证。
