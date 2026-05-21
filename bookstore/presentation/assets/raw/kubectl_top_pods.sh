$ kubectl top pod -n bookstore -l app=backend
NAME                       CPU(cores)   MEMORY(bytes)
backend-7c89b8d9c4-2lwzb   437m         148Mi
backend-7c89b8d9c4-9hk2t   404m         141Mi

$ # ── load fires; HPA scales out ──

$ kubectl get pods -n bookstore -l app=backend
NAME                       READY   STATUS              RESTARTS   AGE
backend-7c89b8d9c4-2lwzb   1/1     Running             0          11m
backend-7c89b8d9c4-9hk2t   1/1     Running             0          11m
backend-7c89b8d9c4-ftxg8   1/1     Running             0          47s
backend-7c89b8d9c4-q4z6r   0/1     ContainerCreating   0          14s
backend-7c89b8d9c4-vp7jx   0/1     Running             0          14s

$ kubectl top pod -n bookstore -l app=backend
NAME                       CPU(cores)   MEMORY(bytes)
backend-7c89b8d9c4-2lwzb   183m         151Mi
backend-7c89b8d9c4-9hk2t   168m         144Mi
backend-7c89b8d9c4-ftxg8   174m         137Mi
backend-7c89b8d9c4-q4z6r   189m         133Mi
backend-7c89b8d9c4-vp7jx   161m         136Mi
