# GKE に Django+React をデプロイする

## やりたいこと

Docker で環境構築して k8s にデプロイしたい。
バックエンドは DjangoRestFramework で RestAPI を配信して、フロントエンドは React(TypeScript)で実装したい。

## 環境

```sh
node --version
v12.14.1

npm --version
6.13.7

python --version
Python 3.7.4

docker --version
Docker version 19.03.8
```

## まずはローカルで始める

### ディレクトリを作成する。

```sh
# プロジェクトフォルダの作成
mkdir gke-django-tutorial
cd gke-django-tutorial
# ディレクトリを作成する
mkdir backend
mkdir frontend
```

### Backend の開発を始める

backend は Djang-rest-framework で RestAPI を作成します。
まずは backend から環境を作成してみます。

```sh
# backendディレクトリに移動
cd backend
```

1. アプリケーションを作成する
   ローカルで起動できることを確認する

2. GCP でプロジェクトを作成する
   CloudSQL, CloudStorage を使ってローカルからクラウドのマネージドサービスを利用できるようにする。

3. Docker イメージを作成する
   イメージを作成する。.env は省いた方が良いがこれはまだ対応していない。

4. GKE のクラスタを作成する
   プロジェクトを開始して GKE クラスタを作成する。

5. Deployment を作成する
   backend の Secret を作成してデータベースに利用。

6. Service を作成する
   backend と frontend

7. Ingress を作成する

8. ヘルスチェックに対応する
   ヘルスチェックに対応する。
   静的アドレスに追加する。200 を返すように view を追加。

9. DNS に対応する
   ドメインを取得して ingress に host を追加。

10. HTTPS 化
    https://qiita.com/watiko/items/71d78a4d31eee02cb47d
