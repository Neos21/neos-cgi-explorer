#!/usr/bin/ruby

# Neo's Uploader


# Require
# ======================================================================

require 'cgi'
require 'fileutils'
require 'pathname'

# グローバル変数 : CGI オブジェクト
$cgi = CGI.new


# 定数
# ======================================================================

# アクセスパスワードを管理するクレデンシャルファイルへのフルパス
CREDENTIAL_FILE_PATH = '/PATH/TO/credential.txt'
# ルートディレクトリ : この配下にのみファイルをアップロードする
ROOT_DIRECTORY = '/PATH/TO/explorer-files'
# ファイルエクスプローラへのルート相対パス
FILE_EXPLORER_PATH = '/neos-explorer.js.cgi'


# 事前処理
# ======================================================================

# メイン
def main()
  # POST でない場合はエラーとする (Credential は無視する)
  if ENV['REQUEST_METHOD'] != 'POST'
    print_error('Invalid Request Method')
    return
  end
  
  # クレデンシャルが不正な場合
  unless is_valid_credential
    print_error('Invalid Credential')
    return
  end
  
  # パラメータを取得する
  credential   = $cgi.params['credential'][0].read
  preview_path = $cgi.params['preview-path'][0].read
  upload_file  = $cgi.params['file'][0]
  file_name    = upload_file.original_filename.split(/(\\|\/)/)[-1]
  
  # ファイルのフルパスを作る
  target_path = Pathname.new(ROOT_DIRECTORY).join(preview_path, file_name).cleanpath.to_s
  
  # ルートディレクトリ配下のパスになっていない場合はアップロードさせない
  unless target_path.start_with?(ROOT_DIRECTORY)
    print_error('Invalid Path')
    return
  end
  
  # ファイルをアップロード (書き込み) する
  File.open(target_path, 'w') do |file|
    file.binmode
    file.write(upload_file.read)
  end
  
  # Explorer の元いたページにリダイレクトする
  print_header
  print(<<"EOL")
    <form action="#{FILE_EXPLORER_PATH}" method="POST" id="redirect-form">
      <input type="hidden" name="credential"  value="#{credential}">
      <input type="hidden" name="mode"        value="cd">
      <input type="hidden" name="target-path" value="#{preview_path}">
    </form>
    <script>
      window.addEventListener('load', () => {
        document.getElementById('redirect-form').submit();
      });
    </script>
EOL
  print_footer
end

# パラメータのクレデンシャルが正しいかチェックする
def is_valid_credential()
  credential_param = $cgi.params['credential'][0].read
  credential = ''
  File.open(CREDENTIAL_FILE_PATH, 'r:UTF-8') { |credential_file|
    credential = credential_file.read.chomp
  }
  return credential_param == credential
end

# HTML のヘッダ部分を出力する
def print_header()
  print(<<"EOL")
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex,nofollow">
    <title>Uploader</title>
    <style>

@font-face { font-family: "Yu Gothic"; src: local("Yu Gothic Medium"), local("YuGothic-Medium"); }
@font-face { font-family: "Yu Gothic"; src: local("Yu Gothic Bold")  , local("YuGothic-Bold")  ; font-weight: bold; }
*, ::before, ::after { box-sizing: border-box; }

html {
  overflow-y: scroll;
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, YuGothic, "Yu Gothic", "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  text-decoration-skip-ink: none;
  -webkit-text-decoration-skip: objects;
  cursor: default;
}

body {
  margin: 1rem;
  line-height: 1.6;
  overflow-wrap: break-word;
}

a { color: #00f; }
a:hover, a:active, strong { color: #f00; }

    </style>
  </head>
  <body>
EOL
end

# HTML のフッタ部分を出力する
def print_footer()
  print(<<'EOL')
  </body>
</html>
EOL
end

# エラーメッセージを表示する
def print_error(message)
  print_header
  print(<<"EOL")
<h1>Uploader : Error</h1>
<p><strong>#{message}</strong></p>
EOL
  print_footer
end


# 実行
# ======================================================================

main
