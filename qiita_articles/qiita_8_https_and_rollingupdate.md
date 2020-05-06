# ゼロからGKEにDjango+Reactをデプロイする(8)HTTPS化とロールアウト

[(7)静的IPとドメイン取得](https://qiita.com/komedaoic/items/c998180c66c6919c9f40)の続きです。

## やりたいこと

Djagno+Reactの構成でアプリケーションを開発してGoogle Kubernetes Engineにデプロイしたいけれども
まとまったチュートリアルが有りそうで無かったので書きました。

ただ**まだ完全ではない点があると思います**が、少し経験がある方ならすぐに利用できるんじゃないかと思っています。

## 注意

これは未経験の趣味エンジニアがポートフォリオを作成するためにデプロイと格闘した記録です。
不備があれば何卒御指摘をお願い致します。。

## 目指す姿

![architecture.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/224317/e24509e1-5c08-ae2b-76a7-12a9642f45cd.png)

## 環境

``` sh
$ node --version
v12.14.1

$ npm --version
6.13.7

$ python --version
Python 3.7.4

$ docker --version
Docker version 19.03.8

OS windows10 pro
```

## デプロイ

### HTTPS化

GoogleマネージドSSL証明書を構成してHTTPS化します。マニフェストファイルからSSL証明書を取得します。
これには `ManagedCertificate` オブジェクトを作成します。

* 参考:
    - [Google マネージド SSL 証明書の使用](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs?hl=ja)

``` yml
apiVersion: networking.gke.io/v1beta1
kind: ManagedCertificate
metadata:
  name: [DOMAIN_SERTIFICATE]
spec:
  domains:

    - domain.page

```

``` sh
$\gke-django-tutorial\manifests\kubectl apply -f sertificate.yml
```

HTTPへのリクエストがHTTPSにリダイレクトされるようにIngressのannotationを更新します。

``` yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: [STATIC_IP_NAME]
    kubernetes.io/ingress.allow-http: "false"  # HTTPSのみ受け付ける
    networking.gke.io/managed-certificates: [DOMAIN_SERTIFICATE]  # 使用したManagedCertificate
# ...[省略]
```

``` sh
$\gke-django-tutorial\manifests\kubectl apply -f ingress.yml
```

これで `https://domain.page/` にアクセスするとHTTPSができていることを確認できます。
が、しかし画面には何も現れません。frontendのTodoを取得するエンドポイントは `http://localhost:8080/api/` のままになっているためです。

### コンテナのロールアウト

kubernetesでは古いポッドの停止と新しいポッドへの起動を繰り返してサービスをアップデートすることができます。

今回はfrontendとbackendのコンテナを更新してきちんと機能することを確認します。

コンテナの更新はコンテナのラベルを新しく指定することで新しいコンテナに適用することができます。

コンテナのラベルはなにも考えずに `latest` としてDeploymentをデプロイしてきましたが、ラベルを使って使用するコンテナを指定することができます。

今回は `v1.0` としてコンテナをロールアウトしてみたいと思います。

#### frontend

`frontend\src\App.js` でデータを取得するリクエスト先を `https://domain.page/api/` に変更します。

``` javascript
import React, {
    Component
} from 'react';
import axios from "axios";
import './App.css';

class App extends Component {
    state = {
        todo: []
    };

    componentDidMount() {
        this.getTodos();
    }

    getTodos() {
        axios
            .get("https://domain.page/api/") // 変更
            .then(res => {
                this.setState({
                    todo: res.data
                });
            })
            .catch(err => {
                console.log(err);
            });
    }
    render() {
        return ( <
            div > {
                this.state.todo.map(item => ( <
                    div key = {
                        item.id
                    } >
                    <
                    h1 > {
                        item.title
                    } < /h1> <
                    p > {
                        item.body
                    } < /p> < /
                    div >
                ))
            } <
            /div>
        );
    }
}

export default App;
```

#### backend

`backend\config\settings.py` の `CORS_ORIGIN_WHITELIST` に取得したドメインを追加します。

```python:settings.py

CORS_ORIGIN_WHITELIST = (

    'http://localhost:3000','https://domain.page',

)

``` 

#### コンテナイメージのビルド

backend, frontendのDeploymentでは使用するコンテナを

* `image: gcr.io/gke-django-tutorial/web-front:v1.0` 
* `image: gcr.io/gke-django-tutorial/web-back:v1.0` 

のように書き換えてデプロイし直します。

```sh
# イメージのビルド
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/gke-django-tutorial/web-backend:v1.0 ./backend/web-back/.

$\gke-django-tutorial\docker image build --no-cache -t gcr.io/gke-django-tutorial/web-front:v1.0 ./frontend/web-front/.

# イメージをGCRにアップロードする
$\gke-django-tutorial\gcloud docker -- push gcr.io/gke-django-tutorial/web-back:v1.0

$\gke-django-tutorial\gcloud docker -- push gcr.io/gke-django-tutorial/web-front:v1.0

# デプロイメントを更新する
$\gke-django-tutorial\manifests\kubectl apply -f backend-deployment.yml

$\gke-django-tutorial\manifests\kubectl apply -f frontend-deployment.yml
```

* 参考:
    - [コンテナ化されたウェブ アプリケーションのデプロイ](https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app)

これで `https://domain.page/` にアクセスするとfrontend(React)のTodoアイテムが表示されました。
また、 `https://domain.page/admin/` にアクセスするとbackend(Django)の管理者画面に飛ぶことが確認できました。Ingressによるルーティングが機能していることがわかります。

## CloudStorageのCORSの構成

`https:domain.page/admin/` のCSSが反映されていない、もしくは開発者ツールを確認すると `Cloud Storage has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.` というエラーが発生している場合にはバケットの[クロスオリジンリソースシェアリング(CORS)の構成](https://cloud.google.com/storage/docs/configuring-cors#gsutil)を設定しましょう。

CORSの構成は構成を記述したjsonファイルをgsutilを使って追加することができます。

``` sh
# バケットのCORSを確認
$\gke-django-tutorial\gsutil cors get gs://[STORAGE_NAME]

# 構成ファイルの作成
$\gke-django-tutorial\type nul > cors-json-file.json
```

jsonファイルを作成します。

``` json
[
  {
    "origin": ["https://domain.page"],
    "responseHeader": ["Content-Type"],
    "method": ["GET", "HEAD", "DELETE"],
    "maxAgeSeconds": 3600
  }
]
```

CORSを追加します。

``` sh
$\gke-django-tutorial\gsutil cors set cors-json-file.json gs://[STORAGE_NAME]
```

⇒[(9)掃除とまとめ]()
