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
    
    async def parse_terraform(self, terraform_content: str) -> Dict[str, Any]:
        """
        Parse Terraform content and generate graph structure.
        
        Args:
            terraform_content: HCL content as string
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
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
    
    def _create_node(
        self,
        resource_type: str,
        resource_name: str,
        config: Dict[str, Any]
    ) -> None:
        """
        Create a node from a Terraform resource.
        
        Args:
            resource_type: Type of resource (e.g., 'aws_instance')
            resource_name: Name of resource (e.g., 'web_server')
            config: Resource configuration
        """
        node_id = f"{resource_type}.{resource_name}"
        
        # Get category metadata
        metadata = self.RESOURCE_CATEGORIES.get(
            resource_type,
            {'category': 'other', 'icon': '📦', 'color': '#95A5A6'}
        )
        
        # Extract display name (use tags if available)
        display_name = config.get('tags', {}).get('Name', resource_name)
        
        node = {
            'id': node_id,
            'type': 'custom',
            'data': {
                'label': display_name,
                'resource_type': resource_type,
                'resource_name': resource_name,
                'category': metadata['category'],
                'icon': metadata['icon'],
                'color': metadata['color'],
                'config': config  # Full config for detail view
            },
            'position': {'x': 0, 'y': 0}  # Will be calculated by Dagre
        }
        
        self.nodes.append(node)
        self.resource_map[node_id] = node
    
    def _create_edges(
        self,
        resource_type: str,
        resource_name: str,
        config: Dict[str, Any]
    ) -> None:
        """
        Create edges based on resource references.
        
        Scans config for references like: aws_vpc.main.id
        
        Args:
            resource_type: Current resource type
            resource_name: Current resource name
            config: Resource configuration
        """
        current_id = f"{resource_type}.{resource_name}"
        
        # Pattern to match Terraform references: resource_type.resource_name.attribute
        reference_pattern = r'(\w+\.\w+)\.[\w\*]+'
        
        # Convert config to string for pattern matching
        config_str = str(config)
        
        matches = re.findall(reference_pattern, config_str)
        
        for match in matches:
            # match is like "aws_vpc.main"
            if match in self.resource_map:
                # Create edge from referenced resource to current resource
                edge_id = f"e_{match.replace('.', '_')}_to_{current_id.replace('.', '_')}"
                
                edge = {
                    'id': edge_id,
                    'source': match,  # Resource being referenced
                    'target': current_id,  # Resource doing the referencing
                    'animated': True,
                    'type': 'smoothstep',
                    'style': {'stroke': '#555'}
                }
                
                self.edges.append(edge)
    
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
