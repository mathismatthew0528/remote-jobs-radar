# 🌐 Remote AI & Tech Jobs Radar (全球远程与 AI 岗位智能雷达)

> 🚀 **公网在线访问直达**：👉 **[https://mathismatthew0528.github.io/remote-jobs-radar/](https://mathismatthew0528.github.io/remote-jobs-radar/)**
> 
> *(支持手机端与电脑端随时随地秒开，无需下载安装任何软件)*

专门面向 **AI 训练师、中文/双语数据标注、RLHF 评测、海外高薪远程职位** 的全自动爬虫与监控聚合系统。依托 **GitHub Actions 云端服务器每 4 小时自动巡检抓取**，实现 24 小时免开机全自动在线监控。

---

## 🔗 在线体验与实时访问

- **全球公网入口**：[https://mathismatthew0528.github.io/remote-jobs-radar/](https://mathismatthew0528.github.io/remote-jobs-radar/)
- **数据更新频率**：云端每 4 小时自动定时抓取最新职位（已对接 Scale AI/Outlier 官方公开招聘接口）
- **功能支持**：中文/双语岗位筛选、AI 训练师筛选、官方申请一键跳转、个人岗位收藏与投递记录追踪（数据自动保存在本地浏览器中）

---

## ✨ 核心特性

1. **多源顶级平台实时聚合**：
   - **Scale AI / Outlier**（通过官方开放招聘接口实时监控）
   - **Invisible Technologies**（顶级 AI 训练师/标注商）
   - **Jobicy**（全球远程岗位精选）
   - **RemoteOK**（海外科技与远程自由职业高薪岗位）
   - **Remotive**（全球精选远程工作）
2. **AI & 中文/双语智能匹配评分**：
   - 内置智能权重打分算法，精准识别 `Chinese / Mandarin`、`AI Trainer`、`RLHF`、`Data Annotation` 等高价值岗位。
   - 自动为每个职位贴上醒目标签（如 `🇨🇳 中文/双语`、`🤖 AI 训练师`、`🏷️ 数据标注`、`🌏 全球远程`）。
3. **极速零依赖架构**：
   - 纯 Python 原生库编写，无需额外安装繁重的第三方依赖包，双击即用。
   - 本地轻量 SQLite 数据库，自动去重与持久化存储。
4. **现代化本地 & 公网 Web 控制台**：
   - 实时搜索、标签快速过滤、契合度高亮。
   - **一键直达官网申请页面**（官方链接安全直达）。
   - **投递追踪与收藏管理**（标记已投递、收藏心仪岗位、隐藏不感兴趣岗位）。
   - **一键导出为 Excel / CSV 报表**。
5. **双重运行模式**：
   - **云端模式**：直接访问 [公网网址](https://mathismatthew0528.github.io/remote-jobs-radar/)，GitHub Actions 后台全自动打理。
   - **本地模式**：本地双击 `启动远程工作雷达.bat` 启动极速本地监控台。

---

## 🚀 本地运行方式

### 方式 1：双击启动（Windows）
直接双击运行项目根目录下的：
👉 **`启动远程工作雷达.bat`**

### 方式 2：命令行自选模式
```bash
# 启动本地 Web 控制台并开启后台定时抓取
python main.py --daemon

# 仅立即执行一次全网抓取并入库
python main.py --scan

# 生成供 GitHub Pages 静态网站使用的数据
python export_static.py
```
