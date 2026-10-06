const test = require("node:test");
const assert = require("node:assert");
const { add, greet } = require("./app");

test("add", () => assert.strictEqual(add(2, 3), 5));
test("greet", () => assert.strictEqual(greet("Ada"), "Hello, Ada!"));
