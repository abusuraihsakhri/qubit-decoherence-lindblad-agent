"use strict";
const assert = require("node:assert/strict");
const { simulate } = require("../web/app.js");

function close(actual, expected, tolerance = 1e-10) {
  assert.ok(Math.abs(actual - expected) <= tolerance, `Expected ${actual} ~= ${expected}`);
}

const samples = simulate({
  t1:30, t2:20, duration:20, steps:2,
  theta:Math.PI/2, phi:0, omega:0
});
close(samples[0].p_excited, 0.5);
close(samples[0].coherence_abs, 0.5);
close(samples[0].purity, 1);
close(samples[1].p_excited, 0.5 * Math.exp(-20/30));
close(samples[1].coherence_abs, 0.5 * Math.exp(-1));
assert.ok(samples.every(row => row.purity >= 0.5 && row.purity <= 1.0000000001));

const phase = simulate({
  t1:10, t2:20, duration:250, steps:3,
  theta:Math.PI/2, phi:Math.PI/2, omega:0
});
close(phase[0].x, 0);
close(phase[0].y, 1);
assert.ok(phase[2].p_excited < 1e-9);
close(phase[2].purity, 1, 1e-8);

for (const invalid of [
  {t1:1,t2:2.1,duration:5,steps:5,theta:0,phi:0,omega:0},
  {t1:0,t2:1,duration:5,steps:5,theta:0,phi:0,omega:0},
  {t1:1,t2:1,duration:5,steps:1,theta:0,phi:0,omega:0},
  {t1:1,t2:1,duration:5,steps:5,theta:4,phi:0,omega:0},
]) {
  assert.throws(() => simulate(invalid), Error);
}
console.log("JavaScript physics regression checks passed");
