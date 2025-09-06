import os
import argparse
from PIL import Image

# コマンドライン引数を解析する
parser = argparse.ArgumentParser(description="Generate HTML image and video tags from files in specified directories.")
parser.add_argument('--name', type=str, default='', help='Filter files by name pattern')
parser.add_argument('--dir', type=str, help='Specific directory to search within img, defaults to all subdirectories')
args = parser.parse_args()

# ベースディレクトリの設定
base_dir = 'img'

# ユーザーがディレクトリを指定したかどうかをチェック
if args.dir:
    directories = [os.path.join(base_dir, args.dir)]
else:
    # サブディレクトリとベースディレクトリの両方を検索対象にする
    # ただし、重複を避けるために別々に処理する
    directories = [base_dir]  # ベースディレクトリを追加
    # サブディレクトリを追加
    sub_directories = [os.path.join(base_dir, d) for d in next(os.walk(base_dir))[1]]
    directories.extend(sub_directories)

# 画像ファイルを取得
img_files = []
processed_files = set()  # 重複を避けるために処理済みファイルを記録

for directory in directories:
    if directory == base_dir:
        # ベースディレクトリの場合は直下のファイルのみを処理
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp4', '.webp')):
                if args.name in file and file_path not in processed_files:  # 重複チェック
                    img_files.append(file_path)
                    processed_files.add(file_path)
    else:
        # サブディレクトリの場合は通常通り再帰的に処理
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.mp4', '.webp')):
                    file_path = os.path.join(root, file)
                    if args.name in file and file_path not in processed_files:  # 重複チェック
                        img_files.append(file_path)
                        processed_files.add(file_path)

# 画像ファイルをアルファベット順にソート
img_files = sorted(img_files)

# HTMLのimgタグを生成
img_tags = []
for img_path in img_files:
    relative_path = os.path.relpath(img_path, base_dir)
    if img_path.lower().endswith('.mp4'):
        # MP4ファイルの場合はvideoタグを使用
        img_tag = f'<video src="./img/{relative_path}" muted playsinline preload="metadata"></video>'
    else:
        # 画像ファイルの場合はimgタグを使用
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                img_tag = f'<img src="./img/{relative_path}" alt="" width="{width}" height="{height}" loading="lazy" />'
        except IOError:
            # PIL がwebpや特定のファイルを開けない場合のフォールバック
            img_tag = f'<img src="./img/{relative_path}" alt="" loading="lazy" />'
    img_tags.append(img_tag)

# 結果を出力
for tag in img_tags:
    print(tag)