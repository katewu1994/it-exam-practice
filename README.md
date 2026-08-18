# 中文认证考试练习题库

一个静态中文练习网站，目前包含 AWS Certified Generative AI Developer – Professional（AIP-C01）与 Claude Certified Architect – Foundations（CCAR-F）两套题库。题目默认显示中文，可展开查看英文原题与选项；作答、正确性统计和重点标记都保存在浏览器本地，并按题库隔离。


> 非官方学习项目，仅供个人学习与复习参考。题目、答案与解析可能存在错误或歧义，请以相应认证的官方考试指南和产品文档为准。

## 功能

- 从首页选择 `/aws-cip`（128 题）或 `/ccar-f`（152 题）
- 支持题号跳转与前后题切换
- 默认中文题面，可按需展开英文原题及选项
- 作答后即时记录对错；每次会话随机排列选项
- 标记重点题目，并在“答题一览”中按已标记、未作答、答对和答错分类查看
- CCAR-F 解析不采用来源 PDF 的解析文字；先独立判断，再仅用 PDF 标注答案做差异核对
- 当独立答案与来源 PDF 答案不一致时，在解析区明确显示两者差异
- 不依赖后端；学习进度仅储存在当前浏览器的 `localStorage`

## 本地运行

本项目使用浏览器模块加载题库 JSON，因此请通过本地 Web 服务器打开：

```bash
python3 -m http.server 8000
```

随后访问 [http://localhost:8000](http://localhost:8000) 选择题库。也可以直接打开：

- AWS AIP-C01：[http://localhost:8000/aws-cip/](http://localhost:8000/aws-cip/)
- Claude CCAR-F：[http://localhost:8000/ccar-f/](http://localhost:8000/ccar-f/)

例如，CCAR-F 第 84 题可通过 [http://localhost:8000/ccar-f/?question=84](http://localhost:8000/ccar-f/?question=84) 打开。

## 项目结构

```text
index.html                   题库选择入口
aws-cip/                     AWS AIP-C01 练习页与答题一览
ccar-f/                      Claude CCAR-F 练习页与答题一览
app.js / overview.js         两套题库共用的页面启动入口
js/core/                    数据加载、本地存储、判题与文本格式化等共享逻辑
js/pages/                   各页面的渲染与交互逻辑
data/                       AWS 与 CCAR-F 的中英文题面、答案与解析数据
styles.css                  页面样式
```

## 使用与声明

- 本仓库不隶属于 Amazon Web Services（AWS），`AWS` 及相关商标归其各自权利人所有。
- 本仓库不隶属于 Anthropic，`Claude` 及相关商标归其各自权利人所有。
- 请勿将本项目中的内容视为官方样题、考试答案或认证保证。
- 如发现题面、译文或解析问题，欢迎提交 Issue 或 Pull Request；修改前请核对官方资料。
