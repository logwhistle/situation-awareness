_base32 = '0123456789bcdefghjkmnpqrstuvwxyz'

_decode_map = {}
_encode_map = {}
for i in range(len(_base32)):
    _decode_map[_base32[i]] = i
    _encode_map[i] = _base32[i]


def encode(lat, lon, precision):
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    geohash = []
    code = []
    j = 0
    while len(geohash) < precision:
        # print(code,lat_range,lon_range,geohash)
        j += 1
        lat_mid = sum(lat_range) / 2
        lon_mid = sum(lon_range) / 2
        # 经度
        if lon <= lon_mid:
            code.append(0)
            lon_range[1] = lon_mid
        else:
            code.append(1)
            lon_range[0] = lon_mid
        # 纬度
        if lat <= lat_mid:
            code.append(0)
            lat_range[1] = lat_mid
        else:
            code.append(1)
            lat_range[0] = lat_mid
        ##encode
        if len(code) >= 5:
            geohash.append(_encode_map[int(''.join(map(str, code[:5])), 2)])
            code = code[5:]
    return ''.join(geohash)


def decode(geohash):
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    is_lon = True
    for letter in geohash:
        code = str(bin(_decode_map[letter]))[2:].rjust(5, '0')
        for bi in code:
            if is_lon and bi == '0':
                lon_range[1] = sum(lon_range) / 2
            elif is_lon and bi == '1':
                lon_range[0] = sum(lon_range) / 2
            elif (not is_lon) and bi == '0':
                lat_range[1] = sum(lat_range) / 2
            elif (not is_lon) and bi == '1':
                lat_range[0] = sum(lat_range) / 2
            is_lon = not is_lon
    return sum(lat_range) / 2, sum(lon_range) / 2


def neighbors(geohash):
    neighbors = []
    lat_range, lon_range = 180, 360
    x, y = decode(geohash)
    num = len(geohash) * 5
    dx = lat_range / (2 ** (num // 2))
    dy = lon_range / (2 ** (num - num // 2))
    for i in range(1, -2, -1):
        for j in range(-1, 2):
            neighbors.append(encode(x + i * dx, y + j * dy, num // 5))
    # 是否保留自身
    # neighbors.remove(geohash)
    return neighbors


# 区域范围
def bbox(geohash):
    lat_range, lon_range = [-90.0, 90.0], [-180.0, 180.0]
    is_lon = True
    for letter in geohash:
        code = str(bin(_decode_map[letter]))[2:].rjust(5, '0')
        for bi in code:
            if is_lon and bi == '0':
                lon_range[1] = sum(lon_range) / 2
            elif is_lon and bi == '1':
                lon_range[0] = sum(lon_range) / 2
            elif (not is_lon) and bi == '0':
                lat_range[1] = sum(lat_range) / 2
            elif (not is_lon) and bi == '1':
                lat_range[0] = sum(lat_range) / 2
            is_lon = not is_lon
    # 左上、右下；(lat_max,lon_min),(lat_min,lon_max)
    return [(lat_range[1], lon_range[0]), (lat_range[0], lon_range[1])]
