Build/update the pytorch-srv6 docker image:

```
docker build -t pytorch-srv6-demo24 .
```

### Test Plugin application flow:

┌─────────────────────────────────────────────────────────────────┐
│ test_plugin.py                                                  │
│   └── main()                                                    │
│         └── DemoPlugin(api_endpoint)                            │
│         └── plugin.init_process_group()                         │
│               │                                                 │
│               ├── ① init_distributed()                         |
│               │     └── dist.init_process_group(gloo, tcp://...)│
│               │                                                 │
│               │                                                 │
│               ├── ② get_all_nodes()        ← NEVER REACHED     │
│               │                                                 │
│               └── ③ program_all_routes()   ← NEVER REACHED     │
│                     └── call Jalapeno API                       │
│                     └── get SRv6 SID                            │
│                     └── ip -6 route add ... encap seg6 ...      │
└─────────────────────────────────────────────────────────────────┘