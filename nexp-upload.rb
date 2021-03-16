#!/usr/bin/ruby

CONFIG_FILE_PATH = './nexp-config.json'

# ================================================================================

require 'cgi'
require 'fileutils'
require 'json'
require 'pathname'

def main()
  begin
    puts 'Content-Type: application/json; charset=UTF-8'
    return response_error('Invalid Request Method') if ENV['REQUEST_METHOD'] != 'POST'
    config = load_config
    cgi = CGI.new  # `curl` で叩く場合 `-d ''` がないと `Integer': can't convert nil into Integer (TypeError)` エラーになる
    return response_error('Invalid Credential') unless cgi.params['credential'][0].read === config['credential']
    exec(config, cgi)
  rescue => error
    response_error('Uncaught Exception')
  end
end

# エラーメッセージをレスポンスする
def response_error(error_message)
  print "Status: 400\n\n", JSON.generate({ 'error' => error_message })
end

# Config ファイルを読み込む
def load_config()
  config = ''
  File.open(CONFIG_FILE_PATH, 'r:UTF-8') do |file|
    config = JSON.load(file)
  end
  return config
end

# メイン処理
def exec(config, cgi)
  directory_path = cgi.params['directory-path'][0].read
  file           = cgi.params['file'][0]
  file_name      = file.original_filename.split(/(\\|\/)/)[-1]
  return response_error('Invalid Parameters') if directory_path.empty? || file.nil? || file_name.empty?  # FIXME : Null チェックがイマイチ
  
  # ファイルのフルパスを作る
  target_file_path = Pathname.new(config['rootDirectoryPath']).join(directory_path, file_name).cleanpath.to_s
  # ルートディレクトリ配下のパスになっていない場合は中断する
  return response_error('Invalid Path') unless target_file_path.start_with?(config['rootDirectoryPath'])
  
  # ファイルをアップロード (書き込み) する
  File.open(target_file_path, 'w') do |upload_file|
    upload_file.binmode
    upload_file.write(file.read)
  end
  
  print "\n", JSON.generate({ 'result' => 'OK' })
end

main
