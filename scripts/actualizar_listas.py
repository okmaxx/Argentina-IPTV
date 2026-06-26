import os
import requests
import gzip
import shutil

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

def obtener_canales_pluto_tv():
    url = "https://raw.githubusercontent.com/LaQuay/TediTV/master/plutotv_es.m3u"
    canales_pluto = []
    try:
        print("📥 Buscando canales estables de Pluto TV...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            lineas = response.text.splitlines()
            info_canal = ""
            for linea in lineas:
                if linea.startswith("#EXTINF"):
                    info_canal = linea
                elif linea.startswith("http") and info_canal:
                    if 'group-title="' not in info_canal:
                        info_canal = info_canal.replace('#EXTINF:-1 ', '#EXTINF:-1 group-title="Pluto TV" ')
                    canales_pluto.append((info_canal, linea))
                    info_canal = ""
    except Exception as e:
        print(f"❌ Error al obtener Pluto TV: {e}")
    return canales_pluto

def obtener_canales_youtube():
    print("📺 Inyectando señales oficiales de YouTube Noticias...")
    noticias_yt = [
        ('#EXTINF:-1 tvg-id="TN.ar" tvg-name="Todo Noticias" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/TodoNoticias.png", TN (Todo Noticias)', 'plugin://plugin.video.youtube/play/?video_id=hMBK7M7p80w'),
        ('#EXTINF:-1 tvg-id="LNPlus.ar" tvg-name="LN+" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/LNPlus.png", LN+', 'plugin://plugin.video.youtube/play/?video_id=3vU0P-gBv2A'),
        ('#EXTINF:-1 tvg-id="C5N.ar" tvg-name="C5N" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/C5N.png", C5N', 'plugin://plugin.video.youtube/play/?video_id=2O-H_p4zYyE'),
        ('#EXTINF:-1 tvg-id="CronicaTV.ar" tvg-name="Crónica TV" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/CronicaTV.png", Crónica TV', 'plugin://plugin.video.youtube/play/?video_id=3v766D03vE0'),
    ]
    return noticias_yt

def generar_epg_automatizada():
    # Usamos una fuente global muy completa compatible con los IDs de iptv-org
    url_epg_gz = "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml.gz"
    os.makedirs("epg", exist_ok=True)
    
    archivo_gz = "epg/temp_epg.xml.gz"
    archivo_xml = "epg/epg.xml"
    
    try:
        print("📥 Descargando guía de programación (EPG) de Argentina...")
        response = requests.get(url_epg_gz, stream=True, timeout=60)
        
        if response.status_code == 200:
            with open(archivo_gz, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            print("📦 Descomprimiendo EPG...")
            with gzip.open(archivo_gz, 'rb') as f_in:
                with open(archivo_xml, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Limpieza del archivo temporal comprimido
            if os.path.exists(archivo_gz):
                os.remove(archivo_gz)
                
            print("✅ Archivo 'epg/epg.xml' generado y listo para Kodi.")
        else:
            print(f"⚠️ No se pudo descargar la EPG. Código: {response.status_code}. Se mantendrá la anterior si existe.")
            
    except Exception as e:
        print(f"❌ Error al procesar la EPG: {e}")

def procesar_y_guardar_listas():
    os.makedirs("playlist", exist_ok=True)
    canales_finales = []

    canales_finales.extend(obtener_canales_youtube())

    contenido_iptv = obtener_canales_iptv_org()
    if contenido_iptv:
        lineas = contenido_iptv.splitlines()
        info_canal = ""
        for linea in lineas:
            if linea.startswith("#EXTM3U"): continue
            if linea.startswith("#EXTINF"):
                info_canal = linea
            elif linea.startswith("http") and info_canal:
                if "TN" not in info_canal and "C5N" not in info_canal:
                    canales_finales.append((info_canal, linea))
                info_canal = ""

    canales_finales.extend(obtener_canales_pluto_tv())

    print(f"♻️ Total de canales consolidados: {len(canales_finales)}")
    
    # Escribir listas M3U
    with open("playlist/argentina_completa.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in canales_finales:
            f.write(f"{info}\n{url}\n")
            
    with open("playlist/argentina_noticias.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in canales_finales:
            if 'group-title="Noticias"' in info or 'Noticias' in info:
                f.write(f"{info}\n{url}\n")
                
    print("✅ Listas M3U actualizadas con éxito.")

if __name__ == "__main__":
    # Corremos tanto las listas como la guía de programación
    procesar_y_guardar_listas()
    generar_epg_automatizada()
