"""Command-line interface for KubeBoy."""

import os
import asyncio
from dotenv import load_dotenv
from .agent import KubernetesAgent


def main():
    """Main CLI function."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required.")
        print("Please set it in your .env file or environment.")
        return
    
    # Initialize the agent
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"Initializing KubeBoy with model: {model_name}")
    
    try:
        agent = KubernetesAgent(model_name=model_name)
        print("✅ KubeBoy initialized successfully!")
        print("🔍 Connected to Kubernetes cluster")
        print("\nType 'help' for suggestions, 'quit' or 'exit' to leave.\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize KubeBoy: {e}")
        print("Make sure you have access to a Kubernetes cluster (kubectl should work)")
        return
    
    # Interactive chat loop
    while True:
        try:
            user_input = input("🤖 KubeBoy> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'help':
                print_help()
                continue
            
            print("\n🔄 Processing...")
            response = agent.chat(user_input)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def print_help():
    """Print help information."""
    help_text = """
🤖 KubeBoy - Your Kubernetes Assistant

Available commands:
• help - Show this help message
• quit/exit - Exit the application

Example questions you can ask:
• "Show me all pods"
• "What deployments are running in the default namespace?"
• "Give me a cluster summary"
• "Show me recent events"
• "Are there any failed pods?"
• "What nodes do I have and what's their status?"
• "List all namespaces"
• "Show me services in the kube-system namespace"

KubeBoy can help you explore and understand your Kubernetes cluster state.
All operations are read-only - no changes will be made to your cluster.
"""
    print(help_text)


if __name__ == "__main__":
    main()
