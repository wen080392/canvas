"""
Infrastructure Graph Service

Parses Terraform files and generates graph data (nodes + edges) for visualization.
"""

import re
import hcl2
from typing import Dict, List, Any, Tuple, Optional

class InfrastructureGraphService:
    """
    Service to parse Terraform and generate graph structure.
    
    Converts HCL resources into nodes and dependency references into edges.
    """
    
    # Resource type to category mapping for visualization
    RESOURCE_CATEGORIES = {
        'aws_instance': {'category': 'compute', 'icon': '🖥️', 'color': '#FF6B35'},
        'aws_lambda_function': {'category': 'compute', 'icon': 'λ', 'color': '#FF6B35'},
        'aws_s3_bucket': {'category': 'storage', 'icon': '🪣', 'color': '#4ECDC4'},
        'aws_db_instance': {'category': 'database', 'icon': '🗄️', 'color': '#3498DB'},
        'aws_rds_cluster': {'category': 'database', 'icon': '🗄️', 'color': '#3498DB'},
        'aws_dynamodb_table': {'category': 'database', 'icon': '⚡', 'color': '#3498DB'},
        'aws_security_group': {'category': 'network', 'icon': '🛡️', 'color': '#9B59B6'},
        'aws_vpc': {'category': 'network', 'icon': '🌐', 'color': '#9B59B6'},
        'aws_subnet': {'category': 'network', 'icon': '🔗', 'color': '#9B59B6'},
        'aws_iam_role': {'category': 'security', 'icon': '🔐', 'color': '#E74C3C'},
        'aws_kms_key': {'category': 'security', 'icon': '🔑', 'color': '#E74C3C'},
    }
    
    def __init__(self):
        """Initialize the graph service"""
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.resource_map: Dict[str, Dict[str, Any]] = {}
    
    async def parse_terraform(self, content: str) -> Dict[str, Any]:
        """
        Parse Terraform content (HCL or JSON State) and generate graph structure.
        
        Args:
            content: HCL string or JSON state string
        """
        import json
        
        # Try parsing as JSON (State file) first
        try:
            state_data = json.loads(content)
            if 'resources' in state_data or 'modules' in state_data:
                return self.parse_state(state_data)
        except json.JSONDecodeError:
            pass
            
        # Fallback to HCL parsing
        return self._parse_hcl(content)

    def parse_state(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Terraform JSON State file"""
        self.nodes = []
        self.edges = []
        self.resource_map = {}
        
        resources = state_data.get('resources', [])
        
        # Process resources
        for res in resources:
            mode = res.get('mode')
            if mode != 'managed':
                continue
                
            res_type = res.get('type')
            res_name = res.get('name')
            
            # Each resource might have multiple instances
            for instance in res.get('instances', []):
                attrs = instance.get('attributes', {})
                dependencies = instance.get('dependencies', [])
                
                # Use explicit ID if available, else type.name
                # We stick to type.name for graph stability unless strict ID needed
                node_id = f"{res_type}.{res_name}"
                
                # Create Node
                self._create_node(res_type, res_name, attrs)
                
                # Create Edges from dependencies
                for dep in dependencies:
                    # Dep format in state: "module.vpc.aws_subnet.public[0]" or "aws_vpc.main"
                    # We need to normalize to "type.name" to match our node IDs
                    # Simple heuristic: extract type.name from end or known patterns
                    # If dep is "aws_vpc.main", it matches.
                    # If dep contains module path, we might need to handle it.
                    # For now, simplistic matching:
                    parts = dep.split('.')
                    if len(parts) >= 2:
                        # Try to find which part is the types
                        # Usually it is explicit in the string.
                        # Let's clean the dependency ID (remove index)
                        dep_clean = dep.split('[')[0] 
                        
                        # Remove "module.xyz" prefix if we aren't graphing modules
                        # But dependencies in state are absolute.
                        
                        # Create edge if target exists (or create partial edge)
                        if dep_clean != node_id:
                             self._create_raw_edge(dep_clean, node_id)
        
        return {
            'nodes': self.nodes,
            'edges': self.edges
        }

    def _create_raw_edge(self, source_id: str, target_id: str):
        """Create edge with basic validation"""
        edge_id = f"e_{source_id.replace('.', '_')}_{target_id.replace('.', '_')}"
        
        # Avoid duplicates
        if any(e['id'] == edge_id for e in self.edges):
            return

        edge = {
            'id': edge_id,
            'source': source_id,
            'target': target_id,
            'animated': True,
            'type': 'smoothstep',
            'style': {'stroke': '#555'}
        }
        self.edges.append(edge)

    def _parse_hcl(self, terraform_content: str) -> Dict[str, Any]:
        try:
            # Parse HCL
            parsed = hcl2.loads(terraform_content)
            
            # Reset state
            self.nodes = []
            self.edges = []
            self.resource_map = {}
            
            # Extract resources
            resources = parsed.get('resource', [])
            
            # First pass: Create all nodes
            for resource_block in resources:
                for resource_type, instances in resource_block.items():
                    for resource_name, config in instances.items():
                        self._create_node(resource_type, resource_name, config)
            
            # Second pass: Create edges from dependencies
            for resource_block in resources:
                for resource_type, instances in resource_block.items():
                    for resource_name, config in instances.items():
                        self._create_edges(
                            resource_type,
                            resource_name,
                            config
                        )
            
            return {
                'nodes': self.nodes,
                'edges': self.edges
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse Terraform: {e}")

    
    def categorize_nodes_by_layer(self) -> Dict[str, List[str]]:
        """
        Categorize nodes into architectural layers for better layout.
        
        Returns:
            Dictionary mapping layer names to node IDs
        """
        layers = {
            'network': [],
            'security': [],
            'compute': [],
            'storage': [],
            'database': [],
            'other': []
        }
        
        for node in self.nodes:
            category = node['data']['category']
            layers[category].append(node['id'])
        
        return layers
    
    async def get_resource_details(
        self,
        resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific resource.
        
        Args:
            resource_id: Resource ID (e.g., 'aws_instance.web')
        
        Returns:
            Resource details or None if not found
        """
        node = self.resource_map.get(resource_id)
        if not node:
            return None
        
        return {
            'id': resource_id,
            'type': node['data']['resource_type'],
            'name': node['data']['resource_name'],
            'display_name': node['data']['label'],
            'category': node['data']['category'],
            'configuration': node['data']['config']
        }
