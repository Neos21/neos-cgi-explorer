#!/usr/bin/env node

const CONFIG_FILE_PATH = './nexp-config.json';

// ================================================================================

const fs   = require('fs');
const path = require('path');

process.on('uncaughtException', _error => responseError('Uncaught Exception'));

(async () => {
  if(process.env.REQUEST_METHOD !== 'POST') return responseError('Invalid Request Method');
  const postBody = await getPostBody();
  if(!postBody) return responseError('Failed To Parse Post Body');
  const config = await loadConfig();
  if(!config) return responseError('Failed To Load Config File');
  if(postBody.credential !== config.credential) return responseError('Invalid Credential');
  await exec(config, postBody);
})();

/** エラーメッセージをレスポンスする */
function responseError(errorMessage) {
  console.log('Content-Type: application/json; charset=UTF-8');  // このファイルのみ Content-Type を変更するためココに実装する
  console.log(`Status: 400\n\n${JSON.stringify({ error: errorMessage })}`);
}

/** POST リクエストを連想配列形式で取得する */
async function getPostBody() {
  try {
    let postBodyStr = '';
    for await(const chunk of process.stdin) postBodyStr += chunk;
    return [...new URLSearchParams(postBodyStr)].reduce((acc, pair) => ({...acc, [pair[0]]: pair[1]}), {});  // このファイルのみ `form` 要素から POST されたデータを受け取りたいため `JSON.parse()` を使用しない
  }
  catch(_error) { }
}

/** Config ファイルを読み込む */
async function loadConfig() {
  try {
    const text = await fs.promises.readFile(CONFIG_FILE_PATH, 'UTF-8');
    return JSON.parse(text);
  }
  catch(_error) { }
}

/** メイン処理 */
async function exec(config, postBody) {
  const filePath = postBody['file-path'];  // ルートディレクトリ直下を `./` 始まりで表現しファイルパスを指定する・スラッシュ始まりでは書かない
  if(!filePath) return responseError('Invalid Parameters');
  
  const targetFilePath = path.resolve(config.rootDirectoryPath, filePath);
  if(!targetFilePath.startsWith(config.rootDirectoryPath)) return responseError('Invalid Path');  // ルートディレクトリ配下になっていない場合は中断する
  
  // ファイル名から拡張子・拡張子から Content-Type を特定する
  const fileName = path.basename(targetFilePath) || 'file.unknown';
  const extension = path.extname(fileName).toLowerCase();
  const contentType = detectContentType(extension);
  
  try {
    // 余計な改行コードが入らないよう `process.stdout` を使って出力する
    const file = await fs.promises.readFile(targetFilePath);
    process.stdout.write(`Content-Type: ${contentType}\n`);
    process.stdout.write(`Content-Disposition: ${contentType === 'application/octet-stream' ? 'attachment' : 'inline'}; filename=${fileName}\n\n`);
    process.stdout.write(file);
  }
  catch(_error) {
    responseError('Failed To Open');
  }
}

/** 拡張子による Content-Type 判定 */
function detectContentType(extension) {
  // テキスト系はいずれもプレーンテキスト扱いにし、その場で表示できるようにする
  const typeText = [
    '.txt' , '.text', '.md'  , '.markdown',
    '.html', '.htm' , '.xml' , '.xhtml'   , '.xhtm',
    '.js'  , '.mjs' , '.jsx' , '.ts'      , '.tsx' , '.vue',
    '.css' , '.sass', '.scss',
    '.json', '.csv' , '.tsv' ,
    '.sh'  , '.bash', '.pl'  , '.py'      , '.rb'  , '.cgi', '.php'
  ];
  if(typeText.includes(extension)) return 'text/plain; charset=UTF-8';
  
  // 画像などはその場で表示できるようにする
  switch(extension) {
    case '.png' : return 'image/png';
    case '.gif' : return 'image/gif';
    case '.jpg' :
    case '.jpeg': return 'image/jpeg';
    case '.svg' : return 'image/svg+xml';
    case '.webp': return 'image/webp';
    case '.ico' : return 'image/vnd.microsoft.icon';
    case '.bmp' : return 'image/bmp';
    case '.tif' :
    case '.tiff': return 'image/tiff';
    case '.pdf' : return 'application/pdf';
  }
  
  // それ以外の拡張子はファイルダウンロードにする
  return 'application/octet-stream';
}
