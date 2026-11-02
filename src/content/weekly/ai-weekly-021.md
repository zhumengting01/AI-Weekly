---
title: "前沿模型走向受控部署，开放权重与企业工作流同步推进"
date: 2026-11-02
periodStart: 2026-10-26
periodEnd: 2026-11-01
excerpt: "10月26日至11月1日9条精选：GPT-6.1 Terra、Gemini 4 Carbon、Mistral Large 4权重、LFM3、国内图像API与企业、机器人、语音及网页训练偏好动态。"
tags: [AI, 周刊, 大模型, 开源, 企业应用]
featured: false
takeaways:
  - "性能升级之外，前沿模型的首批访问正更多与特定任务、用户资格和安全流程绑定。"
  - "开放权重正在覆盖超大模型与端侧小模型两端，但许可证、硬件和验证成本仍决定可用性。"
  - "企业集成的重点从接入聊天界面，转向把既有权限、记录和实际工作流一并接入。"
readerFor: "关注前沿模型、开源部署与企业智能体落地的读者"
sourcesCount: 9
---

本期回顾 **2026 年 10 月 26 日—11 月 1 日**的 AI 动态。

# 本周焦点

## GPT-6.1 Terra上线：把视觉推理与电脑操作放到更低价位

**10 月 26 日**，OpenAI发布GPT-6.1 Terra，并在ChatGPT Work、Codex和API中提供。API标准价格为每百万输入token 1美元、输出token 5美元，缓存输入为0.05美元；产品定位是视觉推理、电脑操作、简洁写作和范围明确的代码修改。

公告给出的Terminal-Bench 4.0、事实性与电脑操作成绩均为厂商评测。例如在最大推理强度下，Terra在Terminal-Bench 4.0的得分为50.3%，对比对象GPT-5.6 Terra为21.5%。这些数值能说明同一套公告口径下的代际变化，不能直接替代企业自身界面、权限、网页状态和任务成功率的验收。

