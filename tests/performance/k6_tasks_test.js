import http from "k6/http";
import { sleep } from "k6";

export const options = {
  vus: 50,
  duration: "2m",
};

export default function () {

  http.get("http://localhost:8080/api/tasks");

  http.post("http://localhost:8080/api/tasks", JSON.stringify({
    title: "Performance test task",
    description: "created by k6"
  }), {
    headers: { "Content-Type": "application/json" }
  });

  http.get("http://localhost:8080/api/stats");

  sleep(1);
}