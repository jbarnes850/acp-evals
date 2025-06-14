"""
ACP Agent Discovery for testing real ACP agents.
"""

import httpx
from typing import List, Dict, Any, Optional


class ACPAgentDiscovery:
    """Discover available ACP agents for testing."""
    
    def __init__(self, endpoint: str):
        """
        Initialize agent discovery.
        
        Args:
            endpoint: Base URL of ACP server (e.g., http://localhost:8000)
        """
        self.endpoint = endpoint.rstrip('/')
        self.client = httpx.AsyncClient(timeout=5.0)
    
    async def discover_agents(self) -> List[Dict[str, Any]]:
        """
        Discover agents at the endpoint.
        
        Returns:
            List of agent information dictionaries
        """
        try:
            # Try to get agents from common ACP endpoints
            agents = []
            
            # Try /agents endpoint
            try:
                response = await self.client.get(f"{self.endpoint}/agents")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        agents.extend(data)
                    elif isinstance(data, dict) and 'agents' in data:
                        agents.extend(data['agents'])
            except Exception:
                pass
            
            # If no agents found via API, try common agent names
            if not agents:
                common_agents = ['echo', 'llm', 'story_writer', 'story-writer']
                for agent_name in common_agents:
                    try:
                        # Test if agent responds to health check
                        response = await self.client.get(f"{self.endpoint}/agents/{agent_name}")
                        if response.status_code in [200, 404]:  # 404 is ok, means server is running
                            agents.append({
                                'name': agent_name,
                                'description': f'Agent discovered at {agent_name}',
                                'url': f"{self.endpoint}/agents/{agent_name}"
                            })
                    except Exception:
                        continue
            
            return agents
            
        except Exception as e:
            # Return empty list if can't connect
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()