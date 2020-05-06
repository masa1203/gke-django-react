# ゼロからGKEにDjango+Reactをデプロイする(2)frontendの開発 - Nginx + React

[(1)backendの開発 - Nginx + Django](https://qiita.com/komedaoic/items/8626b52070163290d8f1)の続きです。

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

### frontendの開発(React編)

frontendはReactで作成します。Pod内の構成を整理しておきます。

| 役割     | コンテナイメージ                  |
|----------|---------------------------|
| プロキシサーバー | Nginx:1.17.4-alpine       |
| アプリケーション | node12.14.1-React@16.13.1 |

新しいコマンドプロンプトを開いてReactのプロジェクトを開始していきます。
backendと同じようにディレクトリを作成します。

``` sh
# ディレクトリの作成
$\gke-django-tutorial\frontend\mkdir web-front
$\gke-django-tutorial\frontend\mkdir nginx

# ディレクトリ下にReactプロジェクトをたてる
$\gke-django-tutorial\frontend\cd web-front
$\gke-django-tutorial\frontend\web-front\npx create-react-app .

# Reactの開発用サーバーを立ち上げてみる
$\gke-django-tutorial\frontend\yarn start
yarn run v1.22.0
$ react-scripts start
i ｢wds｣: Project is running at http://192.168.11.8/
i ｢wds｣: webpack output is served from
i ｢wds｣: Content not from webpack is served from C:\--your_file_path--\gke-django-tutorial_v2\frontend\public
i ｢wds｣: 404s will fallback to /
Starting the development server...
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.11.8:3000

Note that the development build is not optimized.
To create a production build, use yarn build.
```

`http://localhost:3000` にアクセスするとReactのWelcomeページが確認できます。

APIをリクエストするのには `axios` を使います。

``` sh
# ライブラリのインストール
$\gke-django-tutorial\frontend\web-front\npm install axios --save
```

#### App.js

APIのエンドポイントは以下のような形でAPIを返してきます。

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
            .get("http://localhost:8080/api/")
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
                    } < /p> <
                    /div>
                ))
            } <
            /div>
        );
    }
}

export default App;
```

fronendからbarckendへのapiを叩いてtodoリスト一覧を表示させることができました。
これでローカルでの環境構築ができました。

#### Dockerfileの作成

つづいてfrontendのDocker化を行います。backendと同じようにfrontendディレクトリ下にDockerfileを作成し、docker-composeで起動させたいと思います。

``` sh
# docker-composeの作成
$\gke-django-tutorial\frontend\web-front\type nul > Dockerfile
# .dockerignoreの作成
$\gke-django-tutorial\frontend\web-front\type nul > .dockerignore
```

``` Dockerfile
# frontend/web-back/Dockerfile
FROM node:12.14.1

WORKDIR /code

# Install dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install

# Add rest of the client code
COPY . ./
RUN npm run build

EXPOSE 3000

```

frontend に関しては `node_modules/` が巨大であるため、これをマウントしたりコピーしたりするとかなりの時間を要します。

```.dockerignore
node_modules

``` 

### frontendの開発(Nginx編)

frontend-Pod内にもbackendと同じようにリバースプロキシサーバーとしてNginxコンテナを配置します。
流れはbackendの時と同じです。

```sh
# Nginx用のファイル作成
$\gke-django-tutorial\frontened\nginx\type nul > Dockerfile
$\gke-django-tutorial\frontened\nginx\type nul > Dockerfile.dev
$\gke-django-tutorial\frontend\nginx\type nul > default.conf
$\gke-django-tutorial\frontend\nginx\type nul > default.dev.conf
```

``` conf
upstream react {
    server web-front:3000;
}

; default.confの場合
; upstream react {
    ; server localhost:8000;
; }

server {

    listen 80;

    location = /healthz {
        return 200;
    }

    location / {
        proxy_pass http://react;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
    }
    location /sockjs-node {
	    proxy_pass http://react;
      proxy_http_version 1.1;
	    proxy_set_header Upgrade $http_upgrade;
	    proxy_set_header Connection "upgrade";
	}

    error_page 500 502 503 504    /50x.html;

    location = /50x.html {
        root    /usr/share/nginx/html;
    }
}

```

リバースプロキシは `Nginxコンテナ:80` ⇒ `React:3000` となるようにしました。

`location = /healthz` ディレクティブはGKEにデプロイ後に必要になるヘルスチェック用のパスです。

`server` ディレクティブはGKEにデプロイする場合は `localhost:3000` とし、docker-composeで起動する場合は `web-front:3000` としています。
これはdocker-composeで起動する場合はサービス名で名前解決をする必要があるためです。
GKEにデプロイする場合は同じPod内にあるため、 `localhost:3000` で名前解決します。

DockerfileはNginxの設定ファイルをNginxコンテナにコピーさせることで設定を反映させます。

``` Dockerfile
# backend\nginx\Dockerfile.dev
FROM nginx:1.17.4-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY default.dev.conf /etc/nginx/conf.d

# backend\nginx\Dockerfile.devの場合
# COPY default.conf /etc/nginx/conf.d

```

### frontendの開発(docker-compose編)

docker-composeを使ってNginx+Reactの構成でコンテナを起動させたいと思います。

``` sh
# docker-compose.ymlの作成
$\gke-django-tutorial\frontend\type nul > docker-compose.yml
```

``` yaml
# docker-compose.yml
version: "3.7"

services:
  web-front:
    container_name: react-frontend
    build: ./web-front/.
    volumes:

      - ./web-front:/code
      - /code/node_modules

    stdin_open: true
    tty: true
    environment:

      - CHOKIDAR_USEPOLLING=true
      - NODE_ENV=development

    command: yarn start
    networks:

      - frontend_network

  server:
    container_name: nginx_front
    build:
      context: ./nginx/.
      dockerfile: Dockerfile.dev
    ports:

      - "80:80"

    depends_on:

      - web-front

    networks:

      - frontend_network

networks:
  frontend_network:
    driver: bridge
```

ビルドして起動してみます。

``` sh
# イメージのビルド
$\gke-django-tutorial\frontend\docker-compose build --no-cache

# docker-composeの起動
$\gke-django-tutorial\frontend\docker-compose up
```

ビルドに時間がかかりますが、問題なく起動することができました。

`http://localhost:80` にアクセスするとbackendで追加したTodoアイテムが表示されているはずです。

`http://localhost:80` ⇒ `Nginx(front)コンテナ:80` ⇒ `React:3000` となるように
ポートフォワーディングされています。

また、ブラウザから `http://localhost:8080/api/` へリクエストが送られることによってbackendからTodoアイテムが返答され、fronten側で表示させることができました。

これでdocker-composeでfrontendに使用するコンテナが動作できていることが確認できました。

### ローカル編まとめ

docker-composeでNginx+DjagnoとNginx+Reactを起動させ、RestAPIでやりとりさせることができました。これをkubernetesへデプロイさせていきましょう。

⇒[(3)GCPのプロジェクトを作成する]()へ
