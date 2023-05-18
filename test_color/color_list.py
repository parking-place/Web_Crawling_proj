# 랜덤한 색상을 헥스코드로 생성
def rand_hex_color():
    import random
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())

# n을 입력받아 n길이의 랜덤하지만 겹치지않는 헥스코드 리스트를 반환
def rand_hex_list(n):
    hex_list = []
    for i in range(n):
        while True:
            hex_code = rand_hex_color()
            if hex_code not in hex_list:
                hex_list.append(hex_code)
                break
    return hex_list

# n을 입력받아 n길이의 랜덤하지만 겹치지않고 시각적으로 구분되는 헥스코드 리스트를 반환
def rand_hex_list(n):
    import random
    hex_list = []
    while len(hex_list) < n:
        # 16진수 코드 생성
        hex_code = '#' + ''.join(random.choices('0123456789ABCDEF', k=6))
        # 리스트에 있는 코드와 시각적인 차이가 있는지 확인
        distinct = True
        for color in hex_list:
            # RGB 공간에서 유클리드 거리로 색상 차이 계산
            diff = sum([(int(hex_code[i:i+2], 16) - int(color[i:i+2], 16))**2 for i in (1, 3, 5)])
            if diff < 500:
                distinct = False
                break
        if distinct:
            hex_list.append(hex_code)
    return hex_list

# n을 입력받아, n길이의 일정한 간격의 색상을 가진 헥스코드 리스트를 반환
def rand_hex_list_hsv(n, s = 0.5, v = 1.0):
    import colorsys
    # 색상을 저장할 리스트 초기화
    colors = []
    
    if s < 0 or s > 1: s = 0.5
    if v < 0 or v > 1: v = 1.0
    
    # HSV 색상 공간에서 색상(H) 값의 간격 계산
    interval = 1.0 / (n)
    
    # HSV 색상 공간에서 색상(H) 값의 리스트 생성
    for i in range(n):
        # HSV 색상 공간에서 색상(H) 값 계산
        h = i * interval
        
        # HSV 색상 공간에서 RGB 색상 공간으로 변환
        hsv = (h, s, v)
        rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(*hsv))
        
        # RGB 색상을 16진수로 변환
        hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        # 리스트에 추가
        colors.append(hex_code)
        
    return colors