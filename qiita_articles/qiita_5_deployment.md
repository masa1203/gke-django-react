# ゼロからGKEにDjango+Reactをデプロイする(5)Deployment

[(4)クラスタの作成とコンテナPUSH](https://qiita.com/komedaoic/items/99b5afb169bc5b37472a)の続きです。

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

### Frontendのデプロイ

kubernetesクラスターはkubernetesのリソースを記述したマニフェストファイルを適用することでクラスターの構成を組立ていくことができます。

複数のコンテナが一緒になったPodを追加するため、Deploymentファイルを作成します。

まずはfontendのDeploymentを作成してfrontendのPodをデプロイします。
Deploymentとして `frontend-react.yml` というファイルを作成します。

``` sh
# マニフェストファイルを格納するディレクトリを作成
$\gke-django-tutorial\mkdir manifests
$\gke-django-tutorial\cd manifests

# Deploymentファイルの作成
$\gke-django-tutorial\manifests\type nul > frontend-deployment.yml
```

``` yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: frontend
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:

        - name: web-front

          image: gcr.io/gke-django-tutorial/web-front:latest
          imagePullPolicy: Always
          command: ["npm", "start"]
          ports:

            - containerPort: 3000
        - name: nginx-front

          image: gcr.io/gke-django-tutorial/nginx-front:latest
          imagePullPolicy: Always
          ports:

            - containerPort: 80

```

Deploymentの中身はdocker-composeと非常によく似ています。Pod内は `Nginx+React` で構成されています。

クラスターへのデプロイはkubectlを使って行います。インストールしてあることを想定しています。

``` sh
# Deploymentをデプロイ
$\gke-django-tutorial\manifests\kubectl create -f frontend-deployment.yml
deployment.extensions/frontend created

# 確認
$\gke-django-tutorial\manifests\kubectl get pods
NAME                        READY   STATUS              RESTARTS   AGE
frontend-77f75d4c47-lgzv6   0/1     CrashLoopBackOff   6          9m39s
```

#### frontendのCrashLoopBackOff

`STATUS` が `CrashLoopBackOff` となってしましました。ログを確認してみます。

``` sh
$ kubectl logs frontend-77f75d4c47-lgzv6

> frontend@0.1.0 start /code
> react-scripts start

[34mℹ[39m [90m｢wds｣[39m: Project is running at http://XX.XX.X.X/
[34mℹ[39m [90m｢wds｣[39m: webpack output is served from
[34mℹ[39m [90m｢wds｣[39m: Content not from webpack is served from /code/public
[34mℹ[39m [90m｢wds｣[39m: 404s will fallback to /
Starting the development server...
```

Reactの環境構築周りに問題があるらしいことがわかります。

* 参考: [stack overflow : GKE deployment ReactJS app CrashLoopBackoff](https://stackoverflow.com/questions/61463529/gke-deployment-reactjs-app-crashloopbackoff)

どうやら `react-scripts` が悪さをしているようです。

`frontend\package-lock.json` を確認すると `react-scripts` のバージョンは `3.4.1` でした。
`3.4.0` でインストールし直したあと、もう一度GCRへします。

``` sh
# 3.4.1をアンインストール
$\gke-django-tutorial\frontend\npm uninstall react-scripts@3.4.1

# 3.4.0をインストール
$\gke-django-tutorial\frontend\npm install react-scripts@3.4.0 --save

# frontendコンテナイメージの再ビルド
$\gke-django-tutorial\docker image build --no-cache -t gcr.io/[YOUR_PROJECT]/web-front:latest ./frontend/web-front/.

# GCRへのアップロード
$\gke-django-tutorial\gcloud docker -- push gcr.io/[YOUR_PROJECT]/web-front:latest

# frontendのpodを削除して新しいPodを立ち上げる
$\gke-django-tutorial\manifests\kubectl delete pod frontend-77f75d4c47-lgzv6

# 確認
$\gke-django-tutorial\manifests\kubectl get pods

```

問題なくfrontendのPodがデプロイできていることが確認できました。

### Backendのデプロイ

frontendと同じようにbackendのDeploymentを作成してデプロイします。

`backend-deployment.yml` を作成します。

``` sh
$\gke-django-tutorial\manifests\type nul > backend-deployment.yml
```

``` yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: backend
  labels:
    app: backend
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:

        - name: web-back

          image: gcr.io/gke-django-tutorial/web-back:latest
          imagePullPolicy: Always
          command: ["gunicorn", "-b", ":8000", "config.wsgi"]
          env:

            - name: DATABASE_USER

              valueFrom:
                secretKeyRef:
                  name: cloudsql
                  key: username

            - name: DATABASE_PASSWORD

              valueFrom:
                secretKeyRef:
                  name: cloudsql
                  key: password

            - name: SECRET_KEY

              valueFrom:
                secretKeyRef:
                  name: secret-key
                  key: SECRET_KEY
          ports:

            - containerPort: 8000
        - image: gcr.io/cloudsql-docker/gce-proxy:1.16

          name: cloudsql-proxy
          command:
            [
              "/cloud_sql_proxy",
              "--dir=/cloudsql",
              "-instances=gke-django-tutorial:asia-northeast1:websql=tcp:5432",
              "-credential_file=/secrets/cloudsql/credentials.json",
            ]
          volumeMounts:

            - name: cloudsql-oauth-credentials

              mountPath: /secrets/cloudsql
              readOnly: true

            - name: ssl-certs

              mountPath: /etc/ssl/certs

            - name: cloudsql

              mountPath: /cloudsql

        - image: gcr.io/gke-django-tutorial/nginx-back:latest

          name: nginx-back
          imagePullPolicy: Always
          ports:

            - containerPort: 80

      volumes:

        - name: cloudsql-oauth-credentials

          secret:
            secretName: cloudsql-oauth-credentials

        - name: ssl-certs

          hostPath:
            path: /etc/ssl/certs

        - name: cloudsql

          emptyDir:
```

backend側のPodは `web-back(Django)` , `nginx-back(Nginx)` , `cloudsql-proxy` のコンテナがまとめられています。

Django側で必要な環境変数を作成したSecretsから参照していることが確認できます。
backendのイメージは既に作成してGCRにpushしてあるので、早速デプロイします。

``` sh
# backendのデプロイ
$\gke-django-tutorial\manifests\kubectl create -f backend-deployment.yml

# 確認
$\gke-django-tutorial\manifests\kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
backend-989b96b5-ldc9b      3/3     Running   0          35s
frontend-77f75d4c47-f2fdl   1/1     Running   0          28m

$\gke-django-tutorial\manifests\kubectl logs backend-989b96b5-ldc9b web-back
[2020-04-29 14:55:11 +0000] [1] [INFO] Starting gunicorn 20.0.4
[2020-04-29 14:55:11 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
[2020-04-29 14:55:11 +0000] [1] [INFO] Using worker: sync
[2020-04-29 14:55:11 +0000] [8] [INFO] Booting worker with pid: 8

$\gke-django-tutorial\manifests\kubectl logs backend-989b96b5-ldc9b nginx-back

$\gke-django-tutorial\manifests\kubectl logs backend-989b96b5-ldc9b cloudsql-proxy

```

STATUSがRunningになっているので問題なく機能しているようです。

frontend, backendのDeploymentを追加することができました。

⇒[(6)ServiceとIngressを追加する]()
