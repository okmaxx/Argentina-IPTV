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

def obtener_canales_pluto_tv():
    # Fuente confiable de Pluto TV procesada para la región
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
                    # Solo filtramos canales que tengan contenido relevante para latam/argentina si es necesario, 
                    # o agregamos los destacados de entretenimiento general de Pluto
                    info_canal = linea
                elif linea.startswith("http") and info_canal:
                    # Le añadimos el grupo Pluto TV
                    if 'group-title="' not in info_canal:
                        info_canal = info_canal.replace('#EXTINF:-1 ', '#EXTINF:-1 group-title="Pluto TV" ')
                    canales_pluto.append((info_canal, linea))
                    info_canal = ""
    except Exception as e:
        print(f"❌ Error al obtener Pluto TV: {e}")
    return canales_pluto

def obtener_canales_youtube():
    # Canales de noticias 24/7 oficiales de Argentina vía YouTube (Formato compatible con IPTV)
    print("📺 Inyectando señales oficiales de YouTube Noticias...")
    noticias_yt = [
        ('#EXTINF:-1 tvg-id="TN.ar" tvg-name="Todo Noticias" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/TodoNoticias.png", TN (Todo Noticias)', 'plugin://plugin.video.youtube/play/?video_id=hMBK7M7p80w'),
        ('#EXTINF:-1 tvg-id="LNPlus.ar" tvg-name="LN+" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/LNPlus.png", LN+', 'plugin://plugin.video.youtube/play/?video_id=3vU0P-gBv2A'),
        ('#EXTINF:-1 tvg-id="C5N.ar" tvg-name="C5N" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/C5N.png", C5N', 'plugin://plugin.video.youtube/play/?video_id=2O-H_p4zYyE'),
        ('#EXTINF:-1 tvg-id="CronicaTV.ar" tvg-name="Crónica TV" group-title="Noticias" tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/resources/logos/CronicaTV.png", Crónica TV', 'plugin://plugin.video.youtube/play/?video_id=3v766D03vE0'), # ID dinámico o link directo
    ]
    return noticias_yt

def procesar_y_guardar_listas():
    os.makedirs("playlist", exist_ok=True)
    canales_finales = []

    # 1. Cargar canales de YouTube Noticias
    canales_finales.extend(obtener_canales_youtube())

    # 2. Cargar e integrar IPTV-org
    contenido_iptv = obtener_canales_iptv_org()
    if contenido_iptv:
        lineas = contenido_iptv.splitlines()
        info_canal = ""
        for linea in lineas:
            if linea.startswith("#EXTM3U"): continue
            if linea.startswith("#EXTINF"):
                info_canal = linea
            elif linea.startswith("http") and info_canal:
                # Evitamos duplicar los de noticias si ya los pusimos de YT con mejor calidad
                if "TN" not in info_canal and "C5N" not in info_canal:
                    canales_finales.append((info_canal, linea))
                info_canal = ""

    # 3. Cargar canales de Pluto TV (Agrega variedad de películas, series y anime gratis)
    canales_finales.extend(obtener_canales_pluto_tv())

    print(f"♻️ Total de canales consolidados: {len(canales_finales)}")

    # ---- GENERACIÓN DE ARCHIVOS M3U ----
    
    # Lista Completa
    with open("playlist/argentina_completa.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in canales_finales:
            f.write(f"{info}\n{url}\n")
    print("✅ Lista 'argentina_completa.m3u' generada.")

    # Lista Separada: Solo Noticias
    with open("playlist/argentina_noticias.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in canales_finales:
            if 'group-title="Noticias"' in info or 'Noticias' in info:
                f.write(f"{info}\n{url}\n")
    print("✅ Lista 'argentina_noticias.m3u' generada.")

if __name__ == "__main__":
    procesar_y_guardar_listas()
