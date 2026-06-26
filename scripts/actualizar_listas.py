import os
import requests

def obtener_canales_iptv_org():
    url = "https://iptv-org.github.io/iptv/countries/ar.m3u"
    try:
        print("📥 Descargando canales de IPTV-org...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"❌ Error al obtener IPTV-org: {e}")
    return ""

def procesar_y_guardar_listas():
    # 1. Conseguir el contenido base
    contenido_base = obtener_canales_iptv_org()
    
    if not contenido_base:
        print("❌ No se pudo obtener información de las fuentes. Cancelando actualización.")
        return

    lineas = contenido_base.splitlines()
    canales_argentina = []
    
    # Procesamos las líneas en bloques de dos (la info del canal y su link)
    info_canal = ""
    for linea in lineas:
        if linea.startswith("#EXTM3U"):
            continue
        if linea.startswith("#EXTINF"):
            info_canal = linea
        elif linea.startswith("http") and info_canal:
            # Aquí tenemos el par completo (Información + URL)
            canales_argentina.append((info_canal, linea))
            info_canal = ""

    # Aseguramos que la carpeta playlist exista
    os.makedirs("playlist", exist_ok=True)

    # 2. Generar la lista completa organizada
    print(f"♻️ Procesando {len(canales_argentina)} canales encontrados...")
    
    with open("playlist/argentina_completa.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in canales_argentina:
            f.write(f"{info}\n{url}\n")
            
    print("✅ Lista 'playlist/argentina_completa.m3u' actualizada y limpia.")

if __name__ == "__main__":
    procesar_y_guardar_listas()
