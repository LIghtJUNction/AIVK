# AIVK 前端

AIVK是一个现代化的AI交互平台，提供连接各种LLM服务的功能、插件管理、终端命令、日志查看等功能。前端采用了现代简约科幻风格设计。

## 环境要求

- Node.js 16+ (推荐使用16.x LTS版本)
- npm 8+ 或 yarn 1.22+

## 如何启动

1. 安装依赖

```bash
npm install
# 或者
yarn install
```

2. 启动开发服务器

```bash
npm run dev
# 或者
yarn dev
```

3. 构建生产版本

```bash
npm run build
# 或者
yarn build
```

4. 预览构建结果

```bash
npm run preview
# 或者
yarn preview
```

## Node.js版本管理

项目包含一个`.nvmrc`文件，如果你使用nvm管理Node.js版本，可以简单地运行：

```bash
nvm use
```

这会自动切换到项目推荐的Node.js版本。

## 目录结构

```
frontend/
├── public/                # 静态资源
├── src/                   # 源代码
│   ├── assets/            # 资源文件(图片、样式等)
│   ├── components/        # 组件
│   │   └── layout/        # 布局组件
│   ├── router/            # 路由配置
│   ├── services/          # API服务
│   ├── stores/            # Pinia状态管理
│   ├── views/             # 页面视图
│   ├── App.vue            # 主应用组件
│   └── main.js            # 入口文件
├── .eslintrc.js           # ESLint配置
├── .gitignore             # Git忽略配置
├── .nvmrc                 # Node.js版本配置
├── index.html             # HTML入口文件
├── package.json           # 项目配置
├── vite.config.js         # Vite配置
└── README.md              # 项目说明
```

## 主要功能

- **仪表盘**: 展示系统状态、API调用统计、活跃插件和最近活动
- **LLM服务**: 管理和配置各种LLM服务接入
- **插件管理**: 浏览、安装、配置和管理插件
- **终端命令**: 提供命令行界面执行各种操作
- **日志查看**: 查看和过滤系统日志
- **设置**: 配置系统、API密钥、网络等设置

## 技术栈

- Vue.js 3
- Vite
- Pinia (状态管理)
- Vue Router 4
- Axios
- Chart.js (数据可视化)

## 浏览器兼容性

- Chrome/Edge最近两个版本
- Firefox最近两个版本
- Safari最近两个版本

## 代码规范

项目使用ESLint进行代码检查，确保代码风格一致。可以通过以下命令检查和修复代码：

```bash
npm run lint
```

## 常见问题

### 安装依赖失败

如果在安装依赖时遇到问题，尝试以下解决方案：

1. 清除npm缓存：
```bash
npm cache clean --force
```

2. 使用国内镜像源：
```bash
npm config set registry https://registry.npmmirror.com
```

3. 对于Node.js 23+版本可能出现的兼容性警告，可以使用`--force`标志：
```bash
npm install --force
```

### API请求失败

如果API请求失败，确保后端服务正在运行，并检查`vite.config.js`中的代理配置是否正确指向了后端服务的地址和端口。
