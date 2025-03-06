import paho.mqtt.client as mqtt
import threading
import time
import random
from datetime import datetime
import json
import os

# Configurações do MQTT
broker_address = os.getenv("MQTT_BROKER_ADDRESS", "localhost")
devices = int(os.getenv("NUMBER_OF_DEVICES", 5))
port = int(os.getenv("MQTT_BROKER_PORT", 1883))
topic_prefix = os.getenv("MQTT_BROKER_TOPIC", "iot/fhir/")

# Função para criar um registro FHIR genérico
def create_fhir_record(measurement, device_id, measurement_type):
    codes = {
        "heart_rate": {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate", "unit": "beats/minute", "system_unit": "http://unitsofmeasure.org", "code_unit": "beats/min"},
        "blood_pressure": {"system": "http://loinc.org", "code": "55284-4", "display": "Blood pressure systolic & diastolic", "unit": "mmHg", "system_unit": "http://unitsofmeasure.org", "code_unit": "mmHg"},
        "respiratory_rate": {"system": "http://loinc.org", "code": "9279-1", "display": "Respiratory rate", "unit": "breaths/minute", "system_unit": "http://unitsofmeasure.org", "code_unit": "breaths/min"},
        "oxygen_saturation": {"system": "http://loinc.org", "code": "59408-5", "display": "Oxygen saturation in Arterial blood", "unit": "%", "system_unit": "http://unitsofmeasure.org", "code_unit": "%"},
        "body_temperature": {"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature", "unit": "degrees Celsius", "system_unit": "http://unitsofmeasure.org", "code_unit": "Cel"}    }
    if measurement_type in ["blood_pressure_systolic", "blood_pressure_diastolic"]:
        measurement_type = "blood_pressure"
    code_info = codes[measurement_type]

    fhir_record = {
        "resourceType": "Observation",
        "id": measurement_type,
        "status": "final",
        "code": {
            "coding": [{
                "system": code_info["system"],
                "code": code_info["code"],
                "display": code_info["display"]
            }]
        },
        "subject": {
            "reference": f"Patient/{device_id}"
        },
        "effectiveDateTime": datetime.now().isoformat(),
        "valueQuantity": {
            "value": measurement,
            "unit": code_info["unit"],
            "system": code_info["system_unit"],
            "code": code_info["code_unit"]
        }
    }

    return json.dumps(fhir_record, indent=4)

# Funções para simular medições
def simulate_measurement(last_value, min_value, max_value):
    return max(min(random.randint(last_value - 5, last_value + 5), max_value), min_value)

# Função que simula um dispositivo IoT enviando dados
def simulate_iot_device(device_id):
    client = mqtt.Client(f"Device_{device_id}")
    client.connect(broker_address, port=port)
    measurements = {"heart_rate": 60, "blood_pressure_systolic": 120, "blood_pressure_diastolic": 80, "respiratory_rate": 16, "oxygen_saturation": 98, "body_temperature": 37}
    
    while True:
        for measurement_type in measurements.keys():
            if measurement_type in ["blood_pressure_systolic", "blood_pressure_diastolic"]:
                measurement = simulate_measurement(measurements[measurement_type], 60 if measurement_type == "blood_pressure_diastolic" else 90, 100 if measurement_type == "blood_pressure_diastolic" else 160)
                topic = f"{topic_prefix}"
            else:
                measurement = simulate_measurement(measurements[measurement_type], 40 if measurement_type == "heart_rate" else 95 if measurement_type == "oxygen_saturation" else 35, 120 if measurement_type == "heart_rate" else 100 if measurement_type == "oxygen_saturation" else 40)
                topic = f"{topic_prefix}{measurement_type}"
            
            fhir_data = create_fhir_record(measurement, device_id, measurement_type)
            client.publish(topic, fhir_data)
            measurements[measurement_type] = measurement  # Atualiza o último valor medido
        time.sleep(5)  # Enviar dados a cada 5 segundos

if __name__ == "__main__":
    print(f"Conectando ao broker MQTT em {broker_address}:{port}")
    print(f"Enviando dados para o tópico {topic_prefix}<measurement_type>")
    print(f"Simulando {devices} dispositivos")
    # Criando e iniciando threads para simular múltiplos dispositivos
    for i in range(devices):
        print(f"Iniciando dispositivo {i+1}")
        device_thread = threading.Thread(target=simulate_iot_device, args=(i+1,))
        device_thread.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Encerrando simulação")
        exit(0)