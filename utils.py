def rsrp_color(rsrp):
    """根据 RSRP 值返回颜色 RGBA。

    绿色 (> -90 dBm) 表示信号强，
    红色 (< -110 dBm) 表示信号弱，
    中间值渐变黄色-橙色。
    """
    if rsrp > -90:
        return [0, 200, 0, 180]
    if rsrp < -110:
        return [200, 0, 0, 180]
    ratio = (rsrp + 110) / 20
    return [int(200 * (1 - ratio)), int(200 * ratio), 0, 180]


def rgba_to_hex(rgba):
    """将 RGBA 数组转换为十六进制颜色字符串供前端使用。"""
    return f"#{rgba[0]:02x}{rgba[1]:02x}{rgba[2]:02x}{rgba[3]:02x}"


# 上海市各区近似中心坐标（用于经纬度到行政区的粗略映射）
DISTRICT_CENTERS = [
    ((31.23, 121.48), "黄浦区"),
    ((31.23, 121.45), "静安区"),
    ((31.19, 121.44), "徐汇区"),
    ((31.22, 121.42), "长宁区"),
    ((31.25, 121.41), "普陀区"),
    ((31.26, 121.49), "虹口区"),
    ((31.27, 121.52), "杨浦区"),
    ((31.25, 121.54), "浦东新区"),
]


def approx_district(lat, lon):
    """通过最近邻中心点估算所属行政区（离线可用）。"""
    closest = min(
        DISTRICT_CENTERS,
        key=lambda c: (lat - c[0][0]) ** 2 + (lon - c[0][1]) ** 2,
    )
    return closest[1]
