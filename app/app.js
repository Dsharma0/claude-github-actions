// Tiny app used as the practice target for CI/CD workflows.
function add(a, b) {
  return a + b;
}

function greet(name) {
  return `Hello, ${name}!`;
}

module.exports = { add, greet };
