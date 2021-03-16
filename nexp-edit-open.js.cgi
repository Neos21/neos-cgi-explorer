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
  const filePath = postBody.filePath;  // ルートディレクトリ直下を `./` 始まりで表現しファイルパスを指定する・スラッシュ始まりでは書かない
  if(!filePath) return responseError('Invalid Parameters');
  
  const targetFilePath = path.resolve(config.rootDirectoryPath, filePath);
  if(!targetFilePath.startsWith(config.rootDirectoryPath)) return responseError('Invalid Path');  // ルートディレクトリ配下になっていない場合は中断する
  
  try {
    const text = await fs.promises.readFile(targetFilePath, 'UTF-8');
    console.log(`\n${JSON.stringify({ result: 'OK', text: text })}`);
  }
  catch(_error) {
    responseError('Failed To Open Text File');
  }
}
