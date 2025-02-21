from graphviz import Digraph
import pickle
import os
from dotenv import load_dotenv

load_dotenv()


def create_tree(nodes):
    dot = Digraph(comment="Taxonomic Tree", format='svg', engine="neato", node_attr={'shape': 'rect'})
    dot.attr(overlap="false", splines='true', sep="+20", damping='3')

    for tax_id, node in nodes.items():
        label = node.name.replace('-', '\n').replace(' ', '\n')
        if node.is_species:
            dot.node(str(tax_id), label, image=f"photos/{tax_id}.png", imagepos='mc',
                     width="1.3", height="1.3", fixedsize="true", fontcolor="white")
        else:
            dot.node(str(tax_id), label)

    for tax_id, node in nodes.items():
        if node.parent_id is not None:
            dot.edge(str(node.parent_id), str(tax_id))

    dot.render("taxonomic_tree.gv", view=True)


def load_nodes(filename=os.getenv("pkl_file_name")):
    with open(filename, "rb") as file:
        return pickle.load(file)


create_tree(load_nodes())