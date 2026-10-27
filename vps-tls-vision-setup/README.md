# vps-tls-vision-setup

把自己的 VPS 搭成固定出口梯子的 Skill：服务端用 VLESS + TCP + TLS + Vision，Mac 用 Clash Verge 按规则分流，国内网站直连，其余走你自己的固定节点。

这是枕棠用上 Claude 时实际跑通的方案，整理成了 AI 能照着做的说明书。配套文章：《如何安全可用地用上 Claude：一个从没用过 Claude 的人的踩坑全记录》。

## 怎么用

1. 下载仓库根目录的 `vps-tls-vision-setup.zip`，解压后把 `vps-tls-vision-setup` 整个文件夹放进 `~/.codex/skills/`。
2. 新开一个 Codex 会话，输入 `$vps-tls-vision-setup`，再把下面这段任务说明发给它。
3. 它会先只读检查你的服务器和参数，列出还缺什么；你确认之后才会动服务器。最后开代理、测试这一步默认留给你自己。

```text
请先阅读 vps-tls-vision-setup/SKILL.md，再按引用读取 deployment.md。
我的目标：在我自己的 VPS 上部署普通 VLESS/TCP/TLS/Vision，并准备 Clash Verge 客户端配置；已知国内网站直连，其他默认走固定代理。
先整理现有参数和缺口，复用我已提供的信息。不要沿用案例作者的 IP、域名或凭据。
第一步只做只读盘点和可审阅的配置；只有我明确授权部署之后，才修改服务器或客户端。
不要重装我的电脑，不要默认重装 VPS；保护原配置和其他业务。若有旧服务占用 443，先说明影响和恢复方法。
最后的启用和测试默认留给我。
交付：版本清单、备份路径、完整的本地客户端配置文件、导入说明、分步验证结果和未完成项。不能把测速绿色当成真正能用。
```

没有 Codex 的话，Claude Code 这类能读文件、跑终端的 AI 工具也可以用；普通聊天 AI 只能给步骤，没法替你操作。

## 你需要准备

- 一台自己的海外 VPS（Debian / Ubuntu）和 SSH 登录方式
- 一个自己的域名，能改 DNS
- Mac 上装好 Clash Verge Rev

## 文件说明

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 给 AI 读的主说明 |
| `references/deployment.md` | 从准备到交付的完整步骤 |
| `references/troubleshooting.md` | 常见报错怎么查 |
| `references/sources.md` | 官方资料和安装脚本版本 |
| `scripts/prepare_client.py` | 填好参数后生成 Clash 配置 |
| `assets/params.example.json` | 参数示例 |

## 注意

- 包里只有示例地址和示例 UUID，不含作者的服务器信息。你要填自己的 VPS、域名和 UUID。
- `prepare_client.py` 只在本地生成新的配置文件：不联网、不改服务器、不覆盖已有文件。
- 生成的配置里有你的 UUID，别发到公开的地方。
- 只适用于普通 TLS 方案，不要混入 REALITY 的参数。
- 这只解决网络问题。Claude 官方对使用地区有要求，本 Skill 不承诺任何账号安全，也不保证"不封号"。
