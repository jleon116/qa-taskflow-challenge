import http from "k6/http";

export const options = {
  stages: [
    { duration: "30s", target: 50 },
    { duration: "30s", target: 100 },
    { duration: "30s", target: 200 },
    { duration: "30s", target: 0 }
  ]
};

export default function () {
  http.get("http://localhost:8080/api/tasks");
}