import os
import requests

def actualizar_m3u_argentina():
    print("Iniciando descarga de canales globales...")
    url_fuente = "https://iptv-org.github.io/iptv/countries/ar.m3u"
    
    try:
        response = requests.get(url_fuente, timeout=30)
        if response.status_code == 200:
            contenido = response.text
            
            # Aseguramos que la carpeta playlist exista
            os.makedirs("playlist", exist_ok=True)
            
            # Guardamos la lista filtrada de Argentina
            with open("playlist/argentina_completa.m3u", "w", encoding="utf-8") as f:
                f.write(contenido)
                
            print("✅ Lista 'argentina_completa.m3u' actualizada con éxito.")
        else:
            print(f"❌ Error al descargar de la fuente. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    actualizar_m3u_argentina()
