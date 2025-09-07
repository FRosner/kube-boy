"""Kubernetes client wrapper for read-only operations."""

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, List, Any, Optional
import json


class KubernetesClient:
    """Wrapper for Kubernetes API client with read-only operations."""
    
    def __init__(self):
        """Initialize the Kubernetes client."""
        try:
            # Try to load in-cluster config first
            config.load_incluster_config()
        except config.ConfigException:
            # Fall back to kubeconfig
            config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.batch_v1 = client.BatchV1Api()
    
    def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pods from the cluster."""
        try:
            if namespace:
                pods = self.v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.v1.list_pod_for_all_namespaces()
            
            return [self._pod_to_dict(pod) for pod in pods.items]
        except ApiException as e:
            raise Exception(f"Error fetching pods: {e}")
    
    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get deployments from the cluster."""
        try:
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            return [self._deployment_to_dict(deployment) for deployment in deployments.items]
        except ApiException as e:
            raise Exception(f"Error fetching deployments: {e}")
    
    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get services from the cluster."""
        try:
            if namespace:
                services = self.v1.list_namespaced_service(namespace=namespace)
            else:
                services = self.v1.list_service_for_all_namespaces()
            
            return [self._service_to_dict(service) for service in services.items]
        except ApiException as e:
            raise Exception(f"Error fetching services: {e}")
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get nodes from the cluster."""
        try:
            nodes = self.v1.list_node()
            return [self._node_to_dict(node) for node in nodes.items]
        except ApiException as e:
            raise Exception(f"Error fetching nodes: {e}")
    
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get namespaces from the cluster."""
        try:
            namespaces = self.v1.list_namespace()
            return [self._namespace_to_dict(ns) for ns in namespaces.items]
        except ApiException as e:
            raise Exception(f"Error fetching namespaces: {e}")
    
    def get_events(self, namespace: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events from the cluster."""
        try:
            if namespace:
                events = self.v1.list_namespaced_event(namespace=namespace, limit=limit)
            else:
                events = self.v1.list_event_for_all_namespaces(limit=limit)
            
            # Sort by timestamp (most recent first)
            sorted_events = sorted(events.items, 
                                 key=lambda x: x.last_timestamp or x.first_timestamp or x.event_time, 
                                 reverse=True)
            
            return [self._event_to_dict(event) for event in sorted_events]
        except ApiException as e:
            raise Exception(f"Error fetching events: {e}")
    
    def _pod_to_dict(self, pod) -> Dict[str, Any]:
        """Convert pod object to dictionary."""
        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "node": pod.spec.node_name,
            "created": pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None,
            "labels": pod.metadata.labels or {},
            "ready": sum(1 for c in (pod.status.container_statuses or []) if c.ready),
            "total_containers": len(pod.spec.containers),
            "restarts": sum(c.restart_count for c in (pod.status.container_statuses or [])),
        }
    
    def _deployment_to_dict(self, deployment) -> Dict[str, Any]:
        """Convert deployment object to dictionary."""
        return {
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "replicas": deployment.spec.replicas,
            "ready_replicas": deployment.status.ready_replicas or 0,
            "available_replicas": deployment.status.available_replicas or 0,
            "created": deployment.metadata.creation_timestamp.isoformat() if deployment.metadata.creation_timestamp else None,
            "labels": deployment.metadata.labels or {},
            "selector": deployment.spec.selector.match_labels or {},
        }
    
    def _service_to_dict(self, service) -> Dict[str, Any]:
        """Convert service object to dictionary."""
        return {
            "name": service.metadata.name,
            "namespace": service.metadata.namespace,
            "type": service.spec.type,
            "cluster_ip": service.spec.cluster_ip,
            "external_ip": service.status.load_balancer.ingress[0].ip if (
                service.status.load_balancer and 
                service.status.load_balancer.ingress and 
                service.status.load_balancer.ingress[0].ip
            ) else None,
            "ports": [{"port": p.port, "target_port": p.target_port, "protocol": p.protocol} 
                     for p in (service.spec.ports or [])],
            "selector": service.spec.selector or {},
            "created": service.metadata.creation_timestamp.isoformat() if service.metadata.creation_timestamp else None,
        }
    
    def _node_to_dict(self, node) -> Dict[str, Any]:
        """Convert node object to dictionary."""
        conditions = {c.type: c.status for c in (node.status.conditions or [])}
        return {
            "name": node.metadata.name,
            "status": "Ready" if conditions.get("Ready") == "True" else "NotReady",
            "roles": [label.split("/")[-1] for label in (node.metadata.labels or {}).keys() 
                     if label.startswith("node-role.kubernetes.io/")],
            "version": node.status.node_info.kubelet_version if node.status.node_info else None,
            "os": node.status.node_info.operating_system if node.status.node_info else None,
            "created": node.metadata.creation_timestamp.isoformat() if node.metadata.creation_timestamp else None,
            "conditions": conditions,
        }
    
    def _namespace_to_dict(self, namespace) -> Dict[str, Any]:
        """Convert namespace object to dictionary."""
        return {
            "name": namespace.metadata.name,
            "status": namespace.status.phase,
            "created": namespace.metadata.creation_timestamp.isoformat() if namespace.metadata.creation_timestamp else None,
            "labels": namespace.metadata.labels or {},
        }
    
    def _event_to_dict(self, event) -> Dict[str, Any]:
        """Convert event object to dictionary."""
        return {
            "namespace": event.namespace,
            "name": event.metadata.name,
            "reason": event.reason,
            "message": event.message,
            "type": event.type,
            "object": f"{event.involved_object.kind}/{event.involved_object.name}",
            "source": event.source.component if event.source else None,
            "first_timestamp": event.first_timestamp.isoformat() if event.first_timestamp else None,
            "last_timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None,
            "count": event.count,
        }
