from datetime import datetime, timedelta
from html import escape
from pathlib import Path
import json

CONFIG_FILE = "channels.json"

def fmt_xmltv(dt, tz_offset):
    return dt.strftime("%Y%m%d%H%M%S") + " " + tz_offset

def main():
    config = json.loads(Path(CONFIG_FILE).read_text(encoding="utf-8"))
    settings = config["settings"]
    channels = config["channels"]

    days = int(settings.get("days", 7))
    tz_offset = settings.get("timezone_offset", "-0400")
    logo = settings.get("logo", "")
    group_title = settings.get("group_title", "")
    output_xml = settings.get("output_xml", "appletv_series_epg.xml")
    output_m3u = settings.get("output_m3u", "appletv_series.m3u")

    start_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="Apple-247 JSON EPG">']

    for ch in channels:
        xml.append(f'  <channel id="{escape(ch["id"])}">')
        xml.append(f'    <display-name>{escape(ch["name"])}</display-name>')
        if logo:
            xml.append(f'    <icon src="{escape(logo)}" />')
        xml.append('  </channel>')

    for hour in range(days * 24):
        start = start_day + timedelta(hours=hour)
        stop = start + timedelta(hours=1)
        for ch in channels:
            xml.append(f'  <programme start="{fmt_xmltv(start, tz_offset)}" stop="{fmt_xmltv(stop, tz_offset)}" channel="{escape(ch["id"])}">')
            xml.append(f'    <title>{escape(ch["show"])}</title>')
            if ch.get("subtitle"):
                xml.append(f'    <sub-title>{escape(ch["subtitle"])}</sub-title>')
            xml.append('    <desc>24/7 channel</desc>')
            xml.append('  </programme>')

    xml.append('</tv>')
    Path(output_xml).write_text("\n".join(xml), encoding="utf-8")

    m3u = ["#EXTM3U"]
    for ch in channels:
        m3u.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{logo}" group-title="{group_title}",{ch["name"]}')
        m3u.append(ch["stream_url"])

    Path(output_m3u).write_text("\n".join(m3u) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
