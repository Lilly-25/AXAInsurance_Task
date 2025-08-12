/*
Performance Tests für die Titanic API mit k6.
Testet Lastverhalten und Response-Zeiten.
*/

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom Metrics
export let errorRate = new Rate('errors');
export let responseTime = new Trend('response_time');

// Test-Konfiguration
export let options = {
  stages: [
    // Ramp-up: 0 zu 10 Benutzer über 30 Sekunden
    { duration: '30s', target: 10 },
    
    // Konstante Last: 10 Benutzer für 60 Sekunden
    { duration: '60s', target: 10 },
    
    // Spitzenlast: 10 zu 50 Benutzer über 30 Sekunden  
    { duration: '30s', target: 50 },
    
    // Konstante Spitzenlast: 50 Benutzer für 60 Sekunden
    { duration: '60s', target: 50 },
    
    // Ramp-down: 50 zu 0 Benutzer über 30 Sekunden
    { duration: '30s', target: 0 },
  ],
  
  // Thresholds für Pass/Fail-Kriterien
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% der Requests unter 500ms
    http_req_failed: ['rate<0.1'],    // Weniger als 10% Fehler
    errors: ['rate<0.1'],             // Weniger als 10% Fehler
  },
};

// Basis-URL der API
const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  // Test-Scenario: Verschiedene API-Endpunkte testen
  let scenarios = [
    testHealthEndpoint,
    testPassengersEndpoint,
    testStatisticsEndpoint,
    testSurvivalByClassEndpoint,
    testFilteredPassengersEndpoint,
  ];
  
  // Zufälligen Test auswählen
  let scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
  
  // Kurze Pause zwischen Requests
  sleep(1);
}

function testHealthEndpoint() {
  let response = http.get(`${BASE_URL}/health`);
  
  let checkResult = check(response, {
    'Health endpoint status is 200': (r) => r.status === 200,
    'Health endpoint response time < 100ms': (r) => r.timings.duration < 100,
    'Health endpoint has correct status': (r) => JSON.parse(r.body).status === 'healthy',
  });
  
  errorRate.add(!checkResult);
  responseTime.add(response.timings.duration);
}

function testPassengersEndpoint() {
  let response = http.get(`${BASE_URL}/api/v1/passengers?limit=20`);
  
  let checkResult = check(response, {
    'Passengers endpoint status is 200': (r) => r.status === 200,
    'Passengers endpoint response time < 1000ms': (r) => r.timings.duration < 1000,
    'Passengers endpoint has data': (r) => {
      let body = JSON.parse(r.body);
      return body.passengers && body.passengers.length > 0;
    },
    'Passengers endpoint has correct structure': (r) => {
      let body = JSON.parse(r.body);
      return body.hasOwnProperty('total_count') && 
             body.hasOwnProperty('returned_count') &&
             body.hasOwnProperty('passengers');
    },
  });
  
  errorRate.add(!checkResult);
  responseTime.add(response.timings.duration);
}

function testStatisticsEndpoint() {
  let response = http.get(`${BASE_URL}/api/v1/passengers/statistics`);
  
  let checkResult = check(response, {
    'Statistics endpoint status is 200': (r) => r.status === 200,
    'Statistics endpoint response time < 2000ms': (r) => r.timings.duration < 2000,
    'Statistics endpoint has required fields': (r) => {
      let body = JSON.parse(r.body);
      return body.hasOwnProperty('total_passengers') &&
             body.hasOwnProperty('survival_rate') &&
             body.hasOwnProperty('average_age');
    },
  });
  
  errorRate.add(!checkResult);
  responseTime.add(response.timings.duration);
}

function testSurvivalByClassEndpoint() {
  let response = http.get(`${BASE_URL}/api/v1/passengers/survival-by-class`);
  
  let checkResult = check(response, {
    'Survival by class endpoint status is 200': (r) => r.status === 200,
    'Survival by class endpoint response time < 1500ms': (r) => r.timings.duration < 1500,
    'Survival by class endpoint has class data': (r) => {
      let body = JSON.parse(r.body);
      return body.survival_by_class && body.survival_by_class.length === 3;
    },
  });
  
  errorRate.add(!checkResult);
  responseTime.add(response.timings.duration);
}

function testFilteredPassengersEndpoint() {
  // Verschiedene Filter testen
  let filters = [
    'survived=true&limit=10',
    'pclass=1&limit=15',
    'sex=female&limit=25',
    'min_age=18&max_age=65&limit=30',
  ];
  
  let filter = filters[Math.floor(Math.random() * filters.length)];
  let response = http.get(`${BASE_URL}/api/v1/passengers?${filter}`);
  
  let checkResult = check(response, {
    'Filtered passengers endpoint status is 200': (r) => r.status === 200,
    'Filtered passengers endpoint response time < 1500ms': (r) => r.timings.duration < 1500,
    'Filtered passengers endpoint returns data': (r) => {
      let body = JSON.parse(r.body);
      return body.passengers !== undefined;
    },
  });
  
  errorRate.add(!checkResult);
  responseTime.add(response.timings.duration);
}

// Setup-Funktion
export function setup() {
  console.log('🚀 Starting performance tests for Titanic API');
  console.log(`📍 Testing URL: ${BASE_URL}`);
  
  // Health Check vor dem Start
  let response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    console.error('❌ API is not healthy, aborting tests');
    return null;
  }
  
  console.log('✅ API is healthy, starting load tests');
  return { baseUrl: BASE_URL };
}

// Teardown-Funktion
export function teardown(data) {
  console.log('🏁 Performance tests completed');
  console.log('📊 Check the results above for performance metrics');
}

/*
Wie man diesen Test ausführt:

1. k6 installieren:
   sudo apt-get install k6

2. API starten:
   docker-compose up -d

3. Test ausführen:
   k6 run load-test.js

4. Mit spezifischer URL:
   k6 run -e API_URL=http://your-api.com load-test.js

5. Test-Berichte ausgeben:
   k6 run --out json=results.json load-test.js
*/
