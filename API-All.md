# NextCloud-Operator Usage-API
## Upload file
### how
- method
```
PUT
```
- Authorization
```
name: to....
pass: AppPass(operator)
```
- URI
```
https://<domain>/remote.php/dav/files/<user>/<folder>/<upload-name>
```
|名称|説明|
|---|---|
| domain | 対象サービスのFQDN |
| user | アップロード者名 |
| folder | アップロード先のフォルダー |
| upload-name | アップロードしたいファイルのアップロード先での名前 |

### 例
```bash
curl -X PUT -u tochiman:FeBmJ-ns8Y8-dbZ4B-dtdHT-DiMJG https://nextcloud.tochiman.com/remote.php/dav/files/tochiman/nextcloud-data/main.py -T ./main.py
```

## Make folder
### how
- method
```
MKCOL
```
- Authorization
```
name: to....
pass: AppPass(operator)
```
- URI
```
https://<domain>/remote.php/dav/files/<user>/<folder>/<make-folder-name>
```
|名称|説明|
|---|---|
| domain | 対象サービスのFQDN |
| user | アップロード者名 |
| folder | アップロード先のフォルダー |
| make-folder-name | 作りたいフォルダの名前 |
### 例
```
curl -X MKCOL -u tochiman:FeBmJ-ns8Y8-dbZ4B-dtdHT-DiM
JG https://nextcloud.tochiman.com/remote.php/dav/files/tochiman/nextcloud-data/test
```