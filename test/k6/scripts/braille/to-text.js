import http from "k6/http";
import { check, sleep } from "k6";
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

const BASE_URL = `http://${__ENV.HOST || "localhost"}:${__ENV.PORT || 8080}`;

const basic_image = open("/scripts/assets/braille_basic.jpg", "b");
const length_image = open("/scripts/assets/braille_lenght.jpg", "b");
const weight_image = open("/scripts/assets/braille_weight.jpg", "b");

export const options = {
  scenarios: {
    smokeTest: {
      executor: "constant-vus",
      vus: 1,
      duration: "5s",
      exec: "smokeTest",
    },
    loadTest: {
      executor: "constant-vus",
      vus: 5,
      duration: "15s",
      exec: "loadTest",
    },
    stressTest: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "10s", target: 10 },
        { duration: "10s", target: 20 },
        { duration: "10s", target: 5 },
      ],
      exec: "stressTest",
    },
    spikeTest: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "5s", target: 20 },
        { duration: "10s", target: 1 },
      ],
      exec: "spikeTest",
    },
  },
};

export function smokeTest() {
  sendRequest([basic_image], ["braille_basic.jpg"]);
}

export function loadTest() {
  sendRequest([length_image], ["braille_lenght.jpg"]);
}

export function stressTest() {
  sendRequest([weight_image], ["braille_weight.jpg"]);
}

export function spikeTest() {
  sendRequest(
    [basic_image, length_image, weight_image],
    ["braille_basic.jpg", "braille_lenght.jpg", "braille_weight.jpg"]
  );
}

function sendRequest(files, filenames) {
  const data = {};

  files.forEach((f, i) => {
    data[`files${i === 0 ? "" : i}`] = http.file(f, filenames[i], "image/jpeg");
  });

  const res = http.post(`${BASE_URL}/api/braille-to-text/text`, data);

  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(1);
}

export function handleSummary(data) {
  return {
    "/results/braille_test.html": htmlReport(data, { debug: false }),
    stdout: textSummary(data, { indent: " ", enableColors: true }),
  };
}
