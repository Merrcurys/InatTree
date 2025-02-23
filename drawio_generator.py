import pickle
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import base64


def load_nodes(filename="input/nodes.pkl"):
    """Загружает узлы дерева из pickle-файла"""
    with open(filename, 'rb') as file:
        return pickle.load(file)


def create_base_xml_structure():
    """Создаёт базовую структуру XML-документа для draw.io"""
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
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    return mxfile, root


def generate_photo_html(node_id):
    """Генерирует HTML для отображения фотографии вида"""
    photo_path = f"input/photos/{node_id}.png"
    if not os.path.exists(photo_path):
        return ""

    with open(photo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return f'''
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


def create_node_element(root, node_id, node):
    """Создаёт XML-элемент для узла дерева"""
    has_photo = os.path.exists(f"input/photos/{node_id}.png")
    is_species = node.is_species

    # Стилевые настройки
    style = {
        'shape': 'rectangle',
        'html': '1',
        'whiteSpace': 'wrap',
        'fillColor': '#ffffff',
        'strokeColor': '#000000',
        'verticalAlign': 'top' if has_photo else 'middle',
        'labelPosition': 'center',
        'spacingTop': '10' if has_photo else '0',
        'fontSize': '14',
        'rounded': '1'  # Закругление углов
    }

    # Размеры карточки
    base_width = 160 if is_species else 180
    base_height = 180 if is_species else 60

    # Увеличиваем высоту для карточек с фото
    if has_photo:
        base_height += 40 if is_species else 20

    # Генерация HTML-контента
    photo_html = generate_photo_html(node_id) if has_photo else ""
    text_style = [
        "padding: 8px",
        "font-family: Arial",
        "color: #2c3e50",
        "text-align: center",
        "word-wrap: break-word",
        "width: 100%",
        "box-sizing: border-box"
    ]

    cell = ET.SubElement(root, 'mxCell', {
        'id': f'node_{node_id}',
        'value': f'''
        <html>
            <body style="margin:0;padding:0;height:100%;width:100%">
                {photo_html}
                <div style="{';'.join(text_style)}">
                    {node.name}
                </div>
            </body>
        </html>
        ''',
        'style': ';'.join(f"{k}={v}" for k, v in style.items()),
        'vertex': '1',
        'parent': '1'
    })

    ET.SubElement(cell, 'mxGeometry', {
        'width': str(base_width),
        'height': str(base_height),
        'as': 'geometry'
    })


def create_edges(root, nodes):
    """Создаёт связи между узлами дерева"""
    for edge_id, (node_id, node) in enumerate(nodes.items()):
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


def create_drawio_xml(nodes, output_filename):
    """Основная функция создания XML-файла для draw.io"""
    # Создаём базовую структуру документа
    mxfile, root = create_base_xml_structure()

    # Добавляем все узлы
    for node_id, node in nodes.items():
        create_node_element(root, node_id, node)

    # Добавляем связи между узлами
    create_edges(root, nodes)

    # Добавляем автоматическое расположение
    arrange = ET.SubElement(root, 'mxCell', {
        'id': 'arrange',
        'style': 'tree;verticalTree=1;vertical=1;horizontal=0;resizeParent=1;',
        'vertex': '1',
        'parent': '1'
    })
    ET.SubElement(arrange, 'mxGeometry', {'as': 'geometry'})

    # Сохраняем результат в файл
    xml_str = ET.tostring(mxfile)
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent='  ')
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(xml_pretty)


if __name__ == '__main__':
    nodes = load_nodes()
    os.makedirs('output', exist_ok=True)
    create_drawio_xml(nodes, 'output/taxon_tree.drawio')
    print("Файл готов! Откройте taxon_tree.drawio в draw.io и используйте авто-расположение.")
