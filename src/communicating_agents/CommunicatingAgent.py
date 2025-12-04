from __future__ import annotations
import itertools
from graphics_generator import GraphicsGenerator
from messages import ManageMessages



class Agent:
    def __init__(self, id: int, parent: "Agent" = None, links: dict = None, agent_name:str = None) -> None:
        self.id = id
        self.parent = parent
        self.children = []
        self.links = links.copy() if links else {}
        self.agent_name = agent_name
        self.__check_parent()

    def __check_parent(self):
        if self.parent:
            self.parent.children.append(self)
    
    def send_ack(self, type, origin):
        return f"\033[34mACK {type} inquiry from AGENT-{origin.id} to AGENT-{self.id}\033[0m"

    def get_agent_info(self, links):
        parent_id = self.parent.id if self.parent else None

        return (
            f"\033[35mCommunicatingAgent ID={self.id} | "
            f"Links= {links} | "
            f"Parent= {parent_id} | "
            f"Name= {self.agent_name}\033[0m"
        )
    


class CommunicatingAgents(ManageMessages):
    def __init__(self, name: str = 'G'):
        allowed_names = {"A": "Ă", "B": "B̆", "C": "C̆", "D": "D̆", "E": "Ĕ", "F": "F̆", "G": "Ğ", "H": "H̆", 
                         "I": "Ĭ", "J": "J̆", "K": "K̆", "L": "L̆", "M": "M̆", "N": "N̆", "Ñ": "Ñ̆", "O": "Ŏ", 
                         "P": "P̆", "Q": "Q̆", "R": "R̆", "S": "S̆", "T": "T̆", "U": "Ŭ", "V": "V̆", "W": "W̆", 
                         "X": "X̆", "Y": "Y̆", "Z": "Z̆"}
        if len(name) > 1:
            raise ValueError("Name too long")
        if name not in allowed_names.keys():
            raise ValueError("Name not allowed, only capital letters")
        self.name = allowed_names[name.upper()]
        self._id_counter = itertools.count()
        self.graphics = GraphicsGenerator()
        self.agents = []

    def add_agent(self, parent=None, links=None, agent_name = None):
        agent = Agent(next(self._id_counter), parent=parent, links=links, agent_name=agent_name)
        self.agents.append(agent)
        return agent

    def add_link(self, origin: Agent, destiny: Agent, name: str):
        if name not in origin.links:
            origin.links[name] = []
        
        origin.links[name].append(destiny)

    def __cartessian_product_links(self, bare_links: dict) -> dict:
        for tag, links in bare_links.items():
            if len(links) > 1:
                for primary_link in links:
                    t1_e1, t1_e2 = primary_link

                    for secondary_link in links:
                        t2_e1, t2_e2 = secondary_link
                        link = ()
                        if t1_e1 != t2_e1 and (t1_e1, t2_e1) not in links: 
                            link = (t1_e1, t2_e1)
                        elif t1_e2 != t2_e2 and (t1_e2, t2_e2) not in links:
                            link = (t1_e2, t2_e2)
                        elif (t1_e1, t2_e2) not in links and t1_e1 != t2_e2: 
                            link = (t1_e1, t2_e2)
                        if link and link not in links and (link[1], link[0]) not in links:
                            links.append(link)
        return bare_links

    def get_links(self) -> dict:
        total_links = {}
        for agent in self.agents:
            for tag, destiny in agent.links.items():
                for destination in destiny:
                    if tag not in total_links:
                        total_links[tag] = []
                    total_links[tag].append((agent.id, destination.id))
        return self.__cartessian_product_links(total_links)


    def break_link(self, origin: Agent, link_name: str, target: Agent):
        if link_name in origin.links:
            if target in origin.links[link_name]:
                origin.links[link_name].remove(target)

                if not origin.links[link_name]:
                    del origin.links[link_name]
    
    def get_links_with_id(self, id):
        links_from_id = []
        links = self.get_links()
        for tag, val in links.items():
            for o1, o2 in val:
                if id == o1:
                    links_from_id.append(o2)
                elif id == o2:
                    links_from_id.append(o1)
        return links_from_id


    def send_message(self, message):
        available_channel = self._send_message_validations(message, self.agents, self.get_links())
        if available_channel[0]:
            print(available_channel[2].send_ack(available_channel[3], available_channel[1]))

            if available_channel[3] == "INFO":
                print(available_channel[2].get_agent_info(self.get_links_with_id(available_channel[2].id)))

    def receive_message():
        pass
    
    def get_bigraph(self):
        return self.graphics.render_graph(self.agents, self.get_links())

    def get_hyper_graph(self):
        return self.graphics.get_hyper_graph(self.agents, self.get_links())
    
    def get_forest(self):
        return self.graphics.get_bigraph_forest(self.agents)