#!/usr/bin/env python3
"""Offline VLESS/TCP/TLS/Vision client generator. No network or app changes."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import uuid

CN = ['feishu.cn','feishucdn.com','feishu.net','qq.com','qpic.cn','qlogo.cn',
      'gtimg.com','gtimg.cn','wechatpay.com','wechatpay.cn','taobao.com','tmall.com',
      'alipay.com','alipayobjects.com','alicdn.com','bilibili.com','bilivideo.com',
      'biliapi.net','hdslb.com','douyin.com','douyincdn.com','xiaohongshu.com',
      'xhscdn.com','netease.com','163.com','126.com','music.126.net','baidu.com',
      'bdstatic.com','zhihu.com','zhimg.com']
FOREIGN = ['claude.ai','claude.com','anthropic.com','claudeusercontent.com',
           'claudemcpcontent.com','chatgpt.com','openai.com','oaistatic.com',
           'oaiusercontent.com','x.com','twitter.com','twimg.com','t.co','grok.com',
           'x.ai','google.com','googleapis.com','gstatic.com','googleusercontent.com',
           'github.com','githubusercontent.com','githubassets.com']

def domain(value):
    if not isinstance(value,str):
        raise ValueError('domain must be text')
    value=value.lower().rstrip('.')
    if len(value)>253 or '.' not in value or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',s) for s in value.split('.')):
        raise ValueError('use a DNS hostname without URL, port, path or wildcard')
    return value

def port(value):
    if type(value) is not int or not 1<=value<=65535:
        raise ValueError('port must be an integer from 1 to 65535')
    return value

def build(params):
    allowed={'server_ip','server_name','uuid','port','mixed_port','geo_cn','direct_domains','proxy_domains'}
    if set(params)-allowed:
        raise ValueError('unknown parameters: '+','.join(sorted(set(params)-allowed)))
    host=str(ipaddress.IPv4Address(params['server_ip']))
    server_name=domain(params['server_name'])
    client_id=str(uuid.UUID(params['uuid']))
    if client_id=='00000000-0000-0000-0000-000000000000':
        raise ValueError('nil UUID is not accepted')
    remote_port=port(params.get('port',443)); local_port=port(params.get('mixed_port',7897))
    geo=params.get('geo_cn',True)
    if type(geo) is not bool:raise ValueError('geo_cn must be boolean')
    direct=params.get('direct_domains',[]); proxy=params.get('proxy_domains',[])
    if not isinstance(direct,list) or not isinstance(proxy,list):raise ValueError('domain overrides must be lists')
    direct=[domain(s) for s in direct]; proxy=[domain(s) for s in proxy]
    # Reject overlapping overrides; they need a deliberate ordering decision.
    for a in direct:
        for b in proxy+FOREIGN:
            if a==b or a.endswith('.'+b) or b.endswith('.'+a):
                raise ValueError('direct/proxy domain conflict; resolve it explicitly')
    direct=list(dict.fromkeys(direct+CN)); proxy=list(dict.fromkeys(proxy+FOREIGN))
    rules=['DOMAIN-SUFFIX,localhost,DIRECT','DOMAIN-SUFFIX,local,DIRECT',
           'DOMAIN-SUFFIX,lan,DIRECT','DOMAIN-SUFFIX,home.arpa,DIRECT',
           'IP-CIDR,127.0.0.0/8,DIRECT,no-resolve',
           'IP-CIDR,10.0.0.0/8,DIRECT,no-resolve',
           'IP-CIDR,172.16.0.0/12,DIRECT,no-resolve',
           'IP-CIDR,192.168.0.0/16,DIRECT,no-resolve',
           'IP-CIDR,169.254.0.0/16,DIRECT,no-resolve',
           f'IP-CIDR,{host}/32,DIRECT,no-resolve']
    rules += ['DOMAIN-SUFFIX,'+d+',US-FIXED' for d in proxy]
    rules += ['DOMAIN-SUFFIX,'+d+',DIRECT' for d in direct]
    if geo:rules+=['GEOSITE,cn,DIRECT','GEOIP,CN,DIRECT']
    rules+=['MATCH,US-FIXED']
    domestic=['https://dns.alidns.com/dns-query','https://doh.pub/dns-query']
    policy={'+.'+d:domestic for d in direct}
    if geo:policy['geosite:cn']=domestic
    return {'mixed-port':local_port,'allow-lan':False,'bind-address':'127.0.0.1',
            'mode':'rule','log-level':'info','ipv6':False,'tun':{'enable':False},
            'dns':{'enable':True,'ipv6':False,'enhanced-mode':'fake-ip',
                   'fake-ip-range':'198.18.0.1/16','respect-rules':True,
                   'default-nameserver':['223.5.5.5','119.29.29.29'],
                   'proxy-server-nameserver':domestic,
                   'nameserver':['https://1.1.1.1/dns-query#US-FIXED','https://dns.google/dns-query#US-FIXED'],
                   'nameserver-policy':policy,
                   'fake-ip-filter':['*.lan','localhost','*.local']},
            'proxies':[{'name':'VPS-TLS-Vision','type':'vless','server':host,
                        'port':remote_port,'uuid':client_id,'network':'tcp','udp':True,
                        'tls':True,'flow':'xtls-rprx-vision','servername':server_name,
                        'client-fingerprint':'chrome','skip-cert-verify':False}],
            'proxy-groups':[{'name':'US-FIXED','type':'select','proxies':['VPS-TLS-Vision']}],
            'rules':rules}

def write_private(path,content):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(content)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--params',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    try:
        config=build(json.loads(args.params.read_text(encoding='utf-8')))
        # A new directory is mandatory: never overwrite an earlier working profile.
        args.out.mkdir(mode=0o700,parents=True,exist_ok=False)
        # JSON is a YAML subset. Mihomo accepts this as a complete YAML profile.
        body=json.dumps(config,ensure_ascii=False,indent=2)+'\n'
        profile=args.out/'Clash-TLS-Vision.yaml'
        write_private(profile,body)
        receipt={'status':'prepared_offline','profile':profile.name,
                 'sha256':hashlib.sha256(body.encode()).hexdigest(),
                 'network_changed':False,'client_imported':False,'business_verified':False,
                 'core_validation':'pending_on_target_version',
                 'geo_database_required':bool(args.params.read_text() and any(x.startswith('GEOSITE,') for x in config['rules']))}
        write_private(args.out/'receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'ok':True,'status':'prepared_offline','output_directory':str(args.out),'profile_sha256':receipt['sha256']},ensure_ascii=False))
    except (ValueError,KeyError,OSError,TypeError) as e:
        # Exception text never includes credential values supplied by the user.
        print(json.dumps({'ok':False,'error_type':type(e).__name__,'error':'invalid_input_or_existing_output; inspect locally without sharing credentials'}))
        raise SystemExit(2)

if __name__=='__main__':main()
