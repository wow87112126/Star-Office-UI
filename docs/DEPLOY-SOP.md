# Star Office UI 部署与同步 SOP（长期维护版）

## 当前线上部署信息
- 公网地址：`https://office.ziwofuxian.com`
- 服务器：`118.31.239.172`
- 系统：Ubuntu 24.04 64-bit
- 线上项目目录：`/home/ecs-user/Star-Office-UI`
- 本地项目目录：`C:\Users\Administrator\.openclaw\workspace\Star-Office-UI`
- systemd 服务名：`star-office`
- Caddy 配置：`/etc/caddy/Caddyfile`
- 本机后端监听：`127.0.0.1:19000`

---

## 一、当前架构与限制
当前公网线上站点跑的是**服务器上的 Star Office UI 副本**，而不是 Windows 本地工作区里的实时进程。

所以现在默认行为是：
- 本地改代码 ≠ 线上立即变化
- 本地 OpenClaw 状态 ≠ 自动实时同步到线上

这是正常现象，不是 bug，而是部署架构决定的。

---

## 二、为什么现在还不能自动同步本地实时状态
Star Office UI 的“宠物动作 / 工作状态实时变化”，本质依赖的是**状态写入源**。

当前本地模式之所以能实时变化，是因为：
1. OpenClaw / 本地助手运行时会写 `state.json`
2. 本地 Star Office UI 读到这个 `state.json`
3. 页面因此发生实时变化

但现在公网线上部署在另一台服务器上：
- 它读的是服务器自己的 `state.json`
- 不是你 Windows 本地的 `state.json`

所以如果没有额外的“状态桥接 / 推送机制”，线上页面当然不会同步你本地运行状态。

---

## 三、长期正确方向：代码部署 与 状态同步 分离
后续应把这件事拆成两条链路：

### A. 代码部署链路
负责“页面、功能、资源、逻辑”的上线更新：
- 本地修改代码
- 同步文件到服务器
- 重启 `star-office`
- 浏览器验证

### B. 状态同步链路
负责“宠物动作 / OpenClaw 工作状态 / 实时状态气泡”的持续同步：
- 本地 OpenClaw 运行时写入状态
- 一个状态推送器把状态发到服务器上的 Star Office UI
- 线上页面实时刷新显示

这两条链路要分开设计，不能混在一起。

---

## 四、一步到位的目标方案（后续推荐）
目标不是让服务器直接跑你的 Windows 本地 OpenClaw，而是：

### 推荐最终形态
**本地 OpenClaw（真实工作现场）**
→ 写本地状态
→ 状态桥接器 / push agent
→ 公网 Star Office UI 服务器
→ 实时展示宠物状态

这样既能：
- 保留公网稳定站点
- 又能同步你本地真实运行状态
- 还不需要把本地 OpenClaw 整体暴露到公网

---

## 五、可选实现路线
### 方案 1：用项目自带 push 机制（优先推荐）
仓库自带：
- `office-agent-push.py`
- `/join-agent`
- `/agent-push`

这说明它天然支持“外部 agent 把状态推送到一个中心办公室”。

后续可以把你的本地 OpenClaw 视为一个 agent：
1. 本地生成 / 更新状态
2. 本地运行 push 脚本
3. 把状态持续推送到公网 `office.ziwofuxian.com`
4. 线上页面就实时显示动作变化

### 方案 2：直接把本地 `state.json` 做远程同步
例如定时把本地 `state.json` 推送到服务器。

优点：
- 实现简单

缺点：
- 不够优雅
- 容易状态抖动
- 对多 agent、多来源扩展不好

### 方案 3：让 Hermes 统一接管状态桥接
后续可把“本地状态采集 + 推送 + 故障恢复 + 迭代优化”交给 Hermes 作为长期项目能力建设的一部分。

这也是长期最值得做的方向。

---

## 六、当前推荐执行顺序
### 第 1 阶段（已完成）
- 公网站点安全上线
- HTTPS / Caddy / systemd / 本机监听 / 备份完成

### 第 2 阶段（下一步要做）
- 设计并落地“本地 OpenClaw 状态 → 公网 Star Office UI”的桥接方案
- 目标是让宠物动作重新实时同步

### 第 3 阶段（长期）
- 所有维护、修改、升级默认进入 Hermes 协同模式
- 沉淀 SOP、部署脚本、状态同步守护脚本、回滚策略

---

## 七、当前线上维护 SOP（代码层）
1. 本地修改：`C:\Users\Administrator\.openclaw\workspace\Star-Office-UI`
2. 确认改动文件清单
3. 服务器备份对应文件
4. 上传覆盖到：`/home/ecs-user/Star-Office-UI`
5. 重启服务：
   ```bash
   sudo systemctl restart star-office
   ```
6. 检查状态：
   ```bash
   sudo systemctl status star-office --no-pager
   curl http://127.0.0.1:19000/health
   ```
7. 浏览器验收：
   - `https://office.ziwofuxian.com`

---

## 八、回滚 SOP
### 单文件回滚
```bash
cp /home/ecs-user/Star-Office-UI/路径/文件.bak /home/ecs-user/Star-Office-UI/路径/文件
sudo systemctl restart star-office
```

### 整站回滚
使用已打包备份：
- `~/star-office-backup-*.tar.gz`

先停服务，再恢复目录，再启动服务。

---

## 九、Hermes 长期维护约定
后续这个项目进入：
- 维护
- 修改
- 迭代
- 升级
- 同步机制改造
- 状态桥接
- 自动化

都默认：
1. 先进入 Star Office UI 项目上下文
2. 优先用 Hermes 协同思路规划与推进
3. 优先沉淀为可复用机制，而不是一次性修补

---

## 十、下一步最重要的问题
当前最值得优先解决的不是网页部署本身，而是：

**如何让本地 OpenClaw 的实时状态，安全地同步到公网 Star Office UI。**

这将决定“宠物动作是否真的像本地一样实时联动”。
