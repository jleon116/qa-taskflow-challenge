import http from "k6/http";
import { sleep, check } from "k6";

export const options = {

  stages: [
    { duration: "30s", target: 50 },  // load
    { duration: "2m", target: 50 },
    { duration: "30s", target: 0 },
  ]
};

const BASE_URL = "http://localhost:8080";

export default function () {

  // GET tasks
  let res = http.get(`${BASE_URL}/api/tasks`);

  check(res, {
    "status is 200": (r) => r.status === 200
  });

  // POST task
  let payload = JSON.stringify({
    title: "performance test task",
    description: "created by k6"
  });

  http.post(`${BASE_URL}/api/tasks`, payload, {
    headers: { "Content-Type": "application/json" }
  });

  // stats endpoint
  http.get(`${BASE_URL}/api/stats`);

  sleep(1);
}