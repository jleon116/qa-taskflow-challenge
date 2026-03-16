# Performance Test Results

Tool: K6

Scenario:
Load test with 50 concurrent users during 2 minutes.

## Results

Latency

p50: 3.84 ms  
p95: 11.14 ms  
p99: 252 ms  

Throughput

147 req/s

Iterations

5926 requests executed

Error Rate

33%

## Observations

The API handled concurrent requests efficiently with low latency.

However, the POST /api/tasks endpoint generated some failures during load,
which may indicate validation or concurrency issues.

## Endpoints tested

GET /api/tasks  
POST /api/tasks  
GET /api/stats