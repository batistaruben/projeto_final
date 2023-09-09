# Auxiliar Libs
import lib
import stats_lib
import env_vars
import notifications_lib

#Imports
import time
import hashlib
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
import base64 ,os, shutil, secrets, sys
from flask import Flask, Response, redirect, url_for, render_template, request, session, jsonify

# Gerar Chave Secreta para Flask
secret_key = secrets.token_hex(32)

app = Flask(__name__)
app.secret_key = secret_key

#Method to, if needed restart, keep the notifications protocol working 
notifications_lib.start_notifications()

# Path Variables
app.config['UPLOAD_FOLDER'] = 'static/database/plant_images/'
# Directory to store historical data files and backups
base_directory = "static/database/stats"
data_directory = os.path.join(base_directory, "data")
backup_directory = os.path.join(base_directory, "backup")

################
#              #
#     MQTT     #
#              #
################

mqtt_broker_address = "localhost" #Itself

# MQTT topic for temperature and humidity
mqtt_topic_airTemp   = "air_temperature"
mqtt_topic_humidity  = "air_humidity"
mqtt_topic_waterTemp = "water_temperature"
mqtt_topic_ph        = "water_ph"
mqtt_topic_ec        = "water_ec"
latest_temperature       = 0 
latest_humidity          = 0 
latest_water_temperature = 0
latest_ph                = 0
latest_ec                = 0

# Callback for receiving messages from topics
def on_message(client, userdata, message):
    global latest_temperature, latest_humidity, latest_water_temperature, latest_ph, latest_ec
    #print("Msg ->"+str(message), file=sys.stderr)
    payload = message.payload.decode("utf-8")
    print(message.topic, file=sys.stderr)
    print(payload, file=sys.stderr)
    if message.topic == mqtt_topic_airTemp:
        latest_temperature = float(payload)
        if(latest_temperature > env_vars.temperature_max) and (env_vars.warnings[0]==False):
            notifications_lib.add_notification_xml(env_vars.temperature_max_warning_text, env_vars.temperature_max_type)
        elif(latest_temperature < env_vars.temperature_min) and (env_vars.warnings[1]==False):
            notifications_lib.add_notification_xml(env_vars.temperature_min_warning_text, env_vars.temperature_min_type)

    elif message.topic == mqtt_topic_humidity:
        latest_humidity = float(payload)
        if(latest_humidity > env_vars.humidity_max) and (env_vars.warnings[4]==False):
            notifications_lib.add_notification_xml(env_vars.humidity_max_warning_text, env_vars.humidity_max_type)
        elif(latest_humidity < env_vars.humidity_min) and (env_vars.warnings[5]==False):
            notifications_lib.add_notification_xml(env_vars.humidity_min_warning_text, env_vars.humidity_min_type)

    elif message.topic == mqtt_topic_waterTemp:
        latest_water_temperature = float(payload)
        if(latest_water_temperature > env_vars.water_temperature_max) and (env_vars.warnings[2]==False):
            notifications_lib.add_notification_xml(env_vars.water_temperature_max_warning_text, env_vars.water_temperature_max_type)
        elif(latest_water_temperature < env_vars.water_temperature_min) and (env_vars.warnings[3]==False):
            notifications_lib.add_notification_xml(env_vars.water_temperature_min_warning_text, env_vars.water_temperature_min_type)

    elif message.topic == mqtt_topic_ph:
        latest_ph = float(payload)
        if(latest_ph > env_vars.ph_max) and (env_vars.warnings[6]==False):
            notifications_lib.add_notification_xml(env_vars.ph_max_warning_text, env_vars.ph_max_type)
        elif(latest_ph < env_vars.ph_min) and (env_vars.warnings[7]==False):
            notifications_lib.add_notification_xml(env_vars.ph_min_warning_text, env_vars.ph_min_type)

    elif message.topic == mqtt_topic_ec:
        latest_ec = float(payload)
        if(latest_ec > env_vars.ec_max) and (env_vars.warnings[8]==False):
            notifications_lib.add_notification_xml(env_vars.ec_max_warning_text, env_vars.ec_max_type)
        elif(latest_ec < env_vars.ec_min) and (env_vars.warnings[9]==False):
            notifications_lib.add_notification_xml(env_vars.ec_min_warning_text, env_vars.ec_min_type)
    time.sleep(1)


# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker_address, 1883)
mqtt_client.subscribe([(mqtt_topic_airTemp, 0),
                       (mqtt_topic_humidity, 0),
                       (mqtt_topic_waterTemp, 0),
                       (mqtt_topic_ph, 0),
                       (mqtt_topic_ec, 0)])  # Subscribe to all topics
mqtt_client.loop_start()

# Funtions to obtain the latest sensor values from MQTT
def update_temperature_from_mqtt():
    global latest_temperature
    return latest_temperature if latest_temperature is not None else -1

def update_humidity_from_mqtt():
    global latest_humidity
    return latest_humidity if latest_humidity is not None else -1

def update_water_temperature_from_mqtt():
    global latest_water_temperature
    return latest_water_temperature if latest_water_temperature is not None else -1

def update_ph_from_mqtt():
    global latest_ph
    return latest_ph if latest_ph is not None else -1

def update_ec_from_mqtt():
    global latest_ec
    return latest_ec if latest_ec is not None else -1


################
#              #
#  WEB SERVER  #
#              #
################

'''
    Register Page
'''
@app.route('/register')
def register():
    return render_template('register.html')


"""
This method handles user registration. It checks if the user is already registered,
verifies the passwords, creates a password hash, and stores it in the "user_data.txt" file.
"""
@app.route('/registerUser', methods=['POST'])
def registerUser():

    # Check if a user is already registered
    if os.path.exists('user_data.txt'):
        return render_template('register.html')+lib.page_alert("Registo já realizado!")

    # Get the form data
    username        = request.form.get('username')
    password        = request.form.get('password')
    repeat_password = request.form.get('repeatPassword')

    # Validate the passwords
    if password != repeat_password:
        return render_template('register.html')+lib.page_alert("Password's não correspondem!")
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Save the encrypted data in a file
    with open('user_data.txt', 'a') as file:
        file.write(f'{username}:{hashed_password}\n')

    # Redirect to a success page or another route
    return redirect('/')

'''
Login Page
This method handles the Login page. It verifies the entered credentials
and, if they are correct, redirects the user to the main page.
'''
@app.route('/', methods=["POST", "GET"])
def index():
    if 'logged' in session:
        return redirect('main-page')
    
    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")

        # Hash the password input
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if the user exists in the user_data.txt file
        if os.path.exists('user_data.txt'):
            with open('user_data.txt', 'r') as file:
                for line in file:
                    saved_username, saved_hashed_password = line.strip().split(':')
                    if username == saved_username and hashed_password == saved_hashed_password:
                        session['logged'] = True
                        return redirect('main-page')
        
        # If login fails, show an error message
        return render_template('index.html', error="Invalid credentials")+lib.page_alert("Cardenciais Inválidas")

    return render_template('index.html')


'''
    Main Page
    Here is rendered the main page
'''
@app.route('/main-page', methods=["POST", "GET"])
def mainPage():
    if 'logged' not in session:
        return redirect('/')
    else:
        notifications_count = notifications_lib.get_notification_count()
        return render_template('main-page.html', notifications_count=notifications_count)
    
'''
    Stats
    Here is renderes the statistics page
'''
@app.route('/stats')
def stats():
    if 'logged' not in session:
        return redirect('/')
    else:
        notifications_count = notifications_lib.get_notification_count()
        return render_template('stats.html', notifications_count=notifications_count)

