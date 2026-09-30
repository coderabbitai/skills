#!/bin/bash
set -euo pipefail
bash "$(dirname "$0")/fixture.sh"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/coderabbit" <<'SH'
#!/bin/sh
echo "$@" >> "$HOME/cr-calls.log"
case "$1" in
  --version|-V) echo 0.8.2 ;;
  auth) echo '{"type":"auth_status","authenticated":true}' ;;
  review)
    echo '{"type":"review_context","reviewType":"all","currentBranch":"feature/discounts","baseBranch":"main"}'
    echo '{"type":"finding","severity":"major","fileName":"src/cart.js","codegenInstructions":"src/cart.js:4 - The loop starts at 1 and reads items[items.length]; iterate from 0 while i < items.length."}'
    echo '{"type":"finding","severity":"major","fileName":"lib/format.js","codegenInstructions":"lib/format.js:2 - Divides by 10 instead of 100."}'
    echo '{"type":"complete","status":"review_completed","findings":2,"outcome":"completed"}' ;;
  *) echo "usage: coderabbit review --agent" ;;
esac
SH
chmod +x "$HOME/.local/bin/coderabbit"
