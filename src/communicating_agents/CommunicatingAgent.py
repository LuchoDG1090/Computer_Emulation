from __future__ import annotations
from typing import Iterable, Set, List
import itertools
import pydot
from pyvis.network import Network

COLOR_PALETTE = [
    "blue", "red", "green", "purple", "orange",
    "brown", "cyan", "magenta", "gray", "darkgreen"
]

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

    def get_agent_info(self):
        link_info = {name: node.id for name, node in self.links.items()}
        parent_id = self.parent.id if self.parent else None

        return (
            f"\033[35mCommunicatingAgent ID={self.id} | "
            f"Links={link_info} | "
            f"Parent={parent_id}\033[0m"
        )


class CommunicatingAgents:
    def __init__(self, name: str = 'G'):
        allowed_names = {"A": "Ă", "B": "B̆", "C": "C̆", "D": "D̆", "E": "Ĕ", "F": "F̆", "G": "Ğ", "H": "H̆", 
                         "I": "Ĭ", "J": "J̆", "K": "K̆", "L": "L̆", "M": "M̆", "N": "N̆", "Ñ": "Ñ̆", "O": "Ŏ", 
                         "P": "P̆", "Q": "Q̆", "R": "R̆", "S": "S̆", "T": "T̆", "U": "Ŭ", "V": "V̆", "W": "W̆", 
                         "X": "X̆", "Y": "Y̆", "Z": "Z̆"}
        if len(name) > 1:
            raise ValueError("Name too long")
        if name not in allowed_names.keys():
            raise ValueError("Name noit allowed, only capital letters")
        self.name = allowed_names[name.upper()]
        self._id_counter = itertools.count()
        self.agents = []

    def add_agent(self, parent=None, links=None, agent_name = None):
        agent = Agent(next(self._id_counter), parent=parent, links=links, agent_name=agent_name)
        self.agents.append(agent)
        return agent

    def add_link(self, origin: Agent, destiny: Agent, name: str):
        if name not in origin.links:
            origin.links[name] = []
        
        origin.links[name].append(destiny)

    def get_agent_info(self):
        link_info = {
            name: [node.id for node in nodes]
            for name, nodes in self.links.items()
        }
        parent_id = self.parent.id if self.parent else None

        return (
            f"\033[35mCommunicatingAgent ID={self.id} | "
            f"Links={link_info} | "
            f"Parent={parent_id}\033[0m"
        )

    def __collect_clustered_nodes(self, node: Agent, visited = None):
        if visited is None:
            visited = set()

        if node in visited:
            return set()

        visited.add(node)
        result = {node}

        for child in node.children:
            result |= self.__collect_clustered_nodes(child, visited)

        return result
    
    def get_bigraph_forest(self, outfile="forest.html"):
        net = Network(directed=False, height='750px', width='100%')

        for agent in self.agents:
            if agent.agent_name:
                net.add_node(agent.id, label=f"Agent {agent.id}", title = agent.agent_name)
            else:
                net.add_node(agent.id, label=f"Agent {agent.id}")

        for agent in self.agents:
            if agent.parent is not None:
                net.add_edge(agent.parent.id, agent.id)

        net.save_graph(outfile)


    def get_hyper_graph(self, outfile="hypergraph.html"):
        net = Network(directed=False, height='750px', width='100%')
        net.barnes_hut(
            gravity=-8000,
            central_gravity=0.5,
            spring_length=50,
            spring_strength=0.01,
            damping=0.09,
            overlap=0,
        )

        for agent in self.agents:
            if agent.agent_name:
                net.add_node(agent.id, label=f'Agent {agent.id}', title = agent.agent_name)
            else:
                net.add_node(agent.id, label=f'Agent {agent.id}')


        complete_links = self.get_links()

        COLOR_PALETTE = [
            "blue", "red", "green", "purple", "orange",
            "brown", "cyan", "magenta", "gray", "darkgreen"
        ]
        tags = list(complete_links.keys())
        tag_color = {
            tag: COLOR_PALETTE[i % len(COLOR_PALETTE)]
            for i, tag in enumerate(tags)
        }

        for tag, pairs in complete_links.items():
            color = tag_color[tag]
            for (src, dst) in pairs:
                net.add_edge(
                    src,
                    dst,
                    label=tag,
                    color=color
                )

        net.save_graph(outfile)


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


    def __build_cluster(self, parent: Agent):
        tag = f"Agent {parent.id} - {parent.agent_name}" if parent.agent_name else f"Agent {parent.id}"

        cluster = pydot.Cluster(
            f"cluster_{parent.id}",
            label=tag,
            style="rounded, filled",
            color="lightgrey",
            fillcolor="#F8F8F8",
        )

        parent_node = pydot.Node(
            str(parent.id),
            shape="ellipse",
            style="filled",
            fillcolor="white"
        )
        cluster.add_node(parent_node)

        for child in parent.children:
            cluster.add_subgraph(self.__build_cluster(child))

        return cluster


    def render_graph(self, outfile="graph.png"):

        graph = pydot.Dot(graph_type="digraph")

        for agent in self.agents:
            if agent.parent is None:
                graph.add_subgraph(self.__build_cluster(agent))


        complete_links = self.get_links()
        tags = list(complete_links.keys())
        tag_color = {
            tag: COLOR_PALETTE[i % len(COLOR_PALETTE)]
            for i, tag in enumerate(tags)
}

        for tag, pairs in complete_links.items():
            color = tag_color[tag]
            for (src, dst) in pairs:
                graph.add_edge(
                    pydot.Edge(
                        str(src),
                        str(dst),
                        style="solid",
                        arrowhead="dot",
                        arrowtail="dot",
                        dir="both",
                        color=color,
                        label=tag,
                        fontsize="10",
                        fontcolor=color
                    )
                )

        graph.write_png(outfile)
        return outfile