'''
    Section about Farm
    Here is rendered the farm page. MQTT updates are read and plant info are loaded
    based on the plants XML file.
'''
@app.route('/farm', methods=["POST", "GET"])
def farm():
    if 'logged' not in session:
        return redirect('/')
    else:
        #Update sensor values
        update_temperature_from_mqtt() 
        update_humidity_from_mqtt()
        update_ec_from_mqtt()
        update_ph_from_mqtt()
        update_water_temperature_from_mqtt()

        #Put updated values into local variables
        temp_var = latest_temperature
        humid_var = latest_humidity
        water_temperature_var = latest_water_temperature
        ph_var = latest_ph
        ec_var = latest_ec

        h2_str = "Temperatura: "+str(temp_var)+"ºC"
        p = lib.evaluate_variable(temp_var, env_vars.temperature_min, env_vars.temperature_max, env_vars.temperature_ideal_text, env_vars.temperature_min_text, env_vars.temperature_max_text)
        param_description = env_vars.temperature_description
        if request.method == "POST":
            if request.form.get('action') == 'temp':
                h2_str = "Temperatura: "+str(temp_var)+"ºC"
                p = lib.evaluate_variable(temp_var, env_vars.temperature_min, env_vars.temperature_max, env_vars.temperature_ideal_text, env_vars.temperature_min_text, env_vars.temperature_max_text)
                param_description = env_vars.temperature_description
            elif request.form.get('action') == 'humid':
                h2_str = "Humidade: "+str(humid_var)+"%"
                p = lib.evaluate_variable(humid_var, env_vars.humidity_min, env_vars.humidity_max, env_vars.humidity_ideal_text, env_vars.humidity_min_text, env_vars.humidity_max_text)
                param_description = env_vars.humidity_description
            elif request.form.get('action') == 'waterTemp':
                h2_str = "Temperatura da Água: "+str(water_temperature_var)+"ºC"
                p = lib.evaluate_variable(water_temperature_var, env_vars.water_temperature_min, env_vars.water_temperature_max, env_vars.water_temperature_ideal_text, env_vars.water_temperature_min_text, env_vars.water_temperature_max_text)
                param_description = env_vars.humidity_description
            elif request.form.get('action') == 'ph':
                h2_str = "pH: "+str(ph_var)
                p = lib.evaluate_variable(ph_var, env_vars.ph_min, env_vars.ph_max, env_vars.ph_ideal_text, env_vars.ph_min_text, env_vars.ph_max_text)
                param_description = env_vars.ph_description
            elif request.form.get('action') == 'ec':
                h2_str = "Eletrocondutividade: "+str(ec_var)
                p = lib.evaluate_variable(ec_var, env_vars.ec_min, env_vars.ec_max, env_vars.ec_ideal_text, env_vars.ec_min_text, env_vars.ec_max_text)
                param_description = env_vars.ec_description

        # Parse the plant XML
        plant_tree = ET.parse('./static/database/wiki.xml')
        plant_root = plant_tree.getroot()
        plant_data = []
        slot_phaseId = []

        plant_tree = ET.parse('./static/database/tower_plant.xml')
        plant_root = plant_tree.getroot()

        for slot in plant_root.findall("slot"):
            plant_id_element = slot.find('plant-id')
            if plant_id_element is not None and plant_id_element.text:
                plant_id_age = slot.find("plant-age").text
                slot_phaseId.append(lib.calculate_plant_phase_id(plant_id_element.text, int(plant_id_age)))
            else:
                slot_phaseId.append('blank')

        plant_tree = ET.parse('./static/database/wiki.xml')
        plant_root = plant_tree.getroot()
        
        # Extract plant data from XML
        for plant_element in plant_root.findall('plant'):
            plant_id = plant_element.get('id')
            plant_name = plant_element.find('name').text
            plant_data.append({'id': plant_id, 'name': plant_name})  
        notifications_count = notifications_lib.get_notification_count()
    return render_template('farm.html', p=p, h2_str=h2_str, plant_data=plant_data, param_description=param_description, l1=slot_phaseId[0], l2=slot_phaseId[1], l3=slot_phaseId[2], l4=slot_phaseId[3], r1=slot_phaseId[4], r2=slot_phaseId[5], r3=slot_phaseId[6], r4=slot_phaseId[7], notifications_count=notifications_count)
    
