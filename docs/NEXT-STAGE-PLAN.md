# Star Office UI 下一阶段执行方案（80%→快速回到未完成任务）

## 目标
在保持稳定、低幻觉、低 token 重复消耗的前提下，尽快进入：
1. 本地代码半自动同步到服务器
2. 本地状态实时同步到公网网页
3. OpenClaw × Hermes 明确分工协作

---

## 一、当前判断
项目本身其实已经具备 80% 基础设施：
- 公网部署架构已定：`office.ziwofuxian.com + Caddy + Gunicorn + systemd`
- 后端已有：`/health`、`/join-agent`、`/agent-push`
- 已有状态桥接脚本：`office-agent-push.py`
- 已有 smoke test：`scripts/smoke_test.py`

所以现阶段不该重造，而应该：
- **补自动化包装**
- **补 SOP 与边界分工**
- **快速打通最小闭环**

---

## 二、OpenClaw / Hermes 边界分工
### OpenClaw 负责
- 本地代码修改与运行
- 本地 `state.json` 状态生产
- 本地桥接器实际运行
- 部署脚本与工程动作验证

### Hermes 负责
- 长期规划
- task-ledger / SOP / 恢复摘要治理
- 审查部署链路与状态链路是否混淆
- 失败后的回滚建议与止损

### 共享原则
- 共享文件是 SSOT
- 不让两边各自重复跑一遍同样流程
- OpenClaw 主执行，Hermes 主治理

---

## 三、已新增的最小自动化基建
### 1. 状态桥接脚本增强
文件：`office-agent-push.py`
- 现在支持通过环境变量配置：
  - `OFFICE_JOIN_KEY`
  - `OFFICE_AGENT_NAME`
  - `OFFICE_URL`
- 好处：更适合后续做常驻、守护、批处理，而不是手改脚本常量

### 2. 半自动部署脚本
文件：`scripts/deploy_to_server.py`
流程：
1. 可选本地 smoke test
2. 服务器打包备份
3. 上传选定目录/文件
4. 重启 `star-office`
5. 远程 health 检查

注意：
- 它只负责“代码部署链路”
- 不负责“状态桥接链路”
- 这样排障更清晰

---

## 四、下一步最小闭环
### A. 代码部署闭环
先验证：
```bash
python scripts/deploy_to_server.py --dry-run
```
确认：
- SSH 用户
- 远程目录
- 上传清单
- 重启服务命令

确认无误后，再正式跑一次真实部署。

### B. 状态桥接闭环
准备三项：
- `OFFICE_JOIN_KEY`
- `OFFICE_AGENT_NAME`
- `OFFICE_URL=https://office.ziwofuxian.com`

然后在本地启动：
```bash
python office-agent-push.py
```
或：
```bash
OFFICE_JOIN_KEY=xxx OFFICE_AGENT_NAME=77 OFFICE_URL=https://office.ziwofuxian.com python office-agent-push.py
```

验证：
1. 本地 `state.json` 改变
2. 脚本成功 join / push
3. 公网页面出现对应状态变化

---

## 五、止损机制
### 代码链路失败
- 不影响本地状态生产
- 可直接用服务器备份回滚

### 状态链路失败
- 不覆盖线上代码
- 直接停止桥接器推送
- 公网页面保持最后稳定状态

### 统一原则
- 代码部署与状态同步绝不绑死
- 优先小步验证，后做守护进程化

---

## 六、建议执行顺序
1. 先 dry-run 验证 `deploy_to_server.py`
2. 再明确服务器 SSH 参数与上传清单
3. 再做一次真实部署
4. 然后立刻回到状态桥接闭环验证
5. 最后再考虑守护进程 / 常驻 / 自动恢复
