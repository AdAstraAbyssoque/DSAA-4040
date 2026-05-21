$ hey -z 4m -c 50 -q 80 'http://bookstore.local/api/books?q=cloud'

Summary:
  Total:        242.13 secs        Slowest:  0.4413 secs
  Slowest:      0.4413 secs        Fastest:  0.0021 secs
  Average:      0.0237 secs        Requests/sec: 1873.18

  Total data:   1.39 GB            Size/request: 3057 bytes

Latency distribution:
  10% in 0.0098 s   50% in 0.0203 s   90% in 0.0382 s
  25% in 0.0136 s   75% in 0.0289 s   95% in 0.0461 s
                                      99% in 0.0712 s

Status code distribution:
  [200] 453482 responses
  [503]    127 responses