"""
    Here is handled the plant adding to the hydroponic tower slots
"""
@app.route('/add-plant', methods=["POST"])
def add_plant():
    plant_id = request.form.get('plantId')
    plant_fase = request.form.get('plantFase')
    slot_id = request.form.get('slotId')
    slot_id = slot_id[-2:].upper()
    plant_insert_date = request.form.get('insertedDate')

    tree = ET.parse('./static/database/wiki.xml')
    root = tree.getroot()

    plant = root.find(f'./plant[@id="{plant_id}"]')
    if plant is not None:
        if plant_fase == "1":  # Germination
            plant_fase_element = plant.find('germination')
        elif plant_fase == "2":  # Vegetative
            plant_fase_element = plant.find('vegetative')
        elif plant_fase == "3":  # Floration
            plant_fase_element = plant.find('floration')
        else: #Fruiting
            plant_fase_element = plant.find('fruiting')

        if plant_fase_element is not None and plant_fase_element.text:  # Check if value exists
            plant_fase_value = plant_fase_element.text
        else:
            response = {'message': f'Phase {plant_fase} does not have a value in the XML', 'reload': True}
            return jsonify(response)
    else:
        response = {'message': f'Plant {plant_id} not found', 'reload': False}
        return jsonify(response)

    plant_tree = ET.parse('./static/database/tower_plant.xml')
    plant_root = plant_tree.getroot()

    for slot in plant_root.findall("slot"):
        if slot.get("id") == slot_id:
            plant_id_element = slot.find("plant-id")
            plant_id_element.text = plant_id

            plant_fase_element = slot.find("plant-age")
            plant_fase_element.text = plant_fase_value

            insert_date_element = slot.find("plant-inserted-date")
            insert_date_element.text = plant_insert_date

    plant_tree.write('./static/database/tower_plant.xml')

    response = {'message': f'Plant added - {plant_id} - {plant_fase_value} - {slot_id} - successfully', 'reload': False}
    return jsonify(response)


"""
    Here is handled the plants removal to the hydroponic tower slots
"""
@app.route('/rem-plant', methods=["POST"])
def rem_plant():
    slot_id = request.form.get('slotId')
    slot_id = slot_id[-2:].upper()

    plant_tree = ET.parse('./static/database/tower_plant.xml')
    plant_root = plant_tree.getroot()

    for slot in plant_root.findall("slot"):
        if slot.get("id") == slot_id:
            plant_id_element = slot.find("plant-id")
            plant_id_element.text = ""
            plant_fase_element = slot.find("plant-age")
            plant_fase_element.text = ""
            insert_date_element = slot.find("plant-inserted-date")
            insert_date_element.text = ""

    plant_tree.write('./static/database/tower_plant.xml')
    
    response = {'message': 'Plant removed - '+slot_id+' - successfully - ','reload': True}
    return jsonify(response)

'''
    End Section about Farm
'''

'''
    Section about Hydrowiki
    Here is rendered the hydrowiki section.
'''
@app.route('/hydrowiki')
def hydrowiki():
    if 'logged' not in session:
        return redirect('/')
    else:
        notifications_count = notifications_lib.get_notification_count()
        return render_template('hydrowiki.html', notifications_count=notifications_count)
    
"""
   This route handles the adding of new information of plants to the hydrowiki.
"""
@app.route('/hydrowiki_plants')
def hydrowiki_plants():
    if 'logged' not in session:
        return redirect('/')
    else:
        notifications_count = notifications_lib.get_notification_count()
        return render_template('hydrowiki_plants.html', notifications_count=notifications_count)
    
""" 
    Here is rendered the editing page to the wiki
"""
@app.route('/hydrowiki_add')
def hydrowiki_add():
    if 'logged' not in session:
        return redirect('/')
    else:
        return render_template('hydrowiki_add.html')
    
"""
    Here is rendered the editing page of the wiki
"""
@app.route('/hydrowiki_edit/plant_id=<int:plant_id>', methods=['GET', 'POST'])
def hydrowiki_edit(plant_id):
    if 'logged' not in session:
        return redirect('/')
    else:
        return render_template('hydrowiki_edit.html', plant_id=plant_id)

