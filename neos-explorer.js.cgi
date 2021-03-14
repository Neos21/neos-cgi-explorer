#!/usr/bin/env node

/*! Neo's Explorer */


// Require・例外ハンドリング定義
// ====================================================================================================

const fs   = require('fs');
const path = require('path');

process.on('uncaughtException', (error) => {
  console.log('Content-Type: text/html; charset=UTF-8\n\n');
  console.log('<pre style="color: #00f; font-weight: bold;">Uncaught Exception :<br>', error, '</pre>');
});


// 定数
// ====================================================================================================

/** パスワードファイル : サーバ内のフルパスで指定・`input[type="password"]` に入力できる文字列であること */
const credential = (() => fs.readFileSync('/PATH/TO/credential.txt', 'utf-8').trim())();
/** ルートディレクトリ : サーバ内のフルパスで指定・`path.resolve()` を使い末尾のスラッシュを除去しておく */
const rootDirectory = path.resolve('/PATH/TO/explorer-files');
/** ファイルアップローダへのルート相対パス */
const fileUploaderPath = '/neos-uploader.rb';


// 共通関数
// ====================================================================================================

/** HTML ヘッダ */
function writeHtmlHeader(title) {
  console.log(`Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex,nofollow">
    <title>${title}</title>
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

[type="button"], [type="text"], [type="password"] {
  margin: 0;
  border: 1px solid #999;
  border-radius: 2px;
  padding: .25em .5em;
  color: inherit;
  font-family: inherit;
  font-size: inherit;
}

[type="button"] {
  padding-right: 1em;
  padding-left : 1em;
  background: #eee;
  cursor: pointer;
}

[type="button"]:hover, [type="button"]:focus {
  background: #e0e0e0;
}

[type="file"] {
  cursor: pointer;
}

    </style>
  </head>
  <body>`);
}

/** HTML フッタ */
function writeHtmlFooter() {
  console.log('  </body>\n</html>');
}

/** エラーメッセージのみのページを出力する */
function showErrorPage(errorMessage) {
  writeHtmlHeader('Error');
  console.log(`<p><strong>${errorMessage}</strong></p>`);
  writeHtmlFooter();
}


// ログインページ
// ====================================================================================================

/** ログインページ */
function showLoginPage(errorMessage) {
  writeHtmlHeader('Login');
  
  console.log(`
    <form action="${process.env.SCRIPT_NAME}" method="POST" id="login-form">
      <input type="hidden"   name="mode"                       value="login">
      <input type="password" name="credential" id="credential" value="">
      <input type="button"   name="submit-btn" id="submit-btn" value="Login">
    </form>
  `);
  if(errorMessage) console.log(`<p><strong>${errorMessage}</strong></p>`);
  
  console.log(`
    <script>
      document.addEventListener('DOMContentLoaded', () => {
        // Login ボタン押下時 : Local Storage に値を設定してから Submit する
        document.getElementById('submit-btn').addEventListener('click', (event) => {
          localStorage.setItem('credential', document.getElementById('credential').value);
          document.getElementById('login-form').submit();
        });
        
        // 初期表示時の処理
  `);
  if(!errorMessage) {
    // エラーがない場合、Local Storage に値があればその値でログインを試みる
    console.log(`
      const savedCredential = localStorage.getItem('credential');
      if(savedCredential) {
        document.getElementById('credential').value = savedCredential;
        document.getElementById('login-form').submit();
      }
    `);
  }
  else {
    // エラー時は Local Storage の値を削除しておく
    console.log(`localStorage.removeItem('credential');`);
  }
  console.log('});\n</script>');
  
  writeHtmlFooter();
}


// ファイルリストページ
// ====================================================================================================

