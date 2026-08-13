from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # 【新增】用来发网络请求
import os        # 【新增】用来读取环境变量

app = Flask(__name__)
CORS(app)

# ==========================================
# 0. 读取 DeepSeek 的 API Key（从 Render 环境变量读取）
# ==========================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

gua = {
    1: "天", 2: "澤", 3: "火", 4: "雷", 
    5: "風", 6: "水", 7: "山", 8: "地"
}

chinese_num = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}

bagua_map = {
    # 第一行：下卦=天
    (1, 1): "乾為天卦", (2, 1): "澤天夬卦", (3, 1): "火天大有卦", (4, 1): "雷天大壯卦", 
    (5, 1): "風天小畜卦", (6, 1): "水天需卦", (7, 1): "山天大畜卦", (8, 1): "地天泰卦",
    
    # 第二行：下卦=泽
    (1, 2): "天澤履卦", (2, 2): "兌為澤卦", (3, 2): "火澤睽卦", (4, 2): "雷澤歸妹卦", 
    (5, 2): "風澤中孚卦", (6, 2): "水澤節卦", (7, 2): "山澤損卦", (8, 2): "地澤臨卦",

    # 第三行：下卦=火
    (1, 3): "天火同人卦", (2, 3): "澤火革卦", (3, 3): "離為火卦", (4, 3): "雷火豐卦", 
    (5, 3): "風火家人卦", (6, 3): "水火既濟卦", (7, 3): "山火賁卦", (8, 3): "地火明夷卦",

    # 第四行：下卦=雷
    (1, 4): "天雷無妄卦", (2, 4): "澤雷隨卦", (3, 4): "火雷噬嗑卦", (4, 4): "震為雷卦", 
    (5, 4): "風雷益卦", (6, 4): "水雷屯卦", (7, 4): "山雷頤卦", (8, 4): "地雷復卦",

    # 第五行：下卦=风
    (1, 5): "天風姤卦", (2, 5): "澤風大過卦", (3, 5): "火風鼎卦", (4, 5): "雷風恆卦", 
    (5, 5): "巽為風卦", (6, 5): "水風井卦", (7, 5): "山風蠱卦", (8, 5): "地風升卦",

    # 第六行：下卦=水
    (1, 6): "天水訟卦", (2, 6): "澤水困卦", (3, 6): "火水未濟卦", (4, 6): "雷水解卦", 
    (5, 6): "風水渙卦", (6, 6): "坎為水卦", (7, 6): "山水蒙卦", (8, 6): "地水師卦",

    # 第七行：下卦=山
    (1, 7): "天山遯卦", (2, 7): "澤山咸卦", (3, 7): "火山旅卦", (4, 7): "雷山小過卦", 
    (5, 7): "風山漸卦", (6, 7): "水山蹇卦", (7, 7): "艮為山卦", (8, 7): "地山謙卦",

    # 第八行：下卦=地
    (1, 8): "天地否卦", (2, 8): "澤地萃卦", (3, 8): "火地晉卦", (4, 8): "雷地豫卦", 
    (5, 8): "風地觀卦", (6, 8): "水地比卦", (7, 8): "山地剝卦", (8, 8): "坤為地卦",
}

# 注意看这个顺序：第1个数代表上爻，第2个数代表中爻，第3个数代表下爻
bian_gua = {
    "天": "111",  # 阳阳阳
    "澤": "110",  # 阳阳阴
    "火": "101",  # 阳阴阳
    "雷": "100",  # 阳阴阴
    "風": "011",  # 阴阳阳
    "水": "010",  # 阴阳阴
    "山": "001",  # 阴阴阳
    "地": "000"   # 阴阴阴
}

# ==========================================
# 2. 首页页面（有了这个，打开链接就不会 404 了）
# ==========================================
@app.route('/')
def home():
    return """
    <h1>易經數字占卜 API</h1>
    <p>請使用 POST 請求發送到 /divine 進行占卜。</p>
    <p>範例：</p>
    <pre>
    curl -X POST https://bagua-app-xzch.onrender.com/divine \\
      -H "Content-Type: application/json" \\
      -d '{"num1":7,"num2":8,"num3":3,"question":"測試"}'
    </pre>
    """

# ==========================================
# 3. 核心接口（包含 AI 解卦）
# ==========================================
@app.route('/divine', methods=['POST'])
def divine():
    try:
        data = request.get_json()
        num1 = int(data['num1'])
        num2 = int(data['num2'])
        num3 = int(data['num3'])
        question = data['question']
        # 【修正 1】嚴格的 mode 過濾
        mode = data.get('mode', 'base')
        if mode not in ['base', 'ai']:
            mode = 'base' 
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "輸入格式錯誤！請輸入純數字！"})

    if num1 < 1 or num1 > 8 or num2 < 1 or num2 > 8 or num3 < 1 or num3 > 8:
        return jsonify({"error": "請輸入1-8之間的數字！"})

    # --- 1. 起卦逻辑 ---
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

    # ==========================================
    # 2. 准备“原本的基础卦象内容”
    # ==========================================
    base_result = f"""
你是一名易經專家。我剛剛用數字法起了一個卦，問的是：{question}
我的三個數字分別是：{num1}，{num2}，{num3}。
得到的卦象是：上{shang_gua}，下{xia_gua}，{bagua_name}。
動爻為第{chinese_num[move_line]}爻。
變卦為：上{new_shang_gua}，下{new_xia_gua}，{new_bagua_name}。
"""

    # ==========================================
    # 3. 根据 mode 决定返回什么
    # ==========================================
    if mode == 'base':
        return jsonify({"result": base_result})

    elif mode == 'ai':
        ai_prompt = base_result + "\n請為我詳細解此卦的吉凶，並給出3條切實可行的行動建議。"
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": ai_prompt}]
            }
            ai_response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            if ai_response.status_code == 200:
                final_result = ai_response.json()["choices"][0]["message"]["content"]
                # 转换 Markdown 为 HTML
                final_result = final_result.replace("###", "<h3>").replace("**", "<b>").replace("\n", "<br>")
                return jsonify({"result": final_result})
            else:
                return jsonify({"error": "AI 解卦伺服器暫時擁擠，請稍後再按一次。"})
        except Exception:
            return jsonify({"error": "AI 連線失敗，請檢查網絡狀態。"})
# 4. 启动服务器（保持这样）
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
