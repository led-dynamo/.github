#!/usr/bin/env node
import assert from 'node:assert/strict';
import { analyzeSource, formatReport } from './require-send.mjs';

const cases = [
  {
    name: 'rust reports an undelivered chain',
    language: 'rust',
    source: 'fn f(logger: Logger) { logger.info("hello"); }',
    count: 1,
  },
  {
    name: 'rust accepts an inline send',
    language: 'rust',
    source: 'fn f(logger: Logger) { logger.info("hello").send(); }',
    count: 0,
  },
  {
    name: 'rust accepts an assigned event delivered later',
    language: 'rust',
    source: 'fn f(logger: Logger) { let event = logger.info("hello"); event.send(); }',
    count: 0,
  },
  {
    name: 'rust ignores comment and string lookalikes',
    language: 'rust',
    source: 'fn f() { // logger.info("comment")\n let s = "logger.info(\\"string\\")"; println!("{}", s); }',
    count: 0,
  },
  {
    name: 'next-line suppression is honored',
    language: 'rust',
    source: 'fn f(logger: Logger) {\n// ores-lint-disable-next-line require-send\nlogger.info("hello");\n}',
    count: 0,
  },
  {
    name: 'file suppression is honored',
    language: 'dart',
    source: '// ores-lint-disable-file require-send\nvoid f(Logger logger) { logger.warn("hello"); }',
    count: 0,
  },
  {
    name: 'dart reports an undelivered chain',
    language: 'dart',
    source: 'void f(Logger logger) { logger.error("hello"); }',
    count: 1,
  },
  {
    name: 'dart accepts an inline send',
    language: 'dart',
    source: 'void f(Logger logger) { logger.error("hello").send(); }',
    count: 0,
  },
  {
    name: 'multi-argument convenience log is already terminal',
    language: 'dart',
    source: 'void f(Logger logger) { logger.log(level, "hello", context); }',
    count: 0,
  },
  {
    name: 'gleam reports an undelivered non-tail logging call',
    language: 'gleam',
    source: 'pub fn f() { logging.info("hello")\n Nil }',
    count: 1,
  },
  {
    name: 'gleam accepts a tail handoff',
    language: 'gleam',
    source: 'pub fn f() { logging.info("hello") }',
    count: 0,
  },
  {
    name: 'gleam accepts an inline send pipeline',
    language: 'gleam',
    source: 'pub fn f() { logging.info("hello") |> logging.send }',
    count: 0,
  },
  {
    name: 'gleam accepts an assigned event delivered by function call',
    language: 'gleam',
    source: 'pub fn f() { let event = logging.info("hello")\n logging.send(event) }',
    count: 0,
  },
  {
    name: 'gleam accepts an assigned event delivered by pipeline',
    language: 'gleam',
    source: 'pub fn f() { let event = logging.info("hello")\n event |> logging.send }',
    count: 0,
  },
];

let failures = 0;
for (const test of cases) {
  const findings = analyzeSource(test.source, test.language);
  try {
    assert.equal(findings.length, test.count, `${test.name}: ${JSON.stringify(findings)}`);
    process.stdout.write(`ok - ${test.name}\n`);
  } catch (error) {
    failures += 1;
    process.stderr.write(`FAIL - ${error.message}\n`);
  }
}

const report = formatReport([{ file: 'fixture.rs', findings: analyzeSource('fn f(logger: Logger) { logger.info("hello"); }', 'rust') }]);
try {
  assert.match(report, /1 finding\(s\) across 1 rule\(s\)/);
  assert.match(report, /fixture\.rs:1:/);
  process.stdout.write('ok - report format remains machine-greppable\n');
} catch (error) {
  failures += 1;
  process.stderr.write(`FAIL - ${error.message}\n`);
}

if (failures) {
  process.stderr.write(`require-send self-test FAILED: ${failures} case(s)\n`);
  process.exit(1);
}
process.stdout.write(`require-send self-test passed: ${cases.length + 1} assertions\n`);
