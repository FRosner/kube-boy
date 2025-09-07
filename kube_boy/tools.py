"""Kubernetes tools for the LangGraph agent."""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from .k8s_client import KubernetesClient
import json


# Global client instance
k8s_client = KubernetesClient()


@tool
def get_pods(namespace: Optional[str] = None) -> str:
    """
    Get information about pods in the Kubernetes cluster.
    
    Args:
        namespace: Optional namespace to filter pods. If None, gets pods from all namespaces.
    
    Returns:
        JSON string containing pod information including name, namespace, status, node, etc.
    """
    try:
        pods = k8s_client.get_pods(namespace)
        return json.dumps(pods, indent=2)
    except Exception as e:
        return f"Error getting pods: {str(e)}"


@tool
def get_deployments(namespace: Optional[str] = None) -> str:
    """
    Get information about deployments in the Kubernetes cluster.
    
    Args:
        namespace: Optional namespace to filter deployments. If None, gets deployments from all namespaces.
    
    Returns:
        JSON string containing deployment information including name, replicas, status, etc.
    """
    try:
        deployments = k8s_client.get_deployments(namespace)
        return json.dumps(deployments, indent=2)
    except Exception as e:
        return f"Error getting deployments: {str(e)}"


@tool
def get_services(namespace: Optional[str] = None) -> str:
    """
    Get information about services in the Kubernetes cluster.
    
    Args:
        namespace: Optional namespace to filter services. If None, gets services from all namespaces.
    
    Returns:
        JSON string containing service information including name, type, ports, selectors, etc.
    """
    try:
        services = k8s_client.get_services(namespace)
        return json.dumps(services, indent=2)
    except Exception as e:
        return f"Error getting services: {str(e)}"


@tool
def get_nodes() -> str:
    """
    Get information about nodes in the Kubernetes cluster.
    
    Returns:
        JSON string containing node information including name, status, roles, version, etc.
    """
    try:
        nodes = k8s_client.get_nodes()
        return json.dumps(nodes, indent=2)
    except Exception as e:
        return f"Error getting nodes: {str(e)}"


@tool
def get_namespaces() -> str:
    """
    Get information about namespaces in the Kubernetes cluster.
    
    Returns:
        JSON string containing namespace information including name, status, labels, etc.
    """
    try:
        namespaces = k8s_client.get_namespaces()
        return json.dumps(namespaces, indent=2)
    except Exception as e:
        return f"Error getting namespaces: {str(e)}"


@tool
def get_events(namespace: Optional[str] = None, limit: int = 20) -> str:
    """
    Get recent events from the Kubernetes cluster.
    
    Args:
        namespace: Optional namespace to filter events. If None, gets events from all namespaces.
        limit: Maximum number of events to return (default: 20).
    
    Returns:
        JSON string containing recent events with reason, message, object, timestamps, etc.
    """
    try:
        events = k8s_client.get_events(namespace, limit)
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error getting events: {str(e)}"


@tool
def get_cluster_summary() -> str:
    """
    Get a high-level summary of the Kubernetes cluster.
    
    Returns:
        JSON string containing cluster summary with counts of various resources.
    """
    try:
        summary = {}
        
        # Get counts of various resources
        nodes = k8s_client.get_nodes()
        summary["nodes"] = {
            "total": len(nodes),
            "ready": len([n for n in nodes if n["status"] == "Ready"]),
            "not_ready": len([n for n in nodes if n["status"] != "Ready"])
        }
        
        namespaces = k8s_client.get_namespaces()
        summary["namespaces"] = {
            "total": len(namespaces),
            "active": len([ns for ns in namespaces if ns["status"] == "Active"])
        }
        
        pods = k8s_client.get_pods()
        summary["pods"] = {
            "total": len(pods),
            "running": len([p for p in pods if p["status"] == "Running"]),
            "pending": len([p for p in pods if p["status"] == "Pending"]),
            "failed": len([p for p in pods if p["status"] == "Failed"]),
            "succeeded": len([p for p in pods if p["status"] == "Succeeded"])
        }
        
        deployments = k8s_client.get_deployments()
        summary["deployments"] = {
            "total": len(deployments),
            "ready": len([d for d in deployments if d["ready_replicas"] == d["replicas"]])
        }
        
        services = k8s_client.get_services()
        summary["services"] = {
            "total": len(services),
            "cluster_ip": len([s for s in services if s["type"] == "ClusterIP"]),
            "node_port": len([s for s in services if s["type"] == "NodePort"]),
            "load_balancer": len([s for s in services if s["type"] == "LoadBalancer"])
        }
        
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error getting cluster summary: {str(e)}"


# List of all available tools
KUBERNETES_TOOLS = [
    get_pods,
    get_deployments,
    get_services,
    get_nodes,
    get_namespaces,
    get_events,
    get_cluster_summary,
]
