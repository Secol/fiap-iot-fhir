import paho.mqtt.client as mqtt
import json
import os
import psycopg2

# Configurações do MQTT
broker_address = os.getenv("MQTT_BROKER_ADDRESS", "localhost")
port = os.getenv("MQTT_BROKER_PORTC", 1883)
topic = os.getenv("MQTT_BROKER_TOPIC", "iot/fhir/heart_rate")

# Configurações do PostgreSQL
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "iotdb")
db_user = os.getenv("DB_USER", "user")
db_password = os.getenv("DB_PASWD", "password")

# Conexão com o banco de dados
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
cursor = conn.cursor()

# Função para inserir dados no banco
def insert_into_db(id_patient, heart_beat, record_time):
    sql = "INSERT INTO patient_heart_beat_records (id_patient, heart_beat, record_time) VALUES (%s, %s, %s)"
    cursor.execute(sql, (id_patient, heart_beat, record_time))
    conn.commit()

# Função chamada quando o cliente recebe uma mensagem do broker
def on_message(client, userdata, message):
    # Decodificar a mensagem recebida
    msg_payload = json.loads(message.payload.decode('utf-8'))
    # Formatar id_patient removendo o prefixo "Patient/" e transformando a informação em int
    id_patient = int(msg_payload['subject']['reference'].split('/')[1])
    heart_beat = msg_payload['valueQuantity']['value']
    record_time = msg_payload['effectiveDateTime']

    # Inserir os dados no banco
    insert_into_db(id_patient, heart_beat, record_time)
    print("Dados inseridos no banco de dados")

# Criando uma instância do cliente
client = mqtt.Client("PythonSubscriber")
client.on_message = on_message

# Conectando ao broker
client.connect(broker_address, port)
client.loop_start()
client.subscribe(topic)

try:
    while True:
        pass
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
    cursor.close()
    conn.close()
