from archon.core.agent_cards import generate_agent_cards
from pathlib import Path
import json

data = json.loads(generate_agent_cards(Path('.')))
print(f'Agents: {len(data["agents"])}')
for a in data['agents']:
    cost_tier = a['card']['cost-tier'] if a['card'] else 'N/A'
    print(f'  {a["name"]}: {cost_tier}')
