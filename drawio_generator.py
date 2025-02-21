import pickle
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from dotenv import load_dotenv
import base64


def load_nodes(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def create_drawio_xml(nodes, output_filename):
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2023-10-01T00:00:00',
        'agent': 'Python',
        'type': 'device'
    })
    diagram = ET.SubElement(
        mxfile, 'diagram', {'name': 'Taxon Tree', 'id': 'diagram_1'})
    mxgraph = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '0', 'dy': '0', 'grid': '1', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1',
        'arrows': '1', 'fold': '1', 'page': '1',
        'pageScale': '1', 'pageWidth': '850', 'pageHeight': '1100'
    })
    root = ET.SubElement(mxgraph, 'root')

    # Base cells
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    # Create nodes
    for node_id, node in nodes.items():
        # Photo block
        photo_html = ""
        if node.is_species:
            photo_path = f"photos/{node_id}.png"
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as image_file:
                    encoded_string = base64.b64encode(
                        image_file.read()).decode()
                photo_html = f'''
                <div style="
                    width: 120px; 
                    height: 120px; 
                    background-image: url(data:image/png;base64,{encoded_string});
                    background-size: cover;
                    background-position: center;
                    margin: 0 auto 8px auto;
                    border-radius: 8px;
                    border: 2px solid #6c8ebf;
                "></div>
                '''

        # Style configuration
        style = [
            'shape=rectangle',
            'html=1',
            'whiteSpace=wrap',
            'fillColor=#d5e8d4' if not node.is_species else 'fillColor=#dae8fc',
            'strokeColor=#82b366' if not node.is_species else 'strokeColor=#6c8ebf',
            'verticalAlign=top',
            'labelPosition=center',
            'spacingTop=10',
            'fontSize=14'
        ]

        # Create cell
        cell = ET.SubElement(root, 'mxCell', {
            'id': f'node_{node_id}',
            'value': f'''
            <html>
                <body style="margin:0;padding:0">
                    {photo_html}
                    <div style="
                        padding: 8px;
                        font-family: Arial;
                        color: {'#2d4722' if not node.is_species else '#2c3e50'}
                    ">
                        {node.name}
                    </div>
                </body>
            </html>
            ''',
            'style': ';'.join(style),
            'vertex': '1',
            'parent': '1'
        })

        # Set geometry
        ET.SubElement(cell, 'mxGeometry', {
            'width': '140' if node.is_species else '160',
            'height': '180' if node.is_species else '60',
            'as': 'geometry'
        })

    # Create edges
    edge_id = 0
    for node_id, node in nodes.items():
        if node.parent_id and node.parent_id in nodes:
            edge = ET.SubElement(root, 'mxCell', {
                'id': f'edge_{edge_id}',
                'source': f'node_{node.parent_id}',
                'target': f'node_{node_id}',
                'edge': '1',
                'parent': '1',
                'style': 'endArrow=classic;html=1;jettySize=auto;orthogonalLoop=1;'
            })
            ET.SubElement(edge, 'mxGeometry', {
                          'relative': '1', 'as': 'geometry'})
            edge_id += 1

    # Auto layout
    arrange = ET.SubElement(root, 'mxCell', {
        'id': 'arrange',
        'style': 'tree;verticalTree=1;vertical=1;horizontal=0;resizeParent=1;',
        'vertex': '1',
        'parent': '1'
    })
    ET.SubElement(arrange, 'mxGeometry', {'as': 'geometry'})

    # Save
    xml_str = ET.tostring(mxfile)
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent='  ')
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(xml_pretty)


if __name__ == '__main__':
    load_dotenv()
    filename = os.getenv("pkl_file_name", "nodes.pkl")
    nodes = load_nodes(filename)
    create_drawio_xml(nodes, 'taxon_tree.drawio')
    print("Файл готов! Откройте в draw.io и используйте авто-расположение.")
