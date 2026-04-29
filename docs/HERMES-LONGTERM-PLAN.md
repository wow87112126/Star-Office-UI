# Star Office UI 长期维护与 Hermes 协同规则

## 项目身份
本项目是一个长期项目，以下关键词默认指向它：
- 宠物
- 桌面宠物
- 宠物办公场景
- 像素办公室
- 办公室看板
- Star Office
- Star Office UI

项目根目录：`C:\Users\Administrator\.openclaw\workspace\Star-Office-UI`

---

## 长期维护原则
1. 这是长期演进项目，不按一次性脚本处理。
2. 每次维护、修改、迭代、升级，都先做最小范围诊断，再做变更。
3. 每次变更尽量同步留下：
   - 用户说明
   - 开发说明
   - 变更记录
4. 优先能力收敛，不做无限制扩张。
5. 对“桌面宠物”“多 Agent 办公室”“装修/生图”“三语文案”四条主线分别管理。

---

## Hermes 协同规则
未来当这个项目触发以下需求时，应优先调用 Hermes 体系来处理：
- 维护
- 修改
- 迭代
- 升级
- 结构梳理
- 自动化
- 多 Agent 协作
- 状态同步

### 使用原则
1. 先检查项目当前状态：
   - 服务是否可用
   - 哪个模块受影响
   - 是否涉及前端 / 后端 / 资产 / 桌面宠物
2. 再让 Hermes 处理对应问题，并尽量利用 Hermes 的：
   - 状态同步
   - 会话检索/长期记忆
   - 多 Agent 协作能力
   - 自动演进式项目整理能力
3. 每次处理后沉淀到：
   - `PROJECT-INDEX.md`
   - `docs/`
   - 必要时更新长期记忆
4. Hermes 与 OpenClaw 的项目上下文互通，统一参考：
   - `docs/HERMES-OPENCLAW-CONTEXT-BRIDGE.md`
   - `docs/DEPLOY-SOP.md`
   - `docs/REALTIME-BRIDGE-PLAN.md`

---

## 维护触发路由
### A. 前端相关
关键词：界面、场景、气泡、像素办公室、布局、三语、移动端
优先检查：
- `frontend/`
- `assets/`
- `docs/`

### B. 后端相关
关键词：状态、接口、agent、join key、鉴权、安全、配置
优先检查：
- `backend/app.py`
- `backend/requirements.txt`
- `office-agent-push.py`
- `join-keys*.json`

### C. 桌面宠物相关
关键词：桌面宠物、透明窗口、桌面版、壳层
优先检查：
- `desktop-pet/`

### D. 装修/生图相关
关键词：装修、搬新家、背景、生图、Gemini、资产替换
优先检查：
- `scripts/`
- `assets/`
- `runtime-config*`
- Gemini 相关配置

---

## 版本化建议
长期建议补齐这些文件：
- `docs/DEPLOYMENT.md`
- `docs/API.md`
- `docs/ASSET-GUIDE.md`
- `docs/I18N.md`
- `docs/ITERATION-LOG.md`
- `docs/IDEAS.md`
- `docs/PUBLIC-DEPLOY-CHECKLIST.md`
- `docs/HERMES-OPENCLAW-CONTEXT-BRIDGE.md`

---

## 安全原则
1. 不直接把开发态 Flask 裸露到公网。
2. 公网部署优先：域名 + HTTPS + 反向代理 + 最小暴露面。
3. 强制关注：
   - `ASSET_DRAWER_PASS`
   - `FLASK_SECRET_KEY`
   - 安全组端口
   - 访问控制
4. 若只给主人自己使用，优先增加额外访问保护。

---

## 执行口径
以后只要主人提到这个项目相关需求，默认按“长期项目维护”模式处理，而不是把它当成一次性 demo。

