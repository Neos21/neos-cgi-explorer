#!/usr/bin/env node

const CONFIG_FILE_PATH = './nexp-config.json';

// ================================================================================

const fs   = require('fs');
const path = require('path');

process.on('uncaughtException', _error => responseError('Uncaught Exception'));

(async () => {
  console.log('Content-Type: application/json; charset=UTF-8');
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
  console.log(`Status: 400\n\n${JSON.stringify({ error: errorMessage })}`);
}

/** POST リクエストを JSON 形式で取得する */
async function getPostBody() {
  try {
    let postBodyStr = '';
    for await(const chunk of process.stdin) postBodyStr += chunk;
    return JSON.parse(postBodyStr);
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
  const directoryPath = postBody.directoryPath;  // ルートディレクトリ直下を `./` 始まりで表現しファイルパスを指定する・スラッシュ始まりでは書かない・末尾はスラッシュなしが良いが、あっても良い
  if(!directoryPath) return responseError('Invalid Parameters');
  
  const targetDirectoryPath = path.resolve(config.rootDirectoryPath, directoryPath);
  if(!targetDirectoryPath.startsWith(config.rootDirectoryPath)) return responseError('Invalid Path');  // ルートディレクトリ配下になっていない場合は中断する
  
  // ファイル一覧を取得する
  let dirents = null;
  try {
    dirents = await fs.promises.readdir(targetDirectoryPath, { withFileTypes: true });
  }
  catch(_error) {
    return responseError('Failed To Ls');
  }
  
  const cwd = targetDirectoryPath.replace(config.rootDirectoryPath, '.');
  const files = dirents
    .map(dirent => ({
      name: dirent.name,
      isDirectory: dirent.isDirectory(),
      isEditable: (!dirent.isDirectory() && isEditable(dirent.name))
    }))
    .sort((a, b) => {
      if(a.isDirectory < b.isDirectory) return  1;
      if(a.isDirectory > b.isDirectory) return -1;
      return 0;
    });
  console.log(`\n${JSON.stringify({ result: 'OK', cwd: cwd, files: files })}`);
}

/** 編集可能なファイルかどうかを判定する */
function isEditable(fileName) {
  // `open` でテキストとして表示する拡張子を「編集可能なファイル形式」とする
  const editableTypes = [
    '.txt' , '.text', '.md'  , '.markdown',
    '.html', '.htm' , '.xml' , '.xhtml'   , '.xhtm',
    '.js'  , '.mjs' , '.jsx' , '.ts'      , '.tsx' , '.vue',
    '.css' , '.sass', '.scss',
    '.json', '.csv' , '.tsv' ,
    '.sh'  , '.bash', '.pl'  , '.py'      , '.rb'  , '.cgi', '.php'
  ];
  const extension = path.extname(fileName).toLowerCase();
  return editableTypes.includes(extension);
}
