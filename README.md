# thu_validator
匿名验证一个人是否能访问清华网络，原理很简单，通过校内的 dns 查询一个指定域名，即可验证成功。

这个 repo 里的 demo 为了方便演示，使用了 101.6.6.6 的 DNS over HTTPS 模式，但是 101.6.6.6 允许其他一些学校访问，所以不是最好的选择。更好的选择是 166.111.8.28。

同时这个 demo 并没有在 python 里限制连入的地址，而是在系统层面使用 iptables 限制的。

demo 地址：https://val-demo.mcfx.us/