[阅读原文：OpenAI · Introducing GPT-6.1 Terra](https://openai.com/index/introducing-gpt-6-1-terra/)

---

## Gemini 4 Carbon以分阶段方式面向网络防御者开放

**10 月 28 日**，Google DeepMind公布Gemini 4 Carbon，称其面向网络安全与长程任务。公司报告其在Artificial Analysis Intelligence Index v5.0得分59，并列出SEC-bench Pro、ExploitGym和CWE-bench上的结果；这些均应视为发布方引用或报告的评测，而非不同系统可直接横比的通用生产指标。

本次发布的要点也在于访问方式。Google表示，Carbon首先通过Fairwind Program提供给部分网络防御者，并继续收集反馈、完善护栏后再逐步扩大范围；它不是面向所有开发者和消费者的即时普遍可用版本。其标示的起始API价格是每百万输入token 2美元、输出token 10美元，缓存输入折扣为95%。

[阅读原文：Google · Introducing Gemini 4 Carbon](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/)

---

# 开源与国内动态

## Mistral发布Large 4权重，超大开放模型的门槛仍在部署侧

**10 月 29 日**，Mistral宣布发布“Le Chonk”（Mistral Large 4）的权重，定位为面向智能体编程与网络防御的开放模型。此前的10月6日公告已将Large 4作为公共预览推出，本周的变化是权重发布；两者不应混为同一次上线。

Large 4为原生多模态MoE模型，总参数约1万亿、每token激活约520亿。开放权重扩大了研究、私有化评估和托管选择空间，却不等于普通团队可以低成本本地部署：权重体积、推理显存、并行策略和许可条件依然要逐项确认。特别是在安全和代码任务上，还应把补丁是否正确、是否引入新风险作为独立验收项。

[阅读原文：Mistral · Le Chonk: Built for Coders, Trusted by Defenders](https://mistral.ai/news/)

---

## Liquid AI开源LFM3：以2B级多模态家族瞄准端侧专用任务

**10 月 27 日**，Liquid AI发布LFM3系列。首批模型围绕约2B参数级别，覆盖文本、视觉、音频、全模态和决策任务，使用同一基础骨干；基础与后训练权重已在Hugging Face、其Playground和API提供。

公司称LFM3-1.7B采用混合架构、以22万亿token预训练，文本模型拥有256K上下文，并可在单张GPU上微调。公告还给出“4-bit约1GB”等部署数据和多项基准；这些属于厂商材料，实际端侧吞吐、内存和效果仍会受量化格式、设备、上下文长度及工具链影响。

[阅读原文：Liquid AI · Introducing LFM3](https://www.liquid.ai/blog/lfm3)

---

## Qwen-Image-2.1的Pro与Turbo API面向生产图像流程

**10 月 26 日**，阿里云发布Qwen-Image-2.1 Pro和Turbo API的生产使用说明。该系列可由文本和图片输入生成、编辑图像，并支持真实alpha通道与最多10张参考图。公告明确区分了9月开源权重、10月9日Turbo检查点及API上线，与本周文章发布的产品化信息。

按公告所列新加坡标价，Turbo为每图0.016美元、120次/分钟；Pro为每图0.04美元、20次/分钟。该价格为列出的地区标价，未含促销，且不同区域不同；“一万张Turbo约160美元”也只是按此口径的算术示例。开源权重受Qwen Research License约束，商业使用需要通过Model Studio或另行取得商业许可。

[阅读原文：阿里云 · Qwen-Image-2.1 Pro and Turbo APIs](https://www.alibabacloud.com/blog/qwen-image-2-1-pro-and-turbo-apis-are-live-one-7b-model-to-generate-edit-and-cut-out_603679)

---

# 科研与行业应用

## NVIDIA发布Nemotron 3.5 Transcribe，将转写风格变成提示词选择

**10 月 28 日**，NVIDIA发布Nemotron 3.5 Transcribe。这一语音增强语言模型将语音编码器、说话人分离模型与Nemotron 3.5 Lightning 30B-A3B组合，约有43亿激活参数；公告称其可处理最长一小时的录音，支持40种语言的转写、翻译、语种识别和可选逐词时间戳。

与传统固定输出格式的ASR不同，用户可通过自然语言指令选择逐字、书面化、上下文或带说话人归属的转写。NVIDIA报告其在公开英文与多语种Open ASR Leaderboard上的平均词错率分别为4.71%和4.62%，并称给定实体词表可将ContextASR-Bench命名实体错误降至原来的六分之一；这些是发布方给出的特定数据集和设置结果。

[阅读原文：NVIDIA · Nemotron 3.5 Transcribe](https://research.nvidia.com/labs/nemotron/NVIDIA-Nemotron-3.5-Transcribe/)

---

## Gemini Robotics ER 2进入Google Cloud预览，连接高层推理与低层控制

**10 月 27 日**，Google Cloud宣布Gemini Robotics Embodied Reasoning 2（ER 2）在Gemini平台的Model Garden中以预览形式提供。它面向固定机械臂、人形机器人等不同形态，尝试用时空视频理解、长程规划和工具调用协调VLA模型、导航API或自定义函数。

公告描述的能力包括多分钟、数百次决策的任务与多机器人协作，也提出可用空间指向、片段定位和进度分类为演示视频标注，再训练定制VLA模型。对延迟敏感的SLAM和路径规划，官方架构仍建议放在现场的Google Distributed Cloud等环境；这说明“大脑”模型并未取代实时控制和安全系统。

[阅读原文：Google Cloud · Gemini Robotics ER 2](https://cloud.google.com/blog/products/ai-machine-learning/gemini-robotics-embodied-reasoning-2-is-now-available-on-google-cloud)

---

## Oracle与ServiceNow相继宣布把业务上下文接入ChatGPT

**10 月 27 日**，OpenAI与Oracle宣布拟把Oracle应用和数据接入ChatGPT，并开发Oracle AI Workspace、AI Security Mesh与App Composer等能力；公告称美国Oracle客户可通过Marketplace采购API、Codex和ChatGPT Work。次日，OpenAI与ServiceNow宣布扩展合作，ServiceNow MCP插件已在OpenAI marketplace提供，更多交互能力预计在2026年底，若干语音、安全和Codex能力则标注为2027年的计划或早期访问。

两则公告的共同方向是让对话界面读取企业上下文并在既有业务系统中执行经批准的下一步操作，例如查找相似工单、评估变更风险或更新记录。但连接并不绕过治理：ServiceNow明确由客户选择开放哪些能力，Action Fabric沿用组织现有规则与权限；Oracle也把统一登录、权限和审批作为目标的一部分。

[阅读原文：OpenAI · Oracle apps in ChatGPT](https://openai.com/index/oracle-apps-in-chatgpt/)

[阅读原文：OpenAI · ServiceNow partnership expansion](https://openai.com/index/openai-servicenow-partnership-expansion/)

---

## OpenAI响应统一训练偏好信号，实际执行仍待后续说明

**10 月 30 日**，OpenAI宣布将尊重robots.txt中的一项通用信号，让网站运营者表达其内容是否可用于基础生成式AI训练的偏好。这一自愿性做法与IETF的AI Preferences工作组有关，旨在减少站长为不同AI提供方逐一维护规则的成本。

公告同时写明，OpenAI计划在未来数月实施并另行说明实现细节；新信号也不会替代现有的爬虫控制。因此这是对支持标准及未来实施的承诺，并非本周已经完成、可由所有网站立即验证的统一执行结果。

[阅读原文：OpenAI · AI training preferences](https://openai.com/index/helping-websites-express-ai-training-preferences/)

---

# 一周观察

本周的主线不是单纯更大的参数或更多的功能，而是“能力如何被放进可控边界”。Carbon把高风险网络能力先交给有限的防御者；ER 2把高层推理与现场实时控制分层；Oracle和ServiceNow把权限与审批留在原有系统；robots.txt信号则把训练偏好转为可共同处理的规则。

与此同时，开放路线在两个方向扩张：Large 4把超大模型权重交给生态，LFM3和Nemotron则让更专用的多模态、语音能力可被下载和适配。对使用者，下一步应比较的不只是模型榜单，而是三项更具体的事实：是否真的可访问、在自身数据和硬件上能否稳定完成任务、以及失败时谁能看见、阻止和纠正它。
