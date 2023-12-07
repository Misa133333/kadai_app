from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
import os
import random

# Azureの設定を環境変数から読み込む
key = os.environ["COMPUTER_VISION_SUBSCRIPTION_KEY"]
endpoint = os.environ["COMPUTER_VISION_ENDPOINT"]

# Azureのコンピュータービジョンクライアントを初期化
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

app = Flask(__name__)

# 画像を保存するディレクトリへのパス
app.config['UPLOAD_FOLDER'] = r"C:\Users\nagata\Desktop\kadai_app_creation\static\uploads"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ファイルがフォームに存在するか確認
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        # ファイル名が空でないか確認
        if file.filename == '':
            return 'No selected file'
        if file:
            # ファイル名を安全な形式に変換し、ファイルパスを生成
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # ファイルを指定されたパスに保存
            file.save(file_path)
            # 保存したファイルを開き、Azure Computer Vision APIに送信
            with open(file_path, 'rb') as image_stream:
                analysis = computervision_client.analyze_image_in_stream(image_stream, visual_features=[VisualFeatureTypes.tags])
            #生成されたタグに基づいてストーリーを生成
            story = generate_complex_story(analysis.tags)
            image_url = url_for('static', filename=f'uploads/{filename}')
            # 解析結果をテンプレートに渡してレンダリング
            return render_template('result.html', story=story, image_url=image_url)
                    
    return render_template('index.html')

# 物語生成関数
def generate_complex_story(tags):
    # タグをカテゴリーに分類
    nature_tags = ['plant', 'flower', 'tree']
    object_tags = ['car', 'house', 'street']

    # ストーリー要素のオプション
    nature_stories = [
                "秋の田の かりほの庵の 苫をあらみ",
                "春過ぎて 夏来にけらし 白妙の",
                "あしびきの 山鳥の尾の しだり尾の",
                "田子の浦に うち出でてみれば 白妙の",
                "奥山に 紅葉踏み分け 鳴く鹿の",
                "かささぎの 渡せる橋に おく霜の",
                "天の原 ふりさけ見れば 春日なる",
                "わが庵は 都のたつみ しかぞ住む",
                "花の色は うつりにけりな いたづらに",
                "これやこの 行くも帰るも 別れては",
                "ちはやぶる 神代もきかず 竜田川",
                "すみの江の 岸による波 よるさえや",
                "久方の 光のどけき 春の日に",
                "誰をかも 知る人にせむ 高砂の",
                "人はいさ 心も知らず ふるさとは",
                "夏の夜は まだ宵ながら 明けぬるを",
                "白露に 風の吹きしく 秋の野は",
                "忘らるる 身をば思はず 誓ひてし",
                "あさぼらけ 有明の月と 見るまでに",
                "山里は 冬ぞ寂しさ まさりける"

    ]
    object_stories = [
                "みかきもり 衛士のたく火の 夜は燃え",
                "君がため 惜しからざりし 命さえ",
                "かくとだに えやはいぶきの さしも草",
                "天つ風 雲のかよい路 吹きとぢよ",
                "つくばねの 峰より落つる みなの川",
                "みちのくの 忍ぶもぢずり 誰ゆゑに",
                "あはれとも いふべき人は 思ほえで",
                "八重むぐら しげれる宿の さびしきに",
                "我が庵は 都の東ぞ 住む人も",
                "由良のとを 渡る舟人 かぢを絶え",
                "ちはやぶる 神代も聞かず 竜田川",
                "すみの江の 岸による波 よるさへや",
                "心にも あらで憂き夜に 長らへば"

    ]

    # ストーリーの初期化
    story = ""

    # 自然に関するタグがある場合のストーリー
    if any(tag.name in nature_tags for tag in tags):
        story += random.choice(nature_stories) + " "+"は、どうでしょう？"

    # 物体に関するタグがある場合のストーリー
    if any(tag.name in object_tags for tag in tags):
        story += random.choice(object_stories) + " "+"は、どうでしょう？"

    # タグが特定のカテゴリーに当てはまらない場合
    if story == "":
        story = "思いがけない驚きと、語られることのない物語に満ちた世界です"

    return story

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)
