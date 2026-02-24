\# 百度UI自动化测试工具 v2.0



\## 项目简介

基于 \*\*Selenium + Pytest\*\* 实现的百度搜索UI自动化测试项目，支持Excel用例参数化驱动、HTML可视化报告生成，深度解决百度反自动化检测问题，3条测试用例通过率100%。



\## 核心技术栈

\- 自动化框架：Selenium 4.x、Pytest 7.x

\- 数据驱动：Pandas + OpenPyXL（Excel读取）

\- 报告生成：pytest-html

\- 版本管理：Git（分支开发 + 标签标记）



\## 核心亮点

1\. \*\*反反自动化适配\*\*：通过JS直接操作DOM、清除浏览器自动化特征，绕过百度检测；

2\. \*\*工程化规范\*\*：采用Feature分支开发，Main分支存稳定版本，打v2.0标签标记正式版；

3\. \*\*可扩展性强\*\*：支持Excel批量添加用例，无需修改代码即可扩展测试场景。



\## 快速运行

```bash

\# 安装依赖

pip install selenium pytest pandas openpyxl pytest-html webdriver-manager



\# 运行测试并生成报告

cd src

pytest test\_baidu\_search.py -v --html=../reports/baidu\_test\_report.html

