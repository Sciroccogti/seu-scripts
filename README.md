# 东南大学 讲座预约和场馆预约脚本

## 1 Introduce

代码改自 1. https://github.com/zhjcreator/fetch_lecture 2. https://github.com/CooperXxx/seuScript 3. https://github.com/luzy99/SEUAutoLogin

## 2 Install

依赖: requests, js2py, bs4, ddddocr

## 3 Use Case

参考 template_config.py，编写配置文件 config.py。

1. 讲座预约
    python main.py

2. 场馆预约
    python reserve.py

3. 每日健康申报
    nohup python daily_post.py > daily_post.log &
