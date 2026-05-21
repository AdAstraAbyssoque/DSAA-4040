$ kubectl get hpa backend-hpa -n bookstore -w
NAME          REFERENCE            TARGETS    MINPODS  MAXPODS  REPLICAS  AGE
backend-hpa   Deployment/backend   14%/60%    2        8        2         8m07s
backend-hpa   Deployment/backend   17%/60%    2        8        2         8m22s
backend-hpa   Deployment/backend   89%/60%    2        8        2         8m37s
backend-hpa   Deployment/backend   127%/60%   2        8        3         8m51s
backend-hpa   Deployment/backend   141%/60%   2        8        4         9m06s
backend-hpa   Deployment/backend   118%/60%   2        8        4         9m21s
backend-hpa   Deployment/backend   83%/60%    2        8        5         9m37s
backend-hpa   Deployment/backend   62%/60%    2        8        5         9m52s
backend-hpa   Deployment/backend   58%/60%    2        8        5         10m07s
backend-hpa   Deployment/backend   54%/60%    2        8        5         10m22s
backend-hpa   Deployment/backend   11%/60%    2        8        5         12m18s
backend-hpa   Deployment/backend   7%/60%     2        8        5         12m33s
backend-hpa   Deployment/backend   6%/60%     2        8        2         17m41s
