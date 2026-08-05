# AWS AIP-C01 中文练习题库

一个用于复习 AWS Certified AI Practitioner（AIP-C01）的静态中文练习网站。题目默认显示中文，可展开查看英文原题与选项；作答、正确性统计和重点标记都保存在浏览器本地。


> 非官方学习项目，仅供个人学习与复习参考。题目、答案与解析可能存在错误或歧义，请以 [AWS 官方考试指南](https://aws.amazon.com/certification/certified-ai-practitioner/) 和官方文档为准。

## 功能

- 逐题浏览 128 道练习题，支持题号跳转与前后题切换
- 默认中文题面，可按需展开英文原题及选项
- 作答后即时记录对错；每次会话随机排列选项
- 标记重点题目，并在“答题一览”中按已标记、未作答、答对和答错分类查看
- 不依赖后端；学习进度仅储存在当前浏览器的 `localStorage`

## 本地运行

本项目使用浏览器模块加载题库 JSON，因此请通过本地 Web 服务器打开：

```bash
python3 -m http.server 8000
```

随后访问 [http://localhost:8000](http://localhost:8000)。例如，第 24 题可通过 [http://localhost:8000/?question=24](http://localhost:8000/?question=24) 打开。

## 项目结构

```text
index.html / app.js       题目练习页
overview.html / overview.js  学习进度总览页
data/                    中英文题面、答案与解析数据
styles.css               页面样式
```

## 使用与声明

- 本仓库不隶属于 Amazon Web Services（AWS），`AWS` 及相关商标归其各自权利人所有。
- 请勿将本项目中的内容视为官方样题、考试答案或认证保证。
- 如发现题面、译文或解析问题，欢迎提交 Issue 或 Pull Request；修改前请核对官方资料。
