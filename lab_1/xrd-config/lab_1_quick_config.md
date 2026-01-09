## Contents
- [Contents](#contents)
- [london](#london)
- [rome](#rome)
- [Back to Lab 1 Guide](#back-to-lab-1-guide)

## london
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
  locator MyLocator
  !
 ! 
 address-family ipv6 unicast
  segment-routing srv6
  locator MyLocator
  !
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 unicast
  !
 ! 
 neighbor-group xrd-ipv6-peer
  address-family ipv6 unicast
  !
 !
!  
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:1111::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:1111::/48
   !
  !
 !
 commit
 
```

## rome
```
conf t

router isis 100
 address-family ipv6 unicast
  segment-routing srv6
   locator MyLocator
   !
  !
 !
!
router bgp 65000
 address-family ipv4 unicast
  segment-routing srv6
  locator MyLocator
  !
 ! 
 address-family ipv6 unicast
  segment-routing srv6
  locator MyLocator
  !
 !
 neighbor-group xrd-ipv4-peer
  address-family ipv4 unicast
  !
 ! 
 neighbor-group xrd-ipv6-peer
  address-family ipv6 unicast
  !
 !
!
segment-routing
 srv6
  encapsulation
   source-address fc00:0000:7777::1
  !
  locators
   locator MyLocator
    micro-segment behavior unode psp-usd
    prefix fc00:0000:7777::/48
   !
  !
 !
 commit

 ```

 ## Back to Lab 1 Guide
[Lab 1 Guide](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_1/lab_1-guide.md#validate-srv6-configuration-and-reachability)