from archon.core.registry import Registry, AgentCard
reg = Registry()
reg.load()
print(f'Agents: {len(reg.agents)}')
[reg.load_agent_manifest(a) for a in reg.agents]
cards = [a for a in reg.agents if a.card is not None]
print(f'With cards: {len(cards)}')
