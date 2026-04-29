# Hermes ↔ OpenClaw 项目上下文桥（Star Office UI）

## 目的
避免 Windows 本地 OpenClaw 会话 与 WSL 内 Hermes 会话在处理 Star Office UI（宠物 / 宠物办公场景 / 像素办公室）时因为上下文割裂而产生信息缺失、重复判断或幻觉。

---

## 一、统一源头（Single Source of Truth）
以后这个项目的长期事实，统一优先沉淀到以下文件：

### 项目级文档（首选）
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\PROJECT-INDEX.md`
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\docs\DEPLOY-SOP.md`
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\docs\REALTIME-BRIDGE-PLAN.md`
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\docs\HERMES-LONGTERM-PLAN.md`
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\docs\ALIYUN-DEPLOY-RECOMMENDATION.md`
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\docs\PUBLIC-DEPLOY-CHECKLIST.md`

### 记忆级文档（辅助）
- `C:\Users\Administrator\.openclaw\workspace\memory\2026-04-28.md`
- `C:\Users\Administrator\.openclaw\workspace\MEMORY.md`

原则：
1. 项目事实优先写入项目目录 docs。
2. 跨会话长期偏好与约定，再写入 memory / MEMORY。
3. Hermes 与 OpenClaw 后续都优先读取这些文件，而不是依赖短聊天上下文。

---

## 二、Hermes 与 OpenClaw 如何互通
### 现实情况
- OpenClaw 当前主工作区：`C:\Users\Administrator\.openclaw\workspace`
- Hermes 运行在 WSL Ubuntu 中，但可直接访问：
  - `/mnt/c/Users/Administrator/.openclaw/workspace`

这意味着：
- **最优策略不是做复杂数据库同步**
- 而是把共享上下文沉淀到工作区文件里，让两边读取同一份事实源

### 统一读取路径
Hermes 处理该项目时，默认读取：
- `/mnt/c/Users/Administrator/.openclaw/workspace/Star-Office-UI/PROJECT-INDEX.md`
- `/mnt/c/Users/Administrator/.openclaw/workspace/Star-Office-UI/docs/*.md`

OpenClaw 本地会话处理该项目时，默认读取：
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\PROJECT-INDEX.md`
- `C:\Users\Administrator\.openclaw\workspace\Star-Office-UI\docs\*.md`

本质上读的是同一套文件，只是路径表示不同。

---

## 三、后续协同规则
### 1. 项目触发词
以下词默认进入该项目上下文：
- 宠物
- 桌面宠物
- 宠物办公场景
- 像素办公室
- Star Office
- Star Office UI

### 2. 处理顺序
无论是 Hermes 还是 OpenClaw，处理该项目时默认顺序：
1. 看 `PROJECT-INDEX.md`
2. 看 `docs/DEPLOY-SOP.md`
3. 看 `docs/REALTIME-BRIDGE-PLAN.md`
4. 再看本次涉及模块文档
5. 再动代码或配置

### 3. 变更沉淀
每次重要改动后，至少补其中一项：
- docs 中的部署/桥接/SOP/设计文档
- memory 当日记录
- 必要时更新长期记忆

---

## 四、关于“飞书远程指令 → 本地继续工作 → 宠物同步状态”
这个能力拆成三层：
1. 飞书 bot 接收主人远程任务
2. Hermes / OpenClaw 主工作流继续执行
3. Star Office UI 展示实时状态

后续重点不是重复部署网站，而是补齐：
- 本地状态采集
- 状态桥接推送
- 守护进程化
- 故障恢复

---

## 五、当前已确认事实
1. 公网站点已上线：`https://office.ziwofuxian.com`
2. Caddy + Gunicorn + systemd 已可用
3. 服务仅监听 `127.0.0.1:19000`
4. 当前线上项目是服务器副本，不会自动同步本地代码或本地状态
5. 后续采用：
   - 代码同步：方案 A（本地改 → 同步到服务器 → 重启服务）
   - 状态同步：后续补桥接器（本地状态 → 公网办公室）
6. 该项目以后默认由 Hermes 协同长期维护

---

## 六、执行口径
以后只要主人提到该项目相关维护、修改、迭代、升级：
- 默认先检查这些共享文档
- 默认把它视为长期项目
- 默认优先让 Hermes 参与处理与沉淀
