### Deploy debug pods

```bash
# 1. First test with debug pods
kubectl apply -f srv6-pytorch-debug-pods.yaml
kubectl get pods -o wide

# 2. Check both pods have net1 interface with IPv6
kubectl exec srv6-debug-0 -- ip addr show net1
kubectl exec srv6-debug-1 -- ip addr show net1

# 3. Test connectivity between pods on backend network
kubectl exec srv6-debug-0 -- ping6 -c 3 <srv6-debug-1-net1-ip>

# 4. If connectivity works, deploy the real training
kubectl delete -f srv6-pytorch.yaml
kubectl apply -f srv6-pytorch-statefulset.yaml
kubectl logs -f srv6-pytorch-0
```

### Deploy training pods

```bash
kubectl delete -f srv6-pytorch-debug-pods.yaml
kubectl apply -f srv6-pytorch-training-test.yaml
```