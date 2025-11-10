import http from "k6/http";
import { check, sleep } from "k6";
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

const baseUrl = `http://${__ENV.HOST || "localhost"}:${__ENV.PORT || 8080}`;

export const options = {
  vus: 1,
  duration: "5s",
};

export default function () {
  const fileData = open("testimagen.jpg", "b");

  const payload = {
    file: http.file(fileData, "testimagen.jpg", "image/jpeg"),
  };

  const res = http.post(`${baseUrl}/api/braille-to-text`, payload, {
    headers: {
      accept: "application/json",
    },
  });

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response is not empty": (r) => r.body.length > 0,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    "/results/summary.html": htmlReport(data, { debug: false }),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
