# Star Office UI 阿里云公网部署建议（ziwofuxian.com）

## 当前已知信息
- 主域名：`ziwofuxian.com`
- 服务器公网 IP：`118.31.239.172`
- 系统：Ubuntu 24.04 64-bit
- DNS 托管：`dns1.hichina.com` / `dns2.hichina.com`
- 访问目标：公开访问

## 推荐方案
**推荐：Caddy + Gunicorn + systemd + 子域名**

推荐子域名：
- `office.ziwofuxian.com`
- 或 `pet.ziwofuxian.com`

不建议直接把根域名 `ziwofuxian.com` 用在这个项目上，除非你确认它不会给别的站点使用。

### 为什么推荐这套
1. **比直接 Flask 开发服务安全得多**
2. **比 Docker 更省维护成本**（当前项目先不必引入额外容器复杂度）
3. **比临时 Tunnel 更适合长期公开访问**
4. **Caddy 自动处理 HTTPS 证书与续期**，后期维护轻松
5. **Gunicorn + systemd** 更适合 Ubuntu 生产运行

## 目标架构
Internet
→ `office.ziwofuxian.com:443`
→ Caddy
→ `127.0.0.1:19000`
→ Gunicorn
→ Star Office UI

## 安全要求
1. **不要直接暴露 Flask dev server 到公网**
2. **19000 端口不要对公网开放**
3. **安全组只保留：22 / 80 / 443**
4. **ASSET_DRAWER_PASS 必须改强密码**
5. **FLASK_SECRET_KEY 必须改成高强度随机值**
6. **应用监听 127.0.0.1，不监听公网 IP**
7. **建议开启 UFW 与 Fail2ban**

## 阿里云侧要做的事
### 1. DNS 解析
在阿里云云解析里新增：
- 主机记录：`office`
- 记录类型：`A`
- 记录值：`118.31.239.172`

### 2. 安全组
入方向只保留：
- `22/tcp`
- `80/tcp`
- `443/tcp`

如果有 `19000/tcp` 对公网开放，必须关闭。

## 服务器侧部署目标
1. 安装：`python3-pip python3-venv caddy`
2. 项目建立虚拟环境
3. 用 Gunicorn 启动 Flask app
4. 用 systemd 守护 Gunicorn
5. 用 Caddy 反代并自动签发 HTTPS
6. 用环境变量配置生产安全项

## 生产环境变量建议
- `FLASK_SECRET_KEY=<高强度随机值>`
- `ASSET_DRAWER_PASS=<高强度随机值>`
- `STAR_BACKEND_PORT=19000`

## 下一步
等确认以下两点后即可进入正式部署：
1. 你接受使用子域名（推荐 `office.ziwofuxian.com`）
2. 你确认会关闭公网暴露的 `19000`
