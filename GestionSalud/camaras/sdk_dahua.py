import requests
from requests.auth import HTTPDigestAuth

def obtener_total_canales(ip, usuario, password, puerto=80):
    """
    Se conecta al NVR por HTTP y devuelve el número total de canales reales.
    """
    # Comando CGI de Dahua para obtener la configuración de canales de video
    url = f"http://{ip}:{puerto}/cgi-bin/configManager.cgi?action=getConfig&name=ChannelTitle"
    
    try:
        # Dahua maneja autenticación Digest por seguridad
        response = requests.get(url, auth=HTTPDigestAuth(usuario, password), timeout=4)
        
        if response.status_code == 200:
            lineas = response.text.split('\n')
            canales_encontrados = set()
            
            # Buscamos los índices de canales en la respuesta (ej: table.ChannelTitle[0].Name=...)
            for linea in lineas:
                if "table.ChannelTitle" in linea and "[" in linea:
                    try:
                        indice = linea.split('[')[1].split(']')[0]
                        canales_encontrados.add(int(indice))
                    except (ValueError, IndexError):
                        continue
            
            if canales_encontrados:
                # El total de canales es el índice máximo encontrado + 1 (porque empieza en 0)
                return max(canales_encontrados) + 1
            return 0
        else:
            print(f"Error NVR: Código de estado {response.status_code}")
            return 0
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el NVR ({ip}): {e}")
        return 0