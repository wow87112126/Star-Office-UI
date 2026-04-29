# Star Office UI 项目索引

## 项目别名
以下关键词默认指向本项目：
- 宠物
- 桌面宠物
- 宠物办公场景
- 像素办公室
- 办公室看板
- Star Office
- Star Office UI

## 目标
这是一个像素风 AI 办公室 / 宠物办公场景项目，用来可视化 AI 助手状态、支持多 Agent 协作、三语切换、资产替换、可选 AI 生图装修、以及可选 Electron 桌面宠物模式。

## 本地路径
- 项目根目录：`C:\Users\Administrator\.openclaw\workspace\Star-Office-UI`
- 后端入口：`backend/app.py`
- 前端目录：`frontend/`
- 桌面宠物：`desktop-pet/`
- 状态脚本：`set_state.py`
- 多 Agent 推送：`office-agent-push.py`
- 资产位置：`asset-positions.json`
- 资产默认值：`asset-defaults.json`
- 运行态配置：`runtime-config.sample.json`
- Join Key 样板：`join-keys.sample.json`
- 文档目录：`docs/`

## Hermes 长期协同规则
1. 以后只要主人提到“宠物 / 宠物办公场景 / 像素办公室 / Star Office”，默认先检查这个项目。
2. 当这个项目进入维护、修改、迭代、升级时，默认启用 Hermes 协同思路来处理，并优先沉淀可复用规则与文档。
3. 每次处理优先检查：`PROJECT-INDEX.md`、`README.md`、`docs/`、相关模块目录。
4. 每次重要变更后，尽量同步补：
   - 一份用户说明
   - 一份开发说明
   - 一份变更记录
5. 公网部署前，优先查看：`docs/PUBLIC-DEPLOY-CHECKLIST.md`
6. 长期维护策略，优先查看：`docs/HERMES-LONGTERM-PLAN.md`

## 目录职责建议
### 1. 根目录
保留“启动入口 + 项目级配置 + 高频脚本”：
- `README*.md`：面对使用者的说明
- `PROJECT-INDEX.md`：给我和主人检索时快速定位
- `state.json`：当前主 Agent 状态
- `asset-positions.json`：房间内资源摆放
- `asset-defaults.json`：默认资源选择
- `join-keys*.json`：多 Agent 加入控制
- `set_state.py` / `office-agent-push.py`：高频操作脚本

### 2. backend/
只放服务端逻辑：
- API
- 状态存储
- 资产配置写入
- 鉴权与安全逻辑
- 生图异步任务调度

后续若继续迭代，优先细分为：
- `backend/routes/`
- `backend/services/`
- `backend/store/`
- `backend/security/`
- `backend/tasks/`

### 3. frontend/
只放页面与交互：
- 场景渲染
- 多语言文案
- 资产侧栏
- 生图轮询 UI
- 移动端适配

后续建议新增：
- `frontend/assets-manifest/`：资源索引
- `frontend/i18n/`：多语言文案独立管理
- `frontend/components/`：侧栏、气泡、agent卡片等组件拆分
- `frontend/scenes/`：办公室场景相关逻辑

### 4. assets/
只放美术资源，不混逻辑文件。
建议长期按这几类整理：
- `assets/agents/`：角色与动作
- `assets/rooms/`：房间背景
- `assets/decor/`：装饰物
- `assets/ui/`：按钮、图标、面板
- `assets/generated/`：AI 生图产物
- `assets/bg-history/`：背景历史版本
- `assets/home-favorites/`：收藏背景

### 5. docs/
沉淀长期知识，避免知识只留在聊天里。建议长期维护：
- `docs/DEPLOYMENT.md`：部署说明
- `docs/ASSET-GUIDE.md`：资产替换规则
- `docs/API.md`：接口说明
- `docs/I18N.md`：三语文案规则
- `docs/ITERATION-LOG.md`：版本迭代记录
- `docs/IDEAS.md`：宠物办公场景的创意池
- `docs/PUBLIC-DEPLOY-CHECKLIST.md`：阿里云域名公网落地资料清单
- `docs/HERMES-LONGTERM-PLAN.md`：Hermes 协同维护方案

## 长期迭代规则
1. 以后只要主人提到“宠物 / 宠物办公场景 / 像素办公室 / Star Office”，默认先检查这个项目。
2. 修改前优先看：`PROJECT-INDEX.md`、`README.md`、`docs/`、相关目录。
3. 新增功能时尽量同步补：
   - 一份用户说明
   - 一份开发说明
   - 一份可检索关键词
4. 避免把所有东西都堆到根目录；新增文件优先按职责归档。
5. 与“桌面宠物模式”相关的改动，优先同步检查 `desktop-pet/`。
6. 与“多 Agent 办公室”相关的改动，优先同步检查 `office-agent-push.py`、`join-keys*.json`、`backend/app.py`。
7. 与“装修 / 生图 / 背景切换”相关的改动，优先同步检查 `scripts/`、`assets/`、`runtime-config*`、Gemini 相关配置。

## 主人后续可直接说的话
- “去宠物项目里把状态气泡改一下”
- “看看宠物办公场景的前端结构”
- “把 Star Office 的桌面宠物模式整理一下”
- “在像素办公室项目里加一个新面板”

以上都默认指向这个项目。

