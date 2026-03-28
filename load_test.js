import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Normal Load: 20 sanal kullanıcı (VU)
    { duration: '30s', target: 50 },  // Peak Load: 50 sanal kullanıcı (VU)
    { duration: '30s', target: 100 }, // Stress Load: 100 sanal kullanıcı (VU)
    { duration: '10s', target: 0 },   // Recovery: 0 sanal kullanıcı (VU)
  ],
};

const BASE_URL = 'https://sila-api-air-gsh6hgdxgwcedub0.francecentral-01.azurewebsites.net/api/v1';

export default function () {
  // 1. Endpoint: Uçuş Sorgulama
  let queryRes = http.get(`${BASE_URL}/flights/query?date_from=2026-05-01T08:00:00&airport_from=IST&airport_to=ESB&number_of_people=1`);
  check(queryRes, {
    'query endpoint is responding': (r) => r.status === 200 || r.status === 400 || r.status === 404,
  });

  sleep(1);

  // 2. Endpoint: Yolcu Listesi Sorgulama
  let passengerRes = http.get(`${BASE_URL}/flights/passengers?flight_number=TK101&date=2026-05-01&page=1`);
  check(passengerRes, {
    'auth endpoint is responding': (r) => r.status === 401 || r.status === 200,
  });

  sleep(1);
}