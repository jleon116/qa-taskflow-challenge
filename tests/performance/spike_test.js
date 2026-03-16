import http from "k6/http";

export const options = {
  stages: [
    { duration: "10s", target: 10 },
    { duration: "10s", target: 100 }, // spike
    { duration: "30s", target: 100 },
    { duration: "10s", target: 0 }
  ]
};

export default function () {
  http.get("http://localhost:8080/api/tasks");
}