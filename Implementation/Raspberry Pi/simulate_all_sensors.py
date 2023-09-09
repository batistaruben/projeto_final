import paho.mqtt.publish as publish
import threading
from sensor_sim import SensorSimulator

if __name__ == "__main__":
    '''
    Simulators
    
    MQTT topics
    mqtt_topic_airTemp   = "air_temperature"
    mqtt_topic_humidity  = "air_humidity"
    mqtt_topic_waterTemp = "water_temperature"
    mqtt_topic_ph        = "water_ph"
    mqtt_topic_ec        = "water_ec"
    '''
    """
    Aqui é iniciada uma simulação de vários sensores usando tópicos MQTT para publicar
      as leituras simuladas.
    """

    humid_sensor = SensorSimulator("localhost", "air_humidity", 50, 55, 15)
    aTemp_sensor = SensorSimulator("localhost", "air_temperature", 20, 25, 15)
    wTemp_sensor = SensorSimulator("localhost", "water_temperature", 18, 21, 15)
    ph_sensor    = SensorSimulator("localhost", "water_ph", 5.5, 7, 60)
    ec_sensor    = SensorSimulator("localhost", "water_ec", 1, 2, 60)

    # Create threads for each simulator
    humid_thread = threading.Thread(target=humid_sensor.simulate)
    aTemp_thread = threading.Thread(target=aTemp_sensor.simulate)
    wTemp_thread = threading.Thread(target=wTemp_sensor.simulate)
    ph_thread    = threading.Thread(target=ph_sensor.simulate)
    ec_thread    = threading.Thread(target=ec_sensor.simulate)

    # Start the threads
    humid_thread.start()
    aTemp_thread.start()
    wTemp_thread.start()
    ph_thread.start()
    ec_thread.start()


