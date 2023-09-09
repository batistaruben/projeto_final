import xml.etree.ElementTree as ET
import sys
import env_vars
import time

"""
This function reads the XML file "./static/database/notifications.xml" and counts the number
of "notif" elements in the XML file, representing the number of notifications.
"""
def get_notification_count():
    try:
        tree = ET.parse('./static/database/notifications.xml')
        root = tree.getroot()
        return len(root)
    except Exception as e:
        return 0
    
""" 
This function adds a new notification to the XML.
It starts by determining the next ID and creates a "notif" element with the next ID.
The notification type is added with a "type" element, and a timestamp and the notification message are added.
Finally, it updates the notifications and saves the file.
"""
def add_notification_xml(msg, typeOf):
    try:
        if msg:
            tree = ET.parse('./static/database/notifications.xml')  # Load the XML file
            root = tree.getroot()

            # Find the maximum 'id' value in the existing notifications
            max_id = 0
            for notification in root.findall('notif'):
                id_str = notification.get('id')
                if id_str:
                    id_value = int(id_str)
                    max_id = max(max_id, id_value)

            new_id = max_id + 1  # Calculate the new 'id' value

            notification = ET.Element('notif', id=str(new_id))
            
            if typeOf in env_vars.typesOfNot:
                position = env_vars.typesOfNot.index(typeOf)
                env_vars.warnings[position] = True       
                msg_elem1 = ET.SubElement(notification, 'type')
                msg_elem1.text = typeOf
            msg_elem2 = ET.SubElement(notification, 'msg')
            msg_elem2.text = msg+" : "+str(time.asctime(time.localtime(time.time())))

            root.append(notification)
            tree.write('./static/database/notifications.xml')  # Save the updated XML file
            print("WARNINGS->"+str(env_vars.warnings), file=sys.stderr)
            return True
        else:
            print("Error2", file=sys.stderr)
            return False
    except Exception as e:
        print("Error1", file=sys.stderr)
        print(e, file=sys.stderr)
        return False

"""
This function evaluates the type of notifications and sets the environment variables
according to the type of notification.
"""
def evaluate_notif_type(notification_type):
    if notification_type in env_vars.typesOfNot:
        position = env_vars.typesOfNot.index(notification_type)
        env_vars.warnings[position] = False  
    else:
        return

""" 
This function initializes notifications. It reads the XML file and checks if the notification types
match the list of variables.
"""
def start_notifications():
    try:
        tree = ET.parse('./static/database/notifications.xml')  # Load the XML file
        root = tree.getroot()

        for notification in root.findall('notif'):
            type_elem = notification.find('type')

            if type_elem is not None:
                typeOf = type_elem.text

                # Check if typeOf is in your env_vars.typesOfNot array
                if typeOf in env_vars.typesOfNot:
                    position = env_vars.typesOfNot.index(typeOf)
                    env_vars.warnings[position] = True
        print("WARNINGS->"+str(env_vars.warnings), file=sys.stderr)
        return True
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        return False
