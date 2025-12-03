## Appendix

The SONiC image used in the lab leverages [VPP](https://fd.io/) as its underlying dataplane.

To access the VPP CLI from the SONiC bash shell:

```
docker exec -it syncd vppctl
```