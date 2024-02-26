import argparse
# Google APIとの通信に使用するモジュールをインポート
from googleapiclient.discovery import build
# ファイルのアップロードをサポートするクラスをインポート
from googleapiclient.http import MediaFileUpload
# OAuth2認証のフローを管理するクラスをインポート
from google_auth_oauthlib.flow import InstalledAppFlow

# YouTube APIのサービス名とバージョンを定義
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
# 認証時に要求する権限のスコープを定義
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
# クライアントの秘密情報が含まれるJSONファイルへのパスを定義
CLIENT_SECRETS_FILE = r"client_secret.json"

# 認証関数を定義
def authenticate():
    # OAuth2認証のフローを管理
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    # ローカルサーバーを使用して認証情報を取得
    credentials = flow.run_local_server(port=0)
    # 認証情報を使用してAPIサービスを構築
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

# ビデオアップロード関数を定義
def upload_video(youtube, file_path, title, description, category, privacyStatus):
    # アップロードリクエストを作成
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category
            },
            "status": {
                "privacyStatus": privacyStatus,
                "selfDeclaredMadeForKids": False,  # 子供向け動画か？
                "madeForKids": False,  # 大人向けに設定
            }
        },
        # メディアファイルとしてアップロード
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if 'id' in response:
            print(f"Video id '{response['id']}' was successfully uploaded.")
        else:
            print("The upload failed with an unexpected response:", response)

# メイン部分
if __name__ == "__main__":
    # コマンドライン引数のパーサを作成
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="アップロードするビデオのファイルパス")
    parser.add_argument("--title", help="ビデオのタイトル", default="Default Title")
    parser.add_argument("--description", help="ビデオの説明", default="Default Description")
    parser.add_argument("--category", help="ビデオのカテゴリ", type=int, default=22)
    parser.add_argument("--privacyStatus", help="ビデオのプライバシーステータス（public, unlisted, private）", default="unlisted")
  
    # 引数を解析
    args = parser.parse_args()

    # YouTube APIサービスを認証
    youtube = authenticate()

    # ビデオをアップロード
    upload_video(youtube, args.file_path, args.title, args.description, args.category, args.privacyStatus)
