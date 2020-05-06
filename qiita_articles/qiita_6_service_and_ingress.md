# ゼロからGKEにDjango+Reactをデプロイする(6)ServiceとIngress

[(5)Deployment](https://qiita.com/komedaoic/items/6f194cc59665f6af4749)の続きです。

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

### Serviceの追加

KubernetesにデプロイしたコンテナはServiceかIngressを使って外部公開することができます。
Serviceを使って外部公開する場合、ServiceタイプをLoadBalancerにするかExternalNameにして外部公開する方法がありますが、今回はIngressを使ってServiceを公開する構成にしたいと思います。

ServiceもDeploymentと同様、yml形式でマニフェストファイルを作成し、kubectlでGKEにリソースを追加することができます。

``` sh
# ファイルの作成
\gke-django-tutorial\manifests\type nul > service.yml
```

```yml:service.yml
kind: Service
apiVersion: v1
metadata:
  name: frontend-node-service
spec:
  type: NodePort
  selector:

    app: frontend

  ports:

    - port: 80

      targetPort: 80
      protocol: TCP

---
kind: Service
apiVersion: v1
metadata:
  name: backend-node-service
spec:
  type: NodePort
  selector:

    app: backend

  ports:

    - port: 80

      targetPort: 80
      protocol: TCP

``` 

ServiceタイプをNodePortとしました。
外部からのリクエストはIngressのLoadBalancerがServiceに転送し、Serviceはノードの80ポート(backend-Django)に転送しています。

ノードの80ポートはPod内のリバースプロキシ(Nginx)に転送され、アプリケーションとのやり取りが実現します。

```sh
# Serviceの追加
\gke-django-tutorial\manifests\kubectl create -f service.yml
service/frontend-node-service created
service/backend-node-service created

# Serviceの確認
\gke-django-tutorial\manifests\kubectl get services
NAME                    TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)          AGE
backend-node-service    NodePort    10.28.5.61   <none>        80:31332/TCP   32s
frontend-node-service   NodePort    10.28.8.91   <none>        30:31535/TCP   35s
kubernetes              ClusterIP   10.28.0.1    <none>        443/TCP          22h
```

### Ingressの追加

HTTP(S)ロードバランサを作成するIngressを使ってアプリケーションを公開します。

``` sh
# Ingressの追加
\gke-django-tutorial\manifests\type nul > ingress.yml
```

Ingressの実態はIngressコントローラーであり、Ingressコントローラーは指定することができます。
GKEでIngressコントローラーを指定しない場合、デフォルトでCloud LoadBalancerが適用されます。
今回はデフォルトで進めていきます。

``` yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-service
  namespace: default
  annotations:
    kubernetes.io/ingress.class: gce

spec:
  rules:

    - http:

      paths:

      - path: /*

        backend:
          serviceName: frontend-node-service
          servicePort: 80

      - path: /api/*

        backend:
          serviceName: backend-node-service
          servicePort: 80

      - path: /admin/*

        backend:
          serviceName: backend-node-service
          servicePort: 80
```

``` sh
# Ingressの追加
\gke-django-tutorial\manifests\kubectl create -f ingress.yml
ingress.extensions/ingress-service created

# 確認
\gke-django-tutorial\manifests\kubectl get ingress
NAME              HOSTS   ADDRESS        PORTS   AGE
ingress-service   *       34.95.105.61   80      112s
```

ADDRESSが外部公開用のIPアドレスになります。これで外部へ公開ができたと思いきや、コンソールを確認すると `backend services are in UNHEALTHY state` なるメッセージが確認できます。

#### Podへのヘルスチェックに対応する

外部公開するIngressを通して公開されるServiceはロードバランサからのヘルスチェックに応答する必要があります。

このヘルスチェックはデフォルトでは `/` パスに対するGETリクエストに対し、HTTP200ステータスのレスポンスを期待しています。

frontendのReact側では `/` パスに対してHTTP200ステータスを返答しますが、backendのDjango側では `/` への返答は追加していません。

ヘルスチェックのリクエスト先はDeploymentを使って変更することができます。

* 参考:
  + [Ingress でヘルスチェックのリクエスト先を変更する](https://qiita.com/nirasan/items/24858dfa03883cd4aa79)
  + [【GKE】Ingressのヘルスチェックで All backend services are in UNHEALTHY stateが出る場合の原因と解決方法](https://qiita.com/arthur_foreign/items/9e7a2cf4360ffcefcc9a#nuxtjs%E3%81%AEexpress%E3%81%A7health%E3%81%AE%E3%83%91%E3%82%B9%E3%81%AB%E3%83%AA%E3%82%AF%E3%82%A8%E3%82%B9%E3%83%88%E3%81%8C%E9%A3%9B%E3%82%93%E3%81%A0%E3%82%89200%E3%81%AE%E3%82%B9%E3%83%86%E3%83%BC%E3%82%BF%E3%82%B9%E3%82%B3%E3%83%BC%E3%83%89%E3%82%92%E8%BF%94%E3%81%99)

今回はPod内に追加したリバースプロキシ(Nginx)にヘルスチェック用の `location=/healthz` を追加していました。

今回はヘルスチェックへのパスを `/healthz` に変更し、Pod内のリバースプロキシは `/healthz` に対してHTTP200ステータスを返答するようにします。

* 参考:
  + [Ingress for GKE ヘルスチェック](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress?hl=ja#health_checks)
  + [GKE Ingress + gRPC アプリケーションのヘルスチェックをどうにかする](https://medium.com/google-cloud-jp/ce-advent-calendar19-gke-ingress-grpc-health-check-55ce0167322c)

コンソール上から `Compute Engine > ヘルスチェック` を確認すると、Serviceに対するヘルスチェック先のパス一覧が表示されます。

backendサービス, frontendサービスのポートと一致する使用リソースのパスを `/healthz` に変更しておきましょう。

今回のサービスのポートは次のように確認すると、31332と31535です。

``` sh
# Serviceの確認
\gke-django-tutorial\manifests\kubectl get services
NAME                    TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)          AGE
backend-node-service    NodePort    10.28.5.61   <none>        80:31332/TCP   32s
frontend-node-service   NodePort    10.28.8.91   <none>        30:31535/TCP   35s
kubernetes              ClusterIP   10.28.0.1    <none>        443/TCP          22h
```

⇒[(7)静的IPとドメイン取得]()
