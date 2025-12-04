import pydot
import networkx as nx
import matplotlib.pyplot as plt


COLOR_PALETTE = [
    "blue", "red", "green", "purple", "orange",
    "brown", "cyan", "magenta", "gray", "darkgreen"
]

node_size = 3200
font_size_nodes = 20
edge_width = 3.5
font_size_edges = 20


class GraphicsGenerator():
    def __init__(self):
        pass

    def __build_cluster(self, parent):
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


    def render_graph(self, agents, complete_links, outfile="graph.png", width=1000, height=800):
        graph = pydot.Dot(graph_type="digraph")
        graph.set_size(f"{width},{height}!")

        for agent in agents:
            if agent.parent is None:
                graph.add_subgraph(self.__build_cluster(agent))

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


    def get_bigraph_forest(self, agents, outfile="forest.png"):
        G = nx.Graph()

        for agent in agents:
            label = f"Agent {agent.id}"
            G.add_node(agent.id, label = label)

        for agent in agents:
            if agent.parent is not None:
                G.add_edge(agent.parent.id, agent.id)

        pos = nx.spring_layout(G, seed = 42, k = 1.5, iterations=120)

        plt.figure(figsize=(14, 12))

        nx.draw_networkx_nodes(
            G,
            pos,
            node_size=node_size,
            node_color="#A8C5E8",
            edgecolors="black",
            linewidths=1.5
        )

        nx.draw_networkx_edges(
            G,
            pos,
            width=edge_width
        )

        nx.draw_networkx_labels(
            G,
            pos,
            labels={n: G.nodes[n]["label"] for n in G.nodes()},
            font_size=14,
            font_weight="bold"
        )

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(outfile, dpi=300, bbox_inches="tight")
        plt.close()

        return outfile


    def get_hyper_graph(self, agents, complete_links,outfile="hypergraph.png"):
        G = nx.Graph()

        for agent in agents:
            label = f"Agent {agent.id}"
            G.add_node(agent.id, label=label)

        tags = sorted(list(complete_links.keys()))
        tag_color = {tag: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, tag in enumerate(tags)}


        edge_colors = []
        for tag, pairs in complete_links.items():
            color = tag_color[tag]
            for (src, dst) in pairs:
                G.add_edge(src, dst, tag=tag)
                edge_colors.append(color)

        pos = nx.spring_layout(G, seed=42, k=2)


        plt.figure(figsize=(14, 12))

        nx.draw_networkx_nodes(
            G,
            pos,
            node_size=node_size,
            node_color="#A8C5E8",
            edgecolors="black",
            linewidths=1.5
        )

        nx.draw_networkx_labels(
            G,
            pos,
            font_size=font_size_nodes,
            font_weight="bold"
        )

        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=edge_width
        )

        edge_labels = {(u, v): G[u][v]["tag"] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=font_size_edges
        )

        plt.axis("off")
        plt.tight_layout()
        plt.savefig(outfile, dpi=300, bbox_inches="tight")
        plt.close()

        return outfile