/** ファイルリストページ */
async function listFiles(inputPath) {
  const fullPath = path.resolve(rootDirectory, inputPath);
  if(!fullPath.startsWith(rootDirectory)) return showErrorPage('Invalid Path');
  
  // ファイル一覧を取得する
  let dirents;
  try {
    dirents = await fs.promises.readdir(fullPath, { withFileTypes: true });
  }
  catch(error) {
    return showErrorPage('Failed To Open The Directory');
  }
  
  // 画面表示用のパス
  const previewPath = '.' + fullPath.replace(rootDirectory, '') + '/';
  
  writeHtmlHeader('Index Of');
  console.log(`<h1>Index Of : ${previewPath}</h1><ul>`);
  if(previewPath !== './') console.log(`<li><a href="javascript:void(0);" onclick="exec('cd', '..');">../</a></li>`);
  if(!dirents.length) {
    console.log('<li>(No Files)</li>');
  }
  else {
    dirents.filter(dirent => dirent.isDirectory()).sort().forEach(dirent => {
      console.log(`<li><a href="javascript:void(0);" onclick="exec('cd', '${dirent.name}');">${dirent.name}/</a></li>`);
    });
    dirents.filter(dirent => !dirent.isDirectory()).sort().forEach(dirent => {
      console.log(`<li><a href="javascript:void(0);" onclick="exec('openFile', '${dirent.name}');">${dirent.name}</a></li>`);
    });
  }
  console.log('</ul>');
  
  // ファイルアップロード欄・ページ移動用の隠しフォーム
  console.log(`
    <hr>
    <form action="${fileUploaderPath}" method="POST" enctype="multipart/form-data" id="upload-form">
      <input type="hidden" name="credential"   id="upload-credential"   value="">
      <input type="hidden" name="preview-path" id="upload-preview-path" value="">
      <input type="file"   name="file"         id="upload-file">
      <input type="button" name="submit-btn"   id="upload-submit-btn"   value="Upload" onclick="upload()">
    </form>
    <script>
      function upload() {
        const files = document.getElementById('upload-file').files;
        if(!files || !files.length) return alert('No Files');
        document.getElementById('upload-credential'  ).value = localStorage.getItem('credential');
        document.getElementById('upload-preview-path').value = '${previewPath}';
        document.getElementById('upload-form').submit();
      }
    </script>
    
    <form action="${process.env.SCRIPT_NAME}" method="POST" id="exec-form">
      <input type="hidden" name="credential"  id="exec-credential"  value="">
      <input type="hidden" name="mode"        id="exec-mode"        value="">
      <input type="hidden" name="target-path" id="exec-target-path" value="">
    </form>
    <script>
      // ディレクトリ遷移 or ファイルオープン
      function exec(mode, targetPath) {
        document.getElementById('exec-credential' ).value = localStorage.getItem('credential');
        document.getElementById('exec-mode'       ).value = mode;
        document.getElementById('exec-target-path').value = '${previewPath}' + targetPath;
        document.getElementById('exec-form').submit();
      }
    </script>
  `);
  
  writeHtmlFooter();
}


// ファイルオープン
// ====================================================================================================

/** ファイルオープン : プレビュー表示する */
async function openFile(inputPath) {
  const fullPath = path.resolve(rootDirectory, inputPath);
  if(!fullPath.startsWith(rootDirectory)) return showErrorPage('Invalid File Path');
  
  // ファイル名から拡張子・拡張子から Content-Type を特定する
  const fileName = path.basename(fullPath) || 'file.unknown';
  const extension = path.extname(fileName).toLowerCase();
  const contentType = detectContentType(extension);
  
  try {
    // 余計な改行コードが入らないよう `process.stdout` を使って出力する
    const file = await fs.promises.readFile(fullPath);
    process.stdout.write(`Content-Type: ${contentType}\n`);
    process.stdout.write(`Content-Disposition: ${contentType === 'application/octet-stream' ? 'attachment' : 'inline'}; filename=${fileName}\n\n`);
    process.stdout.write(file);
  }
  catch(error) {
    return showErrorPage('Failed To Open File');
  }
}

/** 拡張子による Content-Type 判定 */
function detectContentType(extension) {
  // テキスト系はその場で表示できるようにする
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


// メイン
// ====================================================================================================

(async () => {
  try {
    if(process.env.REQUEST_METHOD === 'POST') {
      let rawPostBody = '';
      for await(const chunk of process.stdin) { rawPostBody += chunk; }
      const postBody = [...new URLSearchParams(rawPostBody)].reduce((acc, pair) => ({...acc, [pair[0]]: pair[1]}), {});
      
      if(postBody.credential !== credential) return showLoginPage('Invalid Credential');
      
      // モード別に処理する
      if(postBody.mode === 'login')    return await listFiles('./');  // ログイン直後
      if(postBody.mode === 'cd')       return await listFiles(postBody['target-path']);
      if(postBody.mode === 'openFile') return await openFile(postBody['target-path']);
      return showErrorPage('Invalid Mode');
    }
    else {
      return showLoginPage();  // GET 時はログインページを表示する
    }
  }
  catch(error) {
    console.log('Content-Type: text/html; charset=UTF-8\n\n');
    console.log('<pre style="color: #f00; font-weight: bold;">An Error Occurred :<br>', error, '</pre>');
  };
})();
