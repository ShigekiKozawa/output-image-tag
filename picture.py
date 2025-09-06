import os
import argparse
from PIL import Image

# コマンドライン引数を解析する
parser = argparse.ArgumentParser(description="Generate HTML picture tags from files in specified directories.")
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
            if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                if args.name in file and file_path not in processed_files:  # 重複チェック
                    img_files.append(file_path)
                    processed_files.add(file_path)
    else:
        # サブディレクトリの場合は通常通り再帰的に処理
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                    file_path = os.path.join(root, file)
                    if args.name in file and file_path not in processed_files:  # 重複チェック
                        img_files.append(file_path)
                        processed_files.add(file_path)

# 画像ファイルをアルファベット順にソート
img_files = sorted(img_files)

# 同じファイル名を持つ画像をグループ化（ディレクトリは無視して純粋にファイル名でグループ化）
image_groups = {}
for img_path in img_files:
    # MP4ファイルは除外（pictureタグはビデオには対応していないため）
    if img_path.lower().endswith('.mp4'):
        continue
        
    # ファイル名を取得（パスなし）
    filename = os.path.basename(img_path)
    
    # 同じファイル名のグループに追加
    if filename not in image_groups:
        image_groups[filename] = []
    image_groups[filename].append(img_path)

# HTMLのpictureタグを生成
picture_tags = []
for filename, paths in image_groups.items():
    # 画像の情報を取得
    pc_path = None      # pcディレクトリの画像
    root_path = None    # imgディレクトリ直下の画像
    sp_path = None      # spディレクトリの画像
    other_path = None   # その他のディレクトリの画像
    
    for path in paths:
        relative_path = os.path.relpath(path, base_dir)
        parts = relative_path.split(os.sep)
        
        # pcディレクトリにある画像
        if len(parts) > 1 and parts[0] == "pc":
            pc_path = path
        # ルートディレクトリ（img直下）の画像
        elif len(parts) == 1:
            root_path = path
        # spディレクトリにある画像
        elif len(parts) > 1 and parts[0] == "sp":
            sp_path = path
        # その他のディレクトリの画像
        else:
            other_path = path
    
    # PC用の画像（min-width: 768px用）を選択
    pc_image_path = None
    # スマートフォン用の画像を選択
    sp_image_path = None
    
    # ケース1: pcディレクトリがある場合
    if pc_path:
        # PC用はpcディレクトリの画像
        pc_image_path = pc_path
        # SP用はルートディレクトリの画像（なければspディレクトリ）
        sp_image_path = root_path if root_path else sp_path
    # ケース2: pcディレクトリがない場合
    else:
        # PC用はルートディレクトリの画像
        pc_image_path = root_path
        # SP用はspディレクトリの画像（なければその他）
        sp_image_path = sp_path if sp_path else other_path
    
    # 両方の画像が存在する場合（PC用とSP用）
    if pc_image_path and sp_image_path:
        try:
            with Image.open(sp_image_path) as img:
                width, height = img.size
                pc_relative_path = os.path.relpath(pc_image_path, base_dir)
                sp_relative_path = os.path.relpath(sp_image_path, base_dir)
                picture_tag = f'<picture>\n  <source media="(min-width: 768px)" srcset="./img/{pc_relative_path}">\n  <source srcset="./img/{sp_relative_path}">\n  <img src="./img/{sp_relative_path}" alt="" width="{width}" height="{height}" loading="lazy" />\n</picture>'
        except IOError:
            pc_relative_path = os.path.relpath(pc_image_path, base_dir)
            sp_relative_path = os.path.relpath(sp_image_path, base_dir)
            picture_tag = f'<picture>\n  <source media="(min-width: 768px)" srcset="./img/{pc_relative_path}">\n  <source srcset="./img/{sp_relative_path}">\n  <img src="./img/{sp_relative_path}" alt="" loading="lazy" />\n</picture>'
    
    # PC用の画像のみがある場合
    elif pc_image_path:
        try:
            with Image.open(pc_image_path) as img:
                width, height = img.size
                relative_path = os.path.relpath(pc_image_path, base_dir)
                picture_tag = f'<picture>\n  <source srcset="./img/{relative_path}">\n  <img src="./img/{relative_path}" alt="" width="{width}" height="{height}" loading="lazy" />\n</picture>'
        except IOError:
            relative_path = os.path.relpath(pc_image_path, base_dir)
            picture_tag = f'<picture>\n  <source srcset="./img/{relative_path}">\n  <img src="./img/{relative_path}" alt="" loading="lazy" />\n</picture>'
    
    # SP用の画像のみがある場合
    elif sp_image_path:
        try:
            with Image.open(sp_image_path) as img:
                width, height = img.size
                relative_path = os.path.relpath(sp_image_path, base_dir)
                picture_tag = f'<picture>\n  <source srcset="./img/{relative_path}">\n  <img src="./img/{relative_path}" alt="" width="{width}" height="{height}" loading="lazy" />\n</picture>'
        except IOError:
            relative_path = os.path.relpath(sp_image_path, base_dir)
            picture_tag = f'<picture>\n  <source srcset="./img/{relative_path}">\n  <img src="./img/{relative_path}" alt="" loading="lazy" />\n</picture>'
    
    picture_tags.append(picture_tag)

# 結果を出力
for tag in picture_tags:
    print(tag)
