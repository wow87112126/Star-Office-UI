# Star Office UI 发布检查单（OpenClaw × Hermes）

## 角色分工
- OpenClaw：执行本地改动、验证、部署、取证
- Hermes：审阅范围/风险/验收标准，监督发布前后 handoff

---

## Release Gates
### Gate 1：本地完成度（OpenClaw）
- [ ] 改动已落地
- [ ] 本地预览/功能验证通过
- [ ] 受影响文件清单已明确
- [ ] 若涉及配置/密钥/状态文件，已确认不会误入版本库

### Gate 2：审阅与风控（Hermes）
- [ ] 改动目的清晰
- [ ] 风险点已标注
- [ ] 验收标准明确
- [ ] 是否影响回滚路径已判断
- [ ] 共享 docs / memory 是否需要同步已判断

### Gate 3：版本落库（GitHub）
- [ ] 已 commit
- [ ] 已 push 到 fork
- [ ] 已记录 deploy commit
- [ ] 已记录 previous known-good commit

### Gate 4：部署许可（OpenClaw + Hermes）
- [ ] 已确认本次上线模块
- [ ] 已确认回滚路径
- [ ] 已确认服务器备份策略
- [ ] Hermes 同意进入部署阶段

---

## 部署执行单
### 部署前
- deploy commit:
- previous known-good commit:
- scope/modules:
- local verification evidence:
- rollback target:
- operator:
- reviewer:
- timestamp:

### 部署中
- [ ] 服务器备份完成
- [ ] 文件上传完成
- [ ] `star-office` 重启完成
- [ ] `/health` 检查通过
- [ ] 页面首屏可达

### 部署后（Hermes 监督）
- [ ] 服务进程健康
- [ ] 核心页面/核心流程正常
- [ ] 无新的明显报错日志
- [ ] 无静态资源版本错配
- [ ] 回滚目标仍明确可用
- [ ] 已写入部署记录

---

## 回滚最小模板
- rollback trigger:
- rollback target commit/tag:
- rollback command/path:
- data/config migration impact:
- result:

---

## 原则
1. 不从聊天记录推导版本事实，以 GitHub commit 为准。
2. 不把服务器热修当成长期真源；若发生，必须尽快回写仓库。
3. 非必要不跳过 Gate 2 和 Gate 4。
