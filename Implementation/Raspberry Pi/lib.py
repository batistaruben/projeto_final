import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
import sys 
from PIL import Image

path = 'static/database/wiki.xml'

"""
This function evaluates a variable against specified lower and upper limits and ideal, low, and high messages.
It receives a variable, lower and upper limits, and ideal, low, and high messages.
It returns a message based on the evaluation of the variable against the limits.
"""
def evaluate_variable(variable, lower_limit, upper_limit, ideal_message, low_message, high_message):
    if variable < lower_limit:
        return low_message
    elif variable < upper_limit:
        return ideal_message
    else:
        return high_message

"""
This function creates a JavaScript script that displays an alert with a specified message
when called. This script is used to generate alerts on the web page.
"""
def page_alert(msg):
    alert_script = "<script>alert('"+str(msg)+"');</script>"
    return alert_script

"""
This function adds data for a new plant to the XML file "./static/database/wiki.xml".
"""
def add_new_plant(data):
    tree = ET.parse(path)
    root = tree.getroot()

    last_id = int(root[-1].get('id')) if root else 0
    new_id = last_id + 1

    new_plant = ET.Element('plant')
    new_plant.set('id', str(new_id)) 

    for key, value in data.items():
        ET.SubElement(new_plant, key).text = value

    root.append(new_plant)

    tree.write(path, encoding='utf-8', xml_declaration=True)
    return new_id

import xml.dom.minidom as minidom

"""
This method removes blank lines in a text document.
"""
def remove_empty_lines(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    with open(filename, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip():
                file.write(line)

"""
This method updates the data of an existing plant based on its ID.
"""
def update_plant_data(plant_id, data):
    tree = ET.parse(path)
    root = tree.getroot()

    plant_to_update = None
    for plant in root.findall('plant'):
        if plant.get('id') == str(plant_id):
            plant_to_update = plant
            break

    if plant_to_update is not None:
        for key, value in data.items():
            element = plant_to_update.find(key)
            if element is not None:
                element.text = value

        xml_string = ET.tostring(root, encoding="utf-8")
        reparsed = minidom.parseString(xml_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        with open(path, "w", encoding="utf-8") as xml_file:
            xml_file.write(pretty_xml)
        
        remove_empty_lines(path)
        return True 

    return False


"""
This method verifies the data integrity before storing it in the database.
"""
def verify_data(data):
    intervalInvalid = False
    aux = ""
    keys = list(data.keys())
    for key in keys[2:]:
        value = data[key]
        if len(value) > 0 and value != '':
            try:
                float_value = float(value)
            except ValueError:
                return False, "Todos os parâmetros devem ser valores numéricos"

    if len(data['name']) <= 1:
        return False, "Deve conter um Nome válido"

    if data['tempMax'] != "" and data['tempMin'] != "" and float(data['tempMax']) <= float(data['tempMin']):
        aux = 'Temperatura: '
        intervalInvalid = True

    if data['lightMax'] != "" and data['lightMin'] != "" and float(data['lightMax']) <= float(data['lightMin']):
        aux = 'Luz: '
        intervalInvalid = True

    if data['humidMax'] != "" and data['humidMin'] != "" and float(data['humidMax']) <= float(data['humidMin']):
        aux = 'Humidade: '
        intervalInvalid = True

    if data['phMax'] != "" and data['phMin'] != "" and float(data['phMax']) <= float(data['phMin']):
        aux = 'pH: '
        intervalInvalid = True

    if data['ecMax'] != "" and data['ecMin'] != "" and float(data['ecMax']) <= float(data['ecMin']):
        aux = 'EC: '
        intervalInvalid = True

    if intervalInvalid:
        return False, aux + "Máximos devem ser superiores aos Mínimos"

    if len(data['humidMax']) > 0 and len(data['humidMin']) > 0:
        if float(data['humidMax']) > 100 or float(data['humidMin']) < 0:
            return False, "Humidade inválida"

    if len(data['phMax']) > 0 and len(data['phMin']) > 0:
        if float(data['phMax']) > 14 or float(data['phMin']) < 0:
            return False, "pH inválido"
    
    if data['germination'] =='' or len(data['germination'])==0:
        return False, "A Fase - Germinação - é necessária" 

    if data['germination'] !='' or len(data['germination'])>0:
        if float(data['germination']) < 0:
           return False, "Fase com valor inválido (dias negativos)" 
        
    if data['vegetative'] !='' or len(data['vegetative'])>0:
        if float(data['vegetative']) < 0:
           return False, "Fase com valor inválido (dias negativos)" 
        
    if data['floration'] !='' or len(data['floration'])>0:
        if float(data['floration']) < 0:
           return False, "Fase com valor inválido (dias negativos)" 
        
    if data['fruiting'] !='' or len(data['fruiting'])>0:
        if float(data['fruiting']) < 0:
           return False, "Fase com valor inválido (dias negativos)" 

    return True, ""



ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

"""
This function checks if a file name has a valid extension (jpg, jpeg, or png).
"""
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""
This function resizes an image to specific width and height.
"""
def resize_image(image_path, new_path, width, height):
    image = Image.open(image_path)
    if image.format == 'PNG':
        image = image.convert('RGB')
    resized_image = image.resize((width, height), Image.LANCZOS)
    resized_image.save(new_path) 

"""
This function calculates the current growth phase of a plant based on the plant's ID and the number of days since it was planted.
"""
def calculate_plant_phase_id(plant_id, plant_days):
    tree = ET.parse('./static/database/wiki.xml')  # Load the XML file
    root = tree.getroot()

    plant = root.find(f'./plant[@id="{plant_id}"]')
    if plant is not None:
        germination_days = int(str(plant.find('germination').text)) if plant.find('germination').text is not None else None
        vegetative_days  = int(str(plant.find('vegetative').text)) if plant.find('vegetative').text is not None else None
        floration_days   = int(str(plant.find('floration').text)) if plant.find('floration').text is not None else None
        fruiting_days    = int(str(plant.find('fruiting').text)) if plant.find('fruiting').text is not None else None
        if germination_days is not None and (vegetative_days is None or plant_days<vegetative_days):
            return 1  # Germination phase
        elif vegetative_days is not None and (floration_days is None or plant_days<floration_days):
            return 2  # Vegetative phase
        elif floration_days is not None and (fruiting_days is None or plant_days<fruiting_days):
            return 3  # Floration phase
        else:
            return 4  # Fruiting phase (or another phase, if defined)
    else:
        return None
    
"""
This function obtains the non-empty growth phases of a plant based on the plant's ID.
"""
def get_non_empty_phases(plant_id):
    tree = ET.parse('./static/database/wiki.xml')  # Load the XML file
    root = tree.getroot()

    plant = root.find(f'./plant[@id="{plant_id}"]')
    if plant is not None:
        non_empty_phases = []

        germination = plant.find('germination').text
        vegetative = plant.find('vegetative').text
        floration = plant.find('floration').text
        fruiting = plant.find('fruiting').text

        if germination:
            non_empty_phases.append('Germination')
        if vegetative:
            non_empty_phases.append('Vegetative')
        if floration:
            non_empty_phases.append('Floration')
        if fruiting:
            non_empty_phases.append('Fruiting')

        return non_empty_phases
    else:
        return None  # Plant not found