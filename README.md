# thu_validator
匿名验证一个人是否能访问清华网络，原理很简单，通过校内的 dns 查询一个指定域名，即可验证成功。

WebVPN 在访问时会先解析 ip，此时使用的 dns 服务器恰好就是 166.111.8.28，故可以满足需求。

另外这个 demo 并没有在 python 里限制连入的地址，而是在系统层面使用 iptables 限制的。

demo 地址：https://val-demo.mcfx.us/
