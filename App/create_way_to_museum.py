def create_yandex_route_link(start_coords):
    end_coords = (48.321527, 40.268680)  # Координаты музея
    base_url = "https://yandex.ru/maps/"
    params = {
        'll': f"{(start_coords[1] + end_coords[1]) / 2}%2C{(start_coords[0] + end_coords[0]) / 2}",
        'mode': 'routes',
        'rtext': f"{start_coords[0]}%2C{start_coords[1]}~{end_coords[0]}%2C{end_coords[1]}",
        'rtt': 'auto',
        'z': '9.81'
    }

    url = f"{base_url}?ll={params['ll']}&mode={params['mode']}&rtext={params['rtext']}&rtt={params['rtt']}&z={params['z']}"

    return url

