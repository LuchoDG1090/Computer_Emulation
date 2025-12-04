import customtkinter as ctk
from CommunicatingAgent import CommunicatingAgents

def main():
    agents = CommunicatingAgents()

    # Agent creation
    agent_v0 = agents.add_agent(None, agent_name = "Mi nodo 1")
    agent_v1 = agents.add_agent(agent_v0)
    agent_v2 = agents.add_agent(agent_v0)
    agent_v3 = agents.add_agent(agent_v2)

    agent_v4 = agents.add_agent(None)
    agent_v5 = agents.add_agent(agent_v4)
    agent_v6 = agents.add_agent(agent_v5)

    # Link creation
    agents.add_link(agent_v0, agent_v4, "e0")
    agents.add_link(agent_v1, agent_v5, "e0")
    agents.add_link(agent_v3, agent_v4, "e2")
    agents.add_link(agent_v1, agent_v3, "e1")
    agents.add_link(agent_v3, agent_v5, "e2")
    agents.add_link(agent_v2, agent_v6, "e3")

    agents.get_bigraph_forest()
    agents.get_hyper_graph()
    agents.render_graph()

if __name__ == '__main__':
    main()
    