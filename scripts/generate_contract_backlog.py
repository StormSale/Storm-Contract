import json
import subprocess

res = subprocess.run([
    'gh', 'issue', 'list',
    '--repo', 'StormSale/Storm-Contract',
    '--limit', '120',
    '--json', 'number,title,labels,body,url'
], capture_output=True, text=True, check=True)

issues = json.loads(res.stdout)
issues.sort(key=lambda x: x['number'])

out = []
out.append('# ⚡ StormSale Smart Contract: Production Backlog & Issue Roadmap\n\n')
out.append('> **Live GitHub Issue Tracker:** [StormSale/Storm-Contract Issues](https://github.com/StormSale/Storm-Contract/issues)\n\n')
out.append(f'This document provides the canonical tracking backlog for all **{len(issues)} production issues** on the StormSale Soroban smart contracts. Every issue is categorized with required Drips milestone tags, complexity tiers, and full technical specifications.\n\n')
out.append('## 📊 Summary by Complexity\n\n')

high = sum(1 for i in issues if any(l['name'] == 'complexity: high' for l in i['labels']))
med = sum(1 for i in issues if any(l['name'] == 'complexity: medium' for l in i['labels']))
low = sum(1 for i in issues if any(l['name'] == 'complexity: low' for l in i['labels']))
drips = sum(1 for i in issues if any(l['name'] == 'Drips' for l in i['labels']))

out.append('| Classification | Tag | Count | Status |\n')
out.append('| :--- | :--- | :--- | :--- |\n')
out.append(f'| **Total Open Issues** | `contract` | **{len(issues)}** | Open for Contribution |\n')
out.append(f'| **Drips Eligible** | `Drips` | **{drips}** | Bounty Milestone |\n')
out.append(f'| **High Complexity** | `complexity: high` | **{high}** | Protocol Core & Cryptography |\n')
out.append(f'| **Medium Complexity** | `complexity: medium` | **{med}** | State Machine & Integration |\n')
out.append(f'| **Low Complexity** | `complexity: low` | **{low}** | Entrypoints, Queries & CLI |\n\n')

out.append('---\n\n')
out.append('## 📋 Backlog Catalog\n\n')

for i in issues:
    num = i['number']
    title = i['title']
    url = i['url']
    labels = ', '.join([f'`{l["name"]}`' for l in i['labels']])
    body = i['body'].strip()
    
    out.append(f'### [#{num}: {title}]({url})\n\n')
    out.append(f'- **Issue Link:** {url}\n')
    out.append(f'- **Labels:** {labels}\n\n')
    out.append(body + '\n\n---\n\n')

with open('/home/abujulaybeeb/Documents/Storm/Storm-Contract/BACKLOG.md', 'w') as f:
    f.write(''.join(out))

print(f'Successfully generated BACKLOG.md with {len(issues)} issues!')
