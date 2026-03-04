# Phase 11 验收单（对话状态“秒切”链路增强）

本阶段目标：
- 状态变化时尽快推送到办公室，不再受固定 15 秒周期限制

## 已做内容
1) `office-agent-push.py` 改为：
- 状态变化立即推送
- 心跳保活低频推送
- 最小推送间隔防抖

2) 新增可配置参数（环境变量）：
- `OFFICE_POLL_INTERVAL`（默认 0.4s）
- `OFFICE_MIN_PUSH_GAP`（默认 0.8s）
- `OFFICE_PUSH_INTERVAL`（默认 2s，心跳）

3) README 增加秒级同步说明

## 验收方式（线上可见）
- 你发消息后，状态应比旧版更快切到工作态
- 回复后应更快回 idle
- push/同步动作应更快切 syncing

## 回滚
- 代码回滚：`git revert <phase11_commit>`
