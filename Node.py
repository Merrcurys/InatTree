class Node:
    tax_id: int
    name: str
    parent_id: int
    is_species: bool

    def __init__(self, id, name, parent, is_species):
        self.tax_id = id
        self.name = name
        self.parent_id = parent
        self.is_species = is_species