"""
    Here is done the plant edition on the XML file
"""
@app.route('/edit_plant_wiki', methods=['GET', 'POST'])
def edit_plant_wiki():
    if request.method == 'POST':
        plant_id = request.form.get('plant_id')  
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'tempMin': request.form['temp_min'],
            'tempMax': request.form['temp_max'],
            'lightMin': request.form['light_min'],
            'lightMax': request.form['light_max'],
            'humidMin': request.form['humid_min'],
            'humidMax': request.form['humid_max'],
            'phMin': request.form['ph_min'],
            'phMax': request.form['ph_max'],
            'ecMin': request.form['ec_min'],
            'ecMax': request.form['ec_max'],
            'germination': request.form['germin_value'],
            'vegetative': request.form['veget_value'],
            'floration': request.form['flor_value'],
            'fruiting': request.form['fruit_value'],
        }
        print(plant_id, file=sys.stderr)
        print(data, file=sys.stderr)

        verified, msg = lib.verify_data(data)
        if(verified and lib.update_plant_data(plant_id, data)):
            image_base64 = request.form.get('image_base64')
            
            if image_base64:
                filename = f"{str(plant_id)}.jpeg"
                image_data = base64.b64decode(image_base64)
                with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                    f.write(image_data)
                resized_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                lib.resize_image(resized_path, resized_path, 1024, 1024)
            else:
                previous_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{str(plant_id)}.jpeg")
                if not os.path.exists(previous_image_path):
                    default_image_path = 'static/database/default.png'
                    filename = str(plant_id) + '.jpeg'
                    destination_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    shutil.copyfile(default_image_path, destination_path)
                    lib.resize_image(destination_path, destination_path, 1024, 1024)

            return redirect(url_for('hydrowiki_plants', alert_type='success'))
        else:
            return render_template('hydrowiki_edit.html', plant_id=plant_id)+lib.page_alert(msg)
    return redirect(url_for('hydrowiki_plants'))

"""
    This route handles the edition of new plants to the wiki
"""
@app.route('/add_plant_wiki', methods=['GET', 'POST'])
def add_plant_wiki():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'tempMin': request.form['temp_min'],
            'tempMax': request.form['temp_max'],
            'lightMin': request.form['light_min'],
            'lightMax': request.form['light_max'],
            'humidMin': request.form['humid_min'],
            'humidMax': request.form['humid_max'],
            'phMin': request.form['ph_min'],
            'phMax': request.form['ph_max'],
            'ecMin': request.form['ec_min'],
            'ecMax': request.form['ec_max'],
            'germination': request.form['germin_value'],
            'vegetative': request.form['veget_value'],
            'floration': request.form['flor_value'],
            'fruiting': request.form['fruit_value'],
        }
        print(data, file=sys.stderr)
        
        verified, msg = lib.verify_data(data)
        if(verified):
            plant_id = lib.add_new_plant(data)   
            image_base64 = request.form.get('image_base64')

            if image_base64:
                filename = f"{str(plant_id)}.jpeg"
                image_data = base64.b64decode(image_base64)
                with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                    f.write(image_data)
                resized_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                lib.resize_image(resized_path, resized_path, 1024, 1024)
            else:
                default_image_path = 'static/database/default.png'
                filename = str(plant_id) + '.jpeg'
                destination_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                shutil.copyfile(default_image_path, destination_path)
                lib.resize_image(destination_path, destination_path, 1024, 1024)

            return render_template('hydrowiki_add.html')+lib.page_alert('Planta adicionada à Wiki!')
        else:
            return render_template('hydrowiki_add.html')+lib.page_alert(msg)
    
    return render_template('hydrowiki_add.html')

"""
    This route handles the removing of plants to the wiki.
"""
@app.route('/rem-plant-wiki', methods=["POST"])
def rem_plant_wiki():
    plant_id = request.form.get('plantId')

    plant_tree = ET.parse('./static/database/wiki.xml')
    plant_root = plant_tree.getroot()

    # Find the plant element with the plant_id
    plant_element = plant_root.find(f"./plant[@id='{plant_id}']")
    
    if plant_element is not None:
        plant_root.remove(plant_element)
        plant_tree.write('./static/database/wiki.xml')  # Save the modified XML
        # Remove the associated image file (assuming it's in the same directory)
        image_filename = f'./static/database/plant_images/{plant_id}.jpeg'
        if os.path.exists(image_filename):
            os.remove(image_filename)
        response = {'message': 'Plant removed - ' + plant_id + ' - successfully from Wiki', 'reload': True}
    else:
        response = {'message': 'Plant not found with ID - ' + plant_id}
    
    return jsonify(response)

