from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# 1. 基础字典
# ==========================================
gua = {
    1: "天", 2: "澤", 3: "火", 4: "雷", 
    5: "風", 6: "水", 7: "山", 8: "地"
}

chinese_num = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}

bagua_map = {
    (1, 1): "1.乾為天卦", (2, 1): "43.澤天夬卦", (3, 1): "14.火天大有卦", (4, 1): "34.雷天大壯卦", 
    (5, 1): "9.風天小畜卦", (6, 1): "5.水天需卦", (7, 1): "26.山天大畜卦", (8, 1): "11.地天泰卦",
    (1, 2): "10.天澤履卦", (2, 2): "58.兌為澤卦", (3, 2): "38.火澤睽卦", (4, 2): "54.雷澤歸妹卦", 
    (5, 2): "61.風澤中孚卦", (6, 2): "60.水澤節卦", (7, 2): "41.山澤損卦", (8, 2): "19.地澤臨卦",
    (1, 3): "13.天火同人卦", (2, 3): "49.澤火革卦", (3, 3): "30.離為火卦", (4, 3): "55.雷火豐卦", 
    (5, 3): "37.風火家人卦", (6, 3): "63.水火既濟卦", (7, 3): "22.山火賁卦", (8, 3): "36.地火明夷卦",
    (1, 4): "25.天雷無妄卦", (2, 4): "17.澤雷隨卦", (3, 4): "21.火雷噬嗑卦", (4, 4): "51.震為雷卦", 
    (5, 4): "42.風雷益卦", (6, 4): "3.水雷屯卦", (7, 4): "27.山雷頤卦", (8, 4): "24.地雷復卦",
    (1, 5): "44.天風姤卦", (2, 5): "28.澤風大過卦", (3, 5): "50.火風鼎卦", (4, 5): "32.雷風恆卦", 
    (5, 5): "57.巽為風卦", (6, 5): "48.水風井卦", (7, 5): "18.山風蠱卦", (8, 5): "46.地風升卦",
    (1, 6): "6.天水訟卦", (2, 6): "47.澤水困卦", (3, 6): "64.火水未濟卦", (4, 6): "40.雷水解卦", 
    (5, 6): "59.風水渙卦", (6, 6): "29.坎為水卦", (7, 6): "4.山水蒙卦", (8, 6): "7.地水師卦",
    (1, 7): "33.天山遯卦", (2, 7): "31.澤山咸卦", (3, 7): "56.火山旅卦", (4, 7): "62.雷山小過卦", 
    (5, 7): "53.風山漸卦", (6, 7): "39.水山蹇卦", (7, 7): "52.艮為山卦", (8, 7): "15.地山謙卦",
    (1, 8): "12.天地否卦", (2, 8): "45.澤地萃卦", (3, 8): "35.火地晉卦", (4, 8): "16.雷地豫卦", 
    (5, 8): "20.風地觀卦", (6, 8): "8.水地比卦", (7, 8): "23.山地剝卦", (8, 8): "2.坤為地卦",
}

bian_gua = {
    "天": "111", "澤": "011", "火": "101", "雷": "100",
    "風": "110", "水": "010", "山": "001", "地": "000"
}

# ==========================================
# 2. 关键接口！这个 @app.route 必须顶格写！
# ==========================================
@app.route('/divine', methods=['POST'])
def divine():
    try:
        data = request.get_json()
        num1 = int(data['num1'])
        num2 = int(data['num2'])
        num3 = int(data['num3'])
        question = data['question']
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "輸入格式錯誤！請輸入純數字！"})

    if num1 < 1 or num1 > 8 or num2 < 1 or num2 > 8 or num3 < 1 or num3 > 8:
        return jsonify({"error": "請輸入1-8之間的數字！"})

    yushu = (num1 + num2 + num3) % 6
    move_line = 6 if yushu == 0 else yushu

    shang_gua = gua[num1]
    xia_gua = gua[num2]
    bagua_name = bagua_map[(num1, num2)]

    current_shang = bian_gua[shang_gua]
    current_xia = bian_gua[xia_gua]

    if move_line == 4: target_char = current_shang[0]
    elif move_line == 5: target_char = current_shang[1]
    elif move_line == 6: target_char = current_shang[2]
    elif move_line == 1: target_char = current_xia[0]
    elif move_line == 2: target_char = current_xia[1]
    elif move_line == 3: target_char = current_xia[2]

    new_char = '0' if target_char == '1' else '1'

    if move_line == 4:
        new_shang, new_xia = new_char + current_shang[1:], current_xia
    elif move_line == 5:
        new_shang, new_xia = current_shang[0] + new_char + current_shang[2:], current_xia
    elif move_line == 6:
        new_shang, new_xia = current_shang[:2] + new_char, current_xia
    elif move_line == 1:
        new_shang, new_xia = current_shang, new_char + current_xia[1:]
    elif move_line == 2:
        new_shang, new_xia = current_shang, current_xia[0] + new_char + current_xia[2:]
    elif move_line == 3:
        new_shang, new_xia = current_shang, current_xia[:2] + new_char

    reverse_bian_gua = {v: k for k, v in bian_gua.items()}
    reverse_gua = {v: k for k, v in gua.items()}
    new_shang_gua = reverse_bian_gua[new_shang]
    new_xia_gua = reverse_bian_gua[new_xia]

    if (new_shang_gua, new_xia_gua) in bagua_map:
        new_bagua_name = bagua_map[(new_shang_gua, new_xia_gua)]
    else:
        new_num1 = reverse_gua[new_shang_gua]
        new_num2 = reverse_gua[new_xia_gua]
        new_bagua_name = bagua_map[(new_num1, new_num2)]

    result_text = f"""
易經占卜：我剛剛用數字法起了一個卦，問的是：{question}
我的三個數字分別是：{num1}，{num2}，{num3}。
得到的卦象是：上{shang_gua}，下{xia_gua}，{bagua_name}。
變卦為：上{new_shang_gua}，下{new_xia_gua}，{new_bagua_name}。
動爻為第{chinese_num[move_line]}爻。
請為我詳細解卦，並列出行動建議。
感謝使用數字占卜法，若有需要，請重新執行程式
"""
    return jsonify({"result": result_text})

# ==========================================
# 3. 启动命令
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
