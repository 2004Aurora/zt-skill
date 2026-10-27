# 来源和版本边界

编制日期：2026-10-27。历史案例是2026-10-22/23的用户实践；本 Skill 是本次重新参数化的通用交付物，已做离线测试，未在另一台VPS完成新部署验证。

- 历史安装器：mack-a/v2ray-agent v3.5.26，commit `d8926406b333442d8d2dc9f0c9e68678949a70de`。
  https://github.com/mack-a/v2ray-agent/blob/d8926406b333442d8d2dc9f0c9e68678949a70de/install.sh
- 当前上游入口与支持范围：https://github.com/mack-a/v2ray-agent
- VLESS/Vision：https://xtls.github.io/config/outbounds/vless.html
- Mihomo VLESS字段：https://wiki.metacubex.one/config/proxies/vless/
- Mihomo DNS：https://wiki.metacubex.one/config/dns/
- Clash Verge本地导入：https://github.com/clash-verge-rev/clash-verge-rev.github.io/blob/main/docs/guide/profile.md
- HTTP-01端口要求：https://letsencrypt.org/docs/challenge-types/
- SERVFAIL可能原因：https://letsencrypt.org/docs/caa/#servfail

这些资料会变；字段与菜单以目标版本为准。历史安装器只是复现基线，不强制降级当前可用核心。

原案例证据只证明当时用户报成功。此包不包含原用户密码、节点UUID、私钥、私有订阅链接；不能拿通用模板直接接入其服务器。机房VPS不因出口在美国就成为住宅IP。

Skill自写生成器不包含上游安装器代码。完整资料包的上游参考源码附独立许可证与来源，不把第三方源码声明为原创。
