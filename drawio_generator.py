import pickle
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import base64


def load_nodes(filename="input/nodes.pkl"):
    """Загружает и фильтрует узлы дерева"""
    with open(filename, 'rb') as file:
        nodes = pickle.load(file)

    # Находим узел "Птицы" и всех его предков
    birds_node_id = next(
        (k for k, v in nodes.items() if v.name == "Птицы"), None)
    if not birds_node_id:
        return nodes

    # Собираем всех предков для удаления
    to_delete = set()
    current = nodes[birds_node_id]
    while current.parent_id:
        to_delete.add(current.parent_id)
        current = nodes.get(current.parent_id)
        if not current:
            break

    # Удаляем ненужные узлы (Жизнь и все вышестоящие)
    filtered_nodes = {
        k: v for k, v in nodes.items()
        if k not in to_delete and v.name != "Жизнь"
    }

    # Делаем Птицы корневым узлом
    filtered_nodes[birds_node_id].parent_id = None
    return filtered_nodes


def create_base_xml_structure():
    """Создаёт базовую структуру XML-документа"""
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
    """Генерирует HTML для фотографии вида"""
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
    """Создаёт XML-элемент для узла"""
    has_photo = os.path.exists(f"input/photos/{node_id}.png")
    is_species = node.is_species
    is_birds = node.name == "Птицы"  # Убедитесь, что название точно совпадает

    # Стилевые настройки для Птиц
    style = {
        'shape': 'rectangle',
        'html': '1',
        'whiteSpace': 'wrap',
        'fillColor': '#ffffff',
        'strokeColor': '#000000',
        'verticalAlign': 'middle',
        'labelPosition': 'center',
        'spacingTop': '10' if has_photo else '0',
        'fontSize': '22' if is_birds else '14'  # Немного уменьшили размер шрифта
    }

    # Размеры карточки
    if is_birds:
        width, height = 200, 200  # Новый размер квадрата
    else:
        width = 160 if is_species else 180
        base_height = 180 if is_species else 60
        height = base_height + \
            (40 if has_photo and is_species else 20 if has_photo else 0)

    # Генерация HTML-контента
    photo_html = generate_photo_html(node_id) if has_photo else ""
    text_style = [
        "padding: 15px" if is_birds else "padding: 8px",  # Уменьшенный padding
        "font-family: Arial",
        "color: #2c3e50",
        "text-align: center",
        "word-wrap: break-word",
        "width: 100%",
        "box-sizing: border-box",
        "font-weight: bold",
        "display: flex",
        "align-items: center",
        "justify-content: center",
        "height: 100%",
        "line-height: 1.2"  # Добавлено для лучшего межстрочного интервала
    ]

    cell = ET.SubElement(root, 'mxCell', {
        'id': f'node_{node_id}',
        'value': f'''
        <html>
            <body style="margin:0;padding:0;height:100%;width:100%">
                {photo_html if not is_birds else ''}
                <div style="{';'.join(text_style)}">
                    {node.name}
                </div>
                {photo_html if is_birds else ''}
            </body>
        </html>
        ''',
        'style': ';'.join(f"{k}={v}" for k, v in style.items()),
        'vertex': '1',
        'parent': '1'
    })

    ET.SubElement(cell, 'mxGeometry', {
        'width': str(width),
        'height': str(height),
        'as': 'geometry'
    })


def create_edges(root, nodes):
    """Создаёт связи между узлами"""
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
    """Основная функция создания XML"""
    mxfile, root = create_base_xml_structure()

    # Сначала создаём узел "Птицы"
    birds_node = next((k for k, v in nodes.items() if v.name == "Птицы"), None)
    if birds_node:
        create_node_element(root, birds_node, nodes[birds_node])

    # Затем остальные узлы
    for node_id, node in nodes.items():
        if node_id != birds_node:
            create_node_element(root, node_id, node)

    create_edges(root, nodes)

    # Автоматическое расположение
    arrange = ET.SubElement(root, 'mxCell', {
        'id': 'arrange',
        'style': 'tree;verticalTree=1;vertical=1;horizontal=0;resizeParent=1;',
        'vertex': '1',
        'parent': '1'
    })
    ET.SubElement(arrange, 'mxGeometry', {'as': 'geometry'})

    # Сохранение файла
    xml_str = ET.tostring(mxfile)
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent='  ')
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(xml_pretty)


if __name__ == '__main__':
    nodes = load_nodes()
    os.makedirs('output', exist_ok=True)
    create_drawio_xml(nodes, 'output/taxon_tree.drawio')
    print("Файл готов! Откройте taxon_tree.drawio в draw.io и используйте авто-расположение.")
