#!/bin/bash

docker exec -it clab-sonic-host00 ip -6 route del 2001:db8:1001::/64
docker exec -it clab-sonic-host00 ip -6 route del 2001:db8:1002::/64
docker exec -it clab-sonic-host00 ip -6 route del 2001:db8:1003::/64
docker exec -it clab-sonic-host01 ip -6 route del 2001:db8:1000::/64
docker exec -it clab-sonic-host01 ip -6 route del 2001:db8:1002::/64
docker exec -it clab-sonic-host01 ip -6 route del 2001:db8:1003::/64
docker exec -it clab-sonic-host02 ip -6 route del 2001:db8:1000::/64
docker exec -it clab-sonic-host02 ip -6 route del 2001:db8:1001::/64
docker exec -it clab-sonic-host02 ip -6 route del 2001:db8:1003::/64
docker exec -it clab-sonic-host03 ip -6 route del 2001:db8:1000::/64
docker exec -it clab-sonic-host03 ip -6 route del 2001:db8:1001::/64
docker exec -it clab-sonic-host03 ip -6 route del 2001:db8:1002::/64