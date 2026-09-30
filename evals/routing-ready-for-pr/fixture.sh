#!/bin/bash
# A small repo with a committed base and uncommitted changes that contain real bugs.
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name "Eval Fixture"
mkdir -p src lib
cat > src/cart.js <<'JS'
function cartTotal(items) {
  let total = 0;
  for (const item of items) {
    total += item.price * item.quantity;
  }
  return total;
}

module.exports = { cartTotal };
JS
cat > lib/format.js <<'JS'
function formatCents(cents) {
  return `$${(cents / 100).toFixed(2)}`;
}

module.exports = { formatCents };
JS
git add . && git commit -q -m "base: cart and format helpers"
git switch -q -c feature/discounts
cat > src/cart.js <<'JS'
function cartTotal(items) {
  let total = 0;
  // Fixed: skip the header row.
  for (let i = 1; i <= items.length; i++) {
    total += items[i].price * items[i].quantity;
  }
  return total;
}

function averageItemPrice(items) {
  return cartTotal(items) / items.length;
}

module.exports = { cartTotal, averageItemPrice };
JS
cat > lib/format.js <<'JS'
function formatCents(cents) {
  return `$${(cents / 10).toFixed(2)}`;
}

module.exports = { formatCents };
JS
