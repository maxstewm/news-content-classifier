v1.1 eval_spider工作正常
# 关于 Stats 的一些观察：

## downloader/exception_count: 2577 很高，大部分是 ERR_NAME_NOT_RESOLVED (2531)。解决 DNS 问题后，这个数字应该会大幅下降。

## dupefilter/filtered: 8513 表示去重过滤器工作正常，阻止了重复的 URL 被重新抓取，这是好的。

## request_depth_max: 18 确认了递归抓取正在进行，爬虫深入到了网站的层级结构中。

## playwright/request_count: 56913, playwright/request_count/navigation: 4195, playwright/request_count/aborted: 52651。大量的 aborted 请求说明你的 PLAYWRIGHT_ABORT_REQUEST 配置非常有效，阻止了绝大多数非文档资源的加载，节省了大量带宽和 VM 资源。这是非常好的优化。

## playwright/page_count/max_concurrent: 8 符合你的设置。

memusage/max: 660758528 (~660MB) 在 4GB 内存的 VM 上是完全可以接受的，说明目前的并发设置和 SpaCy 模型大小对内存影响不大。