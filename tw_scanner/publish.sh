#!/usr/bin/env bash
# publish.sh — tw_scanner 家族共用的「commit + push」步驟（tw_scanner / delta_radar / tsmc_radar 三個 workflow 共用）
#
# 為什麼存在（2026-09-12 tsmc-radar run #1 attempt 2 實測）：
#   三個 workflow 都會重寫同一批「衍生檔」（tw_scanner/README.md、output/tw_brief.json、output/tw_weekly.md）。
#   舊做法 `git pull --rebase --autostash` 把本地衍生檔 stash 再套回 → 只要 main 在跑的期間前進，就衝突、exit 128。
#   衍生檔是 state 的純函數（零網路），正確做法是：先 commit 自己的主輸出 → pull --rebase → **重新產生衍生檔** → 併入同一個
#   commit → push；push 被搶先就重來。
#
# 用法：tw_scanner/publish.sh "<bot 名>" "<commit 訊息>" <主輸出檔...>
#   主輸出檔 = 這個 workflow 自己產生、別的 workflow 不會動的檔（state/report/快取）；缺任一個 → 失敗（不用 || true 吞）。
#   衍生檔固定：tw_scanner/README.md、output/tw_brief.json、output/tw_weekly.md（由本腳本重新產生，不必列）。
# 例外：re-run 一個舊 attempt 時，main 可能已經有這次的主輸出 → rebase 在主輸出衝突 → 放棄本次 commit，印 ::warning，exit 0
#   （資料已在 main，不是雷達的錯；請用 Run workflow 新發，不要 re-run 舊 attempt）。
set -euo pipefail

BOT="${1:?bot name}"; MSG="${2:?commit message}"; shift 2
PRIMARY=("$@")
DERIVED=(tw_scanner/README.md tw_scanner/output/tw_brief.json tw_scanner/output/tw_weekly.md)

regen_derived() {
  python tw_scanner/tw_brief.py --output-dir tw_scanner/output >/dev/null
  python tw_scanner/build_readme.py >/dev/null
}

git config user.name "$BOT"
git config user.email "actions@users.noreply.github.com"

# 1) 主輸出：顯式存在性檢查，缺就 fail loudly
for f in "${PRIMARY[@]}"; do
  if [ -f "$f" ]; then git add "$f"; else echo "::error::expected output missing: $f"; exit 1; fi
done
# 衍生檔先不進 stage：等 pull 之後重新產生（避免與別的 workflow 剛 commit 的版本衝突）
git checkout -- "${DERIVED[@]}" 2>/dev/null || true
if git diff --cached --quiet; then
  echo "主輸出無變化（休市／狀態未變）；仍重組衍生檔看有沒有東西要 commit"
fi
regen_derived
git add "${DERIVED[@]}"
if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi
git commit -q -m "$MSG"

# 2) pull --rebase；衍生檔衝突 → 用「我們重產生」解；主輸出衝突 → 舊 attempt，放棄
for attempt in 1 2 3; do
  if git pull --rebase --quiet origin main; then
    :
  else
    conflicted=$(git diff --name-only --diff-filter=U || true)
    primary_conflict=0
    for f in $conflicted; do
      case " ${DERIVED[*]} " in *" $f "*) ;; *) primary_conflict=1 ;; esac
    done
    if [ "$primary_conflict" = "1" ]; then
      echo "::warning::主輸出與 main 衝突（多半是 re-run 舊 attempt，main 已有本次輸出）：$conflicted → 放棄本次 commit"
      git rebase --abort || true
      exit 0
    fi
    # 只有衍生檔衝突：衝突當下工作樹已是「main 的 state ＋ 本次主輸出」→ 直接重產生衍生檔當作解法，繼續 rebase
    regen_derived
    git add "${DERIVED[@]}"
    GIT_EDITOR=true git rebase --continue
  fi
  # rebase 完的 main 可能有別人的 state 更新 → 衍生檔重產生，併進本 commit
  regen_derived
  git add "${DERIVED[@]}"
  if ! git diff --cached --quiet; then
    git commit -q --amend --no-edit
  fi
  if git push origin HEAD:main; then
    echo "pushed (attempt $attempt)"
    exit 0
  fi
  echo "push rejected (attempt $attempt)，重新 pull"
  sleep $((attempt * 5))
done
echo "::error::push failed after 3 attempts"
exit 1
