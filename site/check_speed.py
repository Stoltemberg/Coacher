import urllib.request
import json
import urllib.error

url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://coacher.app.br/&strategy=desktop'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    categories = data['lighthouseResult']['categories']
    print('--- SCORES ---')
    for k, v in categories.items():
        print(f"{v['title']}: {v.get('score', 0) * 100}")
    print('\n--- OPPORTUNITIES / DIAGNOSTICS ---')
    audits = data['lighthouseResult']['audits']
    for k, v in audits.items():
        score = v.get('score')
        if score is not None and score < 1 and v.get('scoreDisplayMode') not in ('notApplicable', 'informative'):
            print(f"[{k}] {v['title']} (Score: {score})")
            if 'displayValue' in v:
                print(f"  Value: {v['displayValue']}")
except Exception as e:
    print(f'Error: {e}')
