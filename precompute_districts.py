"""One-time script: pre-compute Shanghai district names via Nominatim reverse geocoding.

Run this once to generate data/districts_cache.csv (takes ~8 minutes for 500 points).
After that, the dashboard loads district data from cache instantly.
"""
import sys
import pandas as pd
import time
from geopy.geocoders import Nominatim

sys.stdout.reconfigure(line_buffering=True)


def extract_district(address, display_name):
    city = address.get("city", "")
    if city and city != "上海市" and (city.endswith("区") or city.endswith("新区")):
        return city

    parts = [p.strip() for p in display_name.split(",")]
    for i, p in enumerate(parts):
        if p == "上海市":
            for j in range(i + 1, min(i + 3, len(parts))):
                if parts[j].endswith("新区"):
                    return parts[j]
                if parts[j].endswith("区") and parts[j] != "上海警备区":
                    return parts[j]

    for p in parts:
        if p.endswith("新区"):
            return p
    for p in parts:
        if p.endswith("区") and p != "上海警备区":
            return p
    return "未知"


def main():
    df = pd.read_csv("data/signal_samples.csv")
    geolocator = Nominatim(user_agent="5G_Signal_Dashboard/1.0")

    districts = []
    start = time.time()

    for i, (_, row) in enumerate(df.iterrows()):
        try:
            loc = geolocator.reverse(
                f"{row['Latitude']}, {row['Longitude']}",
                language="zh",
                timeout=10,
            )
            addr = loc.raw.get("address", {})
            display = loc.raw.get("display_name", "")
            district = extract_district(addr, display)
            districts.append(district)
        except Exception as e:
            district = "未知"
            districts.append(district)
            print(f"[{i}] Error: {e}", flush=True)

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start
            eta = (elapsed / (i + 1)) * (len(df) - i - 1)
            # 每 10 条增量保存一次，防止意外中断
            pd.DataFrame({"District": districts}).to_csv(
                "data/districts_cache.csv", index=False
            )
            print(
                f"[{i+1}/{len(df)}] {district} | 已用 {elapsed:.0f}s 预计剩余 {eta:.0f}s",
                flush=True,
            )

        time.sleep(1)

    pd.DataFrame({"District": districts}).to_csv("data/districts_cache.csv", index=False)
    print(
        f"\n完成! 已保存 {len(districts)} 条记录 | 总耗时 {time.time()-start:.0f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
