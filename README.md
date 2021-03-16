# Neo's CGI Explorer

CGI Explorer, File Uploader, Text Editor.


## Features

- Login
- File Explorer (List Files And Change Directory)
- File Preview (Text Files)
- File Download (Non-Text Files)
- File Upload (Made With Ruby CGI)
- Text File Editor
- Create Directory (Mkdir) And File (Touch)
- Rename Directory And File
- Move Directory And File
- Copy File (Copy Directory Not Supported)
- Remove Directory (Recursively) And File


## Setup

- Copy All Files To Web Server
- Set Execute Permission On The Files
- Edit `nexp-config.json` To Set Credential And Root Directory Path
- Make Root Directory And Set Permissions (Detault : `nexp-files/` On `/var/www/html/`)
- If You Need...
    - Edit The Shebang (Default : `#!/usr/bin/env node` Or `#!/usr/bin/ruby`)
    - Edit The Variable `CONFIG_FILE_PATH` In CGI Files (Default : `./nexp-config.json`)
    - Edit The Variable `API_URL` In HTML File


## Links

- [Neo's World](https://neos21.net/)
