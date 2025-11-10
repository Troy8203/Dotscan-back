import http from "k6/http";
import { sleep, check } from "k6";

const host = __ENV.HOST || "localhost";
const port = __ENV.PORT || 8080;

export const options = {
  vus: 5,
  duration: "10s",
};

export default function () {
  const res = http.get(`http://${host}:${port}/api`);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  sleep(1);
}
