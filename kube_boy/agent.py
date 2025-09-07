"""LangGraph agent for Kubernetes operations."""

import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from .tools import KUBERNETES_TOOLS


class AgentState(TypedDict):
    """State for the Kubernetes agent."""
    messages: Annotated[List, add_messages]


class KubernetesAgent:
    """LangGraph-based Kubernetes agent for read-only operations."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the Kubernetes agent."""
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            streaming=True
        )
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(KUBERNETES_TOOLS)
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(KUBERNETES_TOOLS))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _call_model(self, state: AgentState) -> Dict[str, Any]:
        """Call the LLM with the current state."""
        system_message = SystemMessage(content=self._get_system_prompt())
        messages = [system_message] + state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue to tools or end."""
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "continue"
        return "end"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are KubeBoy, a helpful Kubernetes assistant that can help users understand and explore their Kubernetes cluster.

You have access to read-only tools that can query various Kubernetes resources including:
- Pods (get_pods)
- Deployments (get_deployments) 
- Services (get_services)
- Nodes (get_nodes)
- Namespaces (get_namespaces)
- Events (get_events)
- Cluster summary (get_cluster_summary)

Key guidelines:
1. You can only perform READ-ONLY operations - no modifications to the cluster
2. Always use the appropriate tool to get current, accurate information
3. When users ask about specific resources, use the namespace parameter if they specify one
4. Provide clear, helpful explanations of the cluster state
5. If you see issues (like failed pods or not-ready nodes), point them out
6. Format your responses in a user-friendly way, not just raw JSON
7. If users ask about troubleshooting, suggest looking at events and pod status
8. Be proactive in suggesting related information that might be helpful

Remember: You are a read-only assistant. You cannot make any changes to the cluster, only observe and report on its current state."""
    
    def chat(self, message: str) -> str:
        """Process a chat message and return the response."""
        try:
            # Create initial state
            initial_state = {"messages": [HumanMessage(content=message)]}
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Get the final AI message
            final_message = result["messages"][-1]
            return final_message.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def chat_stream(self, message: str):
        """Process a chat message and stream the response."""
        try:
            # Create initial state
            initial_state = {"messages": [HumanMessage(content=message)]}
            
            # Stream the graph execution
            async for event in self.graph.astream(initial_state):
                for node_name, node_output in event.items():
                    if node_name == "agent" and "messages" in node_output:
                        message = node_output["messages"][-1]
                        if hasattr(message, 'content') and message.content:
                            yield message.content
                            
        except Exception as e:
            yield f"Sorry, I encountered an error: {str(e)}"
