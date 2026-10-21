"""审计或删除接入认证前的 Pages 历史版本，保留当前及后续受保护版本。"""
import datetime
import json
import os
import urllib.error
import urllib.request

ACCOUNT = 'bf8566234d0f57c2451986e3cdcb01c4'
BASELINES = {
    'vertflux-aidraw': 'd9cd446fc34b95bd979d6b5d84bc3934119a6fa5',
    'vertflux-aiimage': '3b1727c1d723355819c11e3b026b2aab4cc304cf',
    'vertflux-go': 'bbf3f6b5cf8e0d70c639cafccd05f1ed0fbef4db',
}
MODE = os.environ.get('VERTFLUX_MODE', 'audit')
assert MODE in ['audit', 'cleanup']


def api(path, method='GET'):
    request = urllib.request.Request(
        f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/{path}',
        method=method,
        headers={'Authorization': 'Bearer ' + os.environ['CLOUDFLARE_API_TOKEN']},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'Cloudflare API {method} 失败，HTTP {error.code}') from None
    if not result.get('success'):
        raise RuntimeError(f'Cloudflare API {method} 未成功')
    return result


def created(deployment):
    return datetime.datetime.fromisoformat(deployment['created_on'].replace('Z', '+00:00'))


plans = []
for project, commit in BASELINES.items():
    metadata = api(f'pages/projects/{project}')['result']
    canonical = metadata['canonical_deployment']
    deployments = []
    page = 1
    while True:
        batch = api(f'pages/projects/{project}/deployments?per_page=25&page={page}')['result']
        deployments.extend(batch)
        if len(batch) < 25:
            break
        page += 1
    baseline = [item for item in deployments if item.get('deployment_trigger', {}).get('metadata', {}).get('commit_hash') == commit and item.get('latest_stage', {}).get('status') == 'success']
    assert baseline, f'{project}: 没有找到已成功发布的认证基线，停止清理'
    threshold = min(created(item) for item in baseline)
    assert created(canonical) >= threshold, f'{project}: 当前生产版本早于认证基线，停止清理'
    legacy = [item for item in deployments if created(item) < threshold and item['id'] != canonical['id']]
    plans.append((project, legacy))
    print(json.dumps({'project': project, 'mode': MODE, 'legacy_count': len(legacy), 'legacy_urls': [item['url'] for item in legacy], 'canonical_preserved': True}, ensure_ascii=False), flush=True)

if MODE == 'cleanup':
    for project, deployments in plans:
        for deployment in deployments:
            # 每次删除前重新确认当前生产版本，避免并发发布时误删正式入口。
            canonical = api(f'pages/projects/{project}')['result']['canonical_deployment']
            assert deployment['id'] != canonical['id'], '目标已成为生产版本，停止清理'
            api(f'pages/projects/{project}/deployments/{deployment["id"]}?force=true', method='DELETE')
            print(json.dumps({'project': project, 'removed_legacy_url': deployment['url']}, ensure_ascii=False), flush=True)

print(json.dumps({'status': 'success', 'mode': MODE, 'legacy_count': sum(len(items) for _, items in plans)}, ensure_ascii=False))