### NOTIF SECTION ###
"""
    This routes handles the notification removing
"""
@app.route('/remove-notification', methods=['POST'])
def remove_notification():
    try:
        notification_id = request.form.get('notificationId')

        if notification_id:
            tree = ET.parse('./static/database/notifications.xml')  # Load the XML file
            root = tree.getroot()

            notification_to_remove = root.find(f'./notif[@id="{notification_id}"]')
            if notification_to_remove:

                # Access the <type> element within the notification
                notification_type_element = notification_to_remove.find('type')
                
                if notification_type_element is not None:
                    notifications_lib.evaluate_notif_type(notification_type_element.text)
                    root.remove(notification_to_remove)
                    tree.write('./static/database/notifications.xml')  # Save the updated XML file
                    #print(vars.warnings, file=sys.stderr)
                    return "Notification removed successfully"
                else:
                    root.remove(notification_to_remove)
                    tree.write('./static/database/notifications.xml')  # Save the updated XML file
                    return "Notification removed successfully"
            else:
                return "Notification not found", 404
        else:
            return "Notification ID cannot be empty", 400
    except Exception as e:
        return str(e), 500

"""
    This route obtains notifications in XML
"""
@app.route('/get-notifications-xml')
def get_notifications_xml():

    tree = ET.parse('./static/database/notifications.xml')
    root = tree.getroot()

    # Create an XML response
    xml_response = ET.tostring(root, encoding='utf-8', method='xml')

    # Set the response headers to indicate XML content
    response = Response(xml_response, content_type='application/xml')
    return response
### END NOTIF SECTION ###

'''
    End Section About Hydrowiki
'''

################
#              #
#    STATS     #
#              #
################

"""
     This code runs on a thread separated to save data from sensors in CSV
"""
def data_recording_thread():
    #Control variables
    last_ph_save_time = time.time()  
    last_ec_save_time = time.time() 

    #Files creation if needed
    if not os.path.exists(stats_lib.temperature_data_file(data_directory)):
        stats_lib.create_csv_with_header(stats_lib.temperature_data_file(data_directory))
    if not os.path.exists(stats_lib.humidity_data_file(data_directory)):
        stats_lib.create_csv_with_header(stats_lib.humidity_data_file(data_directory))
    if not os.path.exists(stats_lib.water_temperature_data_file(data_directory)):
        stats_lib.create_csv_with_header(stats_lib.water_temperature_data_file(data_directory)) 
    if not os.path.exists(stats_lib.ph_data_file(data_directory)):
        stats_lib.create_csv_with_header(stats_lib.ph_data_file(data_directory))
    if not os.path.exists(stats_lib.ec_data_file(data_directory)):
        stats_lib.create_csv_with_header(stats_lib.ec_data_file(data_directory))

    #Inifinite Data append
    while True:
        # Check if it's a new day and create new data files if needed
        current_date = stats_lib.get_current_date()
        stats_lib.append_to_csv(stats_lib.temperature_data_file(data_directory), latest_temperature)
        stats_lib.append_to_csv(stats_lib.humidity_data_file(data_directory), latest_humidity)
        stats_lib.append_to_csv(stats_lib.water_temperature_data_file(data_directory), latest_water_temperature) 
        
        ph_interval = time.time() - last_ph_save_time
        ec_interval = time.time() - last_ec_save_time

        if ph_interval >= 3600:  # 3600 secs = 1 hr
            stats_lib.append_to_csv(stats_lib.ph_data_file(data_directory), latest_ph)
            time.sleep(1)
            last_ph_save_time = time.time() 

        if ec_interval >= 600:  # 600 seconds = 10 min
            stats_lib.append_to_csv(stats_lib.ec_data_file(data_directory), latest_ec)
            time.sleep(1)
            last_ec_save_time = time.time()

        if datetime.now().hour == 0:  # Midnight
            stats_lib.create_backup()
        
        time.sleep(30)  # Sleep for 30 seconds before checking again
        

"""
    This route obtains data from sensors
"""
@app.route('/data')
def get_data():
    parameter = request.args.get('parameter')
    date = request.args.get('date')  # 'yyyy-mm-dd' 

    # Call the function to read data
    data = stats_lib.read_data(parameter, date)

    return jsonify(data)



if __name__=='__main__':

    # Abre os ficheiros de dados para escrita (data e backup)
    os.makedirs(data_directory, exist_ok=True)
    os.makedirs(backup_directory, exist_ok=True)

    # Inicia uma thread separada para a gravação contínua de dados e backups
    data_thread = threading.Thread(target=data_recording_thread)
    data_thread.daemon = True
    data_thread.start()

    # Inicia o servidor da web Flask em modo debug
    app.run(debug=True)