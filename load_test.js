import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Normal Load: 20 kullanıcıya çık ve 30s bekle
    { duration: '30s', target: 50 },  // Peak Load: 50 kullanıcıya çık ve 30s bekle
    { duration: '30s', target: 100 }, // Stress Load: 100 kullanıcıya çık ve 30s bekle
    { duration: '10s', target: 0 },
  ],
};

const BASE_URL = 'http://127.0.0.1:5000/api/v1'; // simdilik yerelde test

export default function () {
  // 1. Endpoint Testi: Uçuş Sorgulama (Query Flight)
    let queryRes = http.get(`${BASE_URL}/flights?date-from=2026-05-01&date-to=2026-05-02&airport-from=IST&airport-to=ESB&number-of-people=1&one-way=true`);
  check(queryRes, {
    'query status is 200': (r) => r.status === 200,
  });

  sleep(1); // Gerçekçi kullanıcı davranışı için kısa bir bekleme

  // 2. Endpoint Testi: Yolcu Listesi (Auth gerektiren bir endpoint)
  // Not: Token almadığımız için 401 dönecektir, bu da bir test sonucudur!
  let passengerRes = http.get(`${BASE_URL}/flights/passengers?flight_number=TK101&date=2026-05-01&page=1`);
  check(passengerRes, {
    'auth check performed': (r) => r.status === 401 || r.status === 200,
  });

  sleep(1);
}