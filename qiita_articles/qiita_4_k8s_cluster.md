# ゼロからGKEにDjango+Reactをデプロイする(4)クラスタの作成とコンテナPUSH

[(3)GCPのプロジェクトを作成する](https://qiita.com/komedaoic/items/45a0082467c6b290622d)の続きです。

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

### Kubernetesクラスターの作成

クラスターを作成してコンテナをデプロイします。ServiceとIngressを設定することで外部からアクセスすることが可能になります。

コンソールからクラスタを作成します。

``` sh
クラスター名: [K8S_CLUSTER]
ロケーションタイプ:ゾーン:[K8S_CLUSTER_ZONE]
マスターのバージョン: 1.14.10-gke.27(デフォルト)
```

### contextsの入手

作成したクラスターをローカルのkubectlから利用するためにcontextsを入手します。

``` sh
$\gke-django-tutorial\gcloud container clusters get-credentials [K8S_CLUSTER] --zone="[K8S_CLUSTER_ZONE]"
Fetching cluster endpoint and auth data.
kubeconfig entry generated for [K8S_CLUSTER].

# コンテキストが適用されているかどうかを確認する
$\gke-django-tutorial\manifests\kubectl config current-context
```

### Secrets

データベースのユーザー名、パスワードなどの秘匿すべき環境変数は `.env` で管理してきましたが、KubernetesではSecretsリソースに登録して使用します。

#### Cloud SQL

Secretsを利用することでCloudSQLのユーザー名、パスワードを環境変数として安全に使用することができます。
GKE から Cloud SQL のインスタンスを使用するにあたって、インスタンスレベルアクセスとデータベースアクセスに関するSecretsを作成する必要があります。

* 参考: [インスタンスのアクセス制御]:(https://cloud.google.com/sql/docs/mysql/instance-access-control)

インスタンスレベルのアクセスについてSecretsを作成します。

``` sh
$\gke-django-tutorial\manifests\kubectl create secret generic cloudsql-oauth-credentials --from-file=credentials.json=".\secrets\cloudsql\ZZZZZZZZZZZZZZZ.json"

secret/cloudsql-oauth-credentials created
```

データベースへアクセスに関する secret を作成します。

``` sh
$\gke-django-tutorial\manifests\kubectl create secret generic cloudsql --from-literal=username="[DATABASE_USER]" --from-literal=password="[DATABASE_PASSWORD]"
```

#### SECRET_KEY

`.env` ファイルに記述されている残りの `SECRET_KEY` をSecretsに追加しましょう。
`backend/config/settings.py` の `DEBUG` はFalseとしておきます。

``` sh
$\gke-django-tutorial\manifests\kubectl create secret generic secret-key --from-literal=SECRET_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

`backend/config/settings.py` で関係のある個所は以下のような状態になります。

``` python
# backend/config/settings.py

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.basename(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')  # 変更

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        # If you are using Cloud SQL for MySQL rather than PostgreSQL, set
        # 'ENGINE': 'django.db.backends.mysql' instead of the following.
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'web-db',
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

```

### コンテナイメージのビルド

ローカルでイメージをビルドしてGoogle Cloud Registryにアップロードします。
イメージ名は `gcr.io/${PROJECT}/${IMAGENAME}:${TAGNAME}` 形式にする必要があります。

``` sh
# プロジェクト名の確認
$\gke-django-tutorial\gcloud config get-value project
Your active configuration is: [YOUR_PROJECT]
gke-django-tutorial

# イメージのビルド
# web-back(Django)
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/web-back:latest ./backend/web-back/.

# nginx-back
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/nginx-back:latest ./backed/nginx/.

# web-front(React)
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/web-front:latest ./frontend/web-front/.

# nginx-back
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/nginx-front:latest ./frontend/nginx/.
```

### コンテナイメージのアップロード

作成した4つのDockerイメージをGoocle Container Registry(以下, GCR)にアップロードします。

``` sh
# backend
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/web-back:latest
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/nginx-back:latest

# frontend
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/web-front:latest
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/nginx-front:latest
```

backend, frontendのコンテナイメージを作成してGCRにPushすることが出来ました。

⇒[(5)Deployment](https://qiita.com/komedaoic/items/0f4c5366fc490aaf47dc)
