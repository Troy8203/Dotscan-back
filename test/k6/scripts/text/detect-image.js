import http from "k6/http";
import { check, sleep } from "k6";
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

const BASE_URL = `http://${__ENV.HOST || "localhost"}:${__ENV.PORT || 8080}`;

const basic_image = open("/scripts/assets/braille_basic.jpg", "b");

export const options = {
  scenarios: {
    smokeTest: {
      executor: "constant-vus",
      vus: 1,
      duration: "30s",
      exec: "smokeTest",
    },
    gradualLoad: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "30s", target: 5 },
        { duration: "1m", target: 20 },
        { duration: "2m", target: 40 },
        { duration: "2m", target: 50 }, // máximo recomendado
        { duration: "1m", target: 50 }, // mantener carga
        { duration: "1m", target: 0 }, // rampa de bajada
      ],
      exec: "stressTest",
      gracefulRampDown: "30s",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<5000"], // CORREGIDO: usar p(95) en lugar de p95
  },
};

export function smokeTest() {
  sendRequest(basic_image, "text.jpg");
}

export function loadTest() {
  sendRequest(basic_image, "text.jpg");
}

export function stressTest() {
  sendRequest(basic_image, "text.jpg");
}

export function spikeTest() {
  sendRequest(basic_image, "text.jpg");
}

function sendRequest(file, filename) {
  const data = {
    file: http.file(file, filename, "image/jpeg"),
  };
  const res = http.post(`${BASE_URL}/api/text-to-braille`, data);
  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(1);
}

export function handleSummary(data) {
  return {
    "/results/resumen_text_detect.html": htmlReport(data, { debug: false }),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
