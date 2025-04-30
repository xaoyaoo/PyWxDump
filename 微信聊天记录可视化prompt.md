任务：根据 提供的微信群聊天记录（json格式）生成今日群/好友日报，输出为风格固定、一致的HTML页面，适合截图分享
## 日报模式选择
- 日报模式：[完整版/简化版] (默认为完整版)
- 如果需要简化版，请在提交时注明"生成简化版"

## 简化版说明
如选择"简化版"，将只生成以下核心部分：
- 今日讨论热点（最多3个）
- 重要消息汇总
- 话唠榜（仅前3名）
- 简化版词云
日报内容更精简，适合快速浏览和分享。

## 聊天记录格式
``` json
[
{
        "nickname": "昏沉沉的", # 发消息人昵称
        "message": "XXX", # 消息内容
        "time": "2025-04-27 11:33:20" #发消息时间
    },
]
```

如未能识别消息格式或未找到有效记录，将显示提示信息并尝试按最佳猜测处理。

## 输出要求
必须使用以下固定的HTML模板和CSS样式，仅更新内容部分，确保每次生成的页面风格完全一致。使用严格定义的深色科技风格。



## HTML结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>[群名称]报告 - [日期]</title>
    <style>
        /* 严格定义的CSS样式，确保风格一致性 */
        :root {
            --bg-primary: #0f0e17;
            --bg-secondary: #1a1925;
            --bg-tertiary: #252336;
            --text-primary: #fffffe;
            --text-secondary: #a7a9be;
            --accent-primary: #ff8906;
            --accent-secondary: #f25f4c;
            --accent-tertiary: #e53170;
            --accent-blue: #3da9fc;
            --accent-purple: #7209b7;
            --accent-cyan: #00b4d8;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Display', 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            font-size: 16px;
            width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            background-color: var(--bg-secondary);
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 36px;
            font-weight: 700;
            color: var(--accent-primary);
            margin-bottom: 10px;
        }
        
        .date {
            font-size: 18px;
            color: var(--text-secondary);
            margin-bottom: 20px;
        }
        
        .meta-info {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        
        .meta-info span {
            background-color: var(--bg-tertiary);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }
        
        section {
            background-color: var(--bg-secondary);
            margin-bottom: 30px;
            padding: 25px;
        }
        
        h2 {
            font-size: 28px;
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-blue);
        }
        
        h3 {
            font-size: 22px;
            font-weight: 600;
            color: var(--accent-primary);
            margin: 15px 0 10px 0;
        }
        
        h4 {
            font-size: 18px;
            font-weight: 600;
            color: var(--accent-secondary);
            margin: 12px 0 8px 0;
        }
        
        p {
            margin-bottom: 15px;
        }
        
        ul, ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        a {
            color: var(--accent-blue);
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        /* 卡片容器样式 */
        .topics-container, .tutorials-container, .messages-container, 
        .dialogues-container, .qa-container, .participants-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        /* 卡片样式 */
        .topic-card, .tutorial-card, .message-card, 
        .dialogue-card, .qa-card, .participant-item, .night-owl-item {
            background-color: var(--bg-tertiary);
            padding: 20px;
        }
        
        /* 话题卡片 */
        .topic-category {
            display: inline-block;
            background-color: var(--accent-blue);
            color: var(--text-primary);
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .topic-keywords {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }
        
        .keyword {
            background-color: rgba(61, 169, 252, 0.2);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 14px;
        }
        
        .topic-mentions {
            color: var(--accent-cyan);
            font-weight: 600;
        }
        
        /* 教程卡片 */
        .tutorial-type {
            display: inline-block;
            background-color: var(--accent-secondary);
            color: var(--text-primary);
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .tutorial-meta {
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .tutorial-category {
            margin-top: 10px;
            font-style: italic;
            color: var(--text-secondary);
        }
        
        /* 消息卡片 */
        .message-meta {
            margin-bottom: 10px;
        }
        
        .message-meta span {
            margin-right: 15px;
            font-size: 14px;
        }
        
        .message-type {
            background-color: var(--accent-tertiary);
            color: var(--text-primary);
            padding: 3px 10px;
            border-radius: 15px;
        }
        
        .priority {
            padding: 3px 10px;
            border-radius: 15px;
        }
        
        .priority-high {
            background-color: var(--accent-secondary);
        }
        
        .priority-medium {
            background-color: var(--accent-primary);
        }
        
        .priority-low {
            background-color: var(--accent-blue);
        }
        
        /* 对话卡片 */
        .dialogue-type {
            display: inline-block;
            background-color: var(--accent-purple);
            color: var(--text-primary);
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .dialogue-content {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .dialogue-highlight {
            font-style: italic;
            color: var(--accent-primary);
            margin: 10px 0;
            font-weight: 600;
        }
        
        /* 问答卡片 */
        .question {
            margin-bottom: 15px;
        }
        
        .question-meta, .answer-meta {
            color: var(--text-secondary);
            margin-bottom: 5px;
            font-size: 14px;
        }
        
        .question-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .tag {
            background-color: rgba(114, 9, 183, 0.2);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 14px;
        }
        
        .answer {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-top: 10px;
        }
        
        .accepted-badge {
            background-color: var(--accent-primary);
            color: var(--text-primary);
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 14px;
        }
        
        /* 热度图 */
        .heatmap-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }
        
        .heat-topic {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .heat-bar {
            height: 20px;
            background-color: rgba(255, 255, 255, 0.1);
            margin: 5px 0;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .heat-fill {
            height: 100%;
            border-radius: 10px;
        }
        
        /* 话唠榜 */
        .participant-rank {
            font-size: 28px;
            font-weight: 700;
            color: var(--accent-primary);
            margin-right: 15px;
            float: left;
        }
        
        .participant-name {
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 5px;
        }
        
        .participant-count {
            color: var(--accent-cyan);
            margin-bottom: 10px;
        }
        
        .participant-characteristics, .participant-words {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .characteristic {
            background-color: rgba(242, 95, 76, 0.2);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 14px;
        }
        
        .word {
            background-color: rgba(229, 49, 112, 0.2);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 14px;
        }
        
        /* 熬夜冠军 */
        .night-owl-item {
            background: linear-gradient(135deg, #0f0e17 0%, #192064 100%);
            padding: 20px;
            display: flex;
            align-items: center;
        }
        
        .owl-crown {
            font-size: 40px;
            margin-right: 20px;
        }
        
        .owl-name {
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 5px;
        }
        
        .owl-title {
            color: var(--accent-primary);
            font-style: italic;
            margin-bottom: 10px;
        }
        
        .owl-time, .owl-messages {
            color: var(--text-secondary);
            margin-bottom: 5px;
        }
        
        .owl-note {
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 10px;
            font-style: italic;
        }
        
        /* 词云 - 云朵样式 */
        .cloud-container {
            position: relative;
            margin: 0 auto;
            padding: 20px 0;
        }
        
        .cloud-wordcloud {
            position: relative;
            width: 600px;
            height: 400px;
            margin: 0 auto;
            background-color: var(--bg-tertiary);
            border-radius: 50%;
            box-shadow: 
                40px 40px 0 -5px var(--bg-tertiary),
                80px 10px 0 -10px var(--bg-tertiary),
                110px 35px 0 -5px var(--bg-tertiary),
                -40px 50px 0 -8px var(--bg-tertiary),
                -70px 20px 0 -10px var(--bg-tertiary);
            overflow: visible;
        }
        
        .cloud-word {
            position: absolute;
            transform-origin: center;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .cloud-word:hover {
            transform: scale(1.1);
            z-index: 10;
        }
        
        .cloud-legend {
            margin-top: 60px;
            display: flex;
            justify-content: center;
            gap: 30px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }
        
        /* 底部 */
        footer {
            text-align: center;
            padding: 20px 0;
            margin-top: 50px;
            background-color: var(--bg-secondary);
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        footer p {
            margin: 5px 0;
        }
        
        .disclaimer {
            margin-top: 15px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <header>
        <h1>[群名称]报告</h1>
        <p class="date">[日期]</p>
        <div class="meta-info">
            <span>总消息数：[数量]</span>
            <span>活跃用户：[数量]</span>
            <span>时间范围：[时间范围]</span>
        </div>
    </header>

    <!-- 1. 今日讨论热点 -->
    <section class="hot-topics">
        <h2>今日讨论热点</h2>
        <div class="topics-container">
            <!-- 在这里填充讨论热点内容，严格按照以下格式，保留3-5个话题 -->
            <div class="topic-card">
                <h3>[热点话题名称]</h3>
                <div class="topic-category">[话题分类]</div>
                <p class="topic-summary">[简要总结(50-100字)]</p>
                <div class="topic-keywords">
                    <span class="keyword">[关键词1]</span>
                    <span class="keyword">[关键词2]</span>
                    <!-- 添加更多关键词 -->
                </div>
                <div class="topic-mentions">提及次数：[次数]</div>
            </div>
            <!-- 复制上述卡片结构添加更多话题 -->
        </div>
    </section>

    <!-- 2. 实用教程与资源分享 -->
    <section class="tutorials">
        <h2>实用教程与资源分享</h2>
        <div class="tutorials-container">
            <!-- 在这里填充教程和资源内容，严格按照以下格式 -->
            <div class="tutorial-card">
                <div class="tutorial-type">[TUTORIAL | NEWS | RESOURCE]</div>
                <h3>[分享的教程或资源标题]</h3>
                <div class="tutorial-meta">
                    <span class="shared-by">分享者：[昵称]</span>
                    <span class="share-time">时间：[时间]</span>
                </div>
                <p class="tutorial-summary">[内容简介]</p>
                <div class="key-points">
                    <h4>要点：</h4>
                    <ul>
                        <li>[要点1]</li>
                        <li>[要点2]</li>
                        <!-- 添加更多要点 -->
                    </ul>
                </div>
                <div class="tutorial-link">
                    <a href="[URL]" class="link valid">查看原文: [域名]</a>
                </div>
                <div class="tutorial-category">分类：[分类]</div>
            </div>
            <!-- 复制上述卡片结构添加更多资源 -->
        </div>
    </section>

    <!-- 3. 重要消息汇总 -->
    <section class="important-messages">
        <h2>重要消息汇总</h2>
        <div class="messages-container">
            <!-- 在这里填充重要消息内容，严格按照以下格式 -->
            <div class="message-card">
                <div class="message-meta">
                    <span class="time">[消息时间]</span>
                    <span class="sender">[发送者昵称]</span>
                    <span class="message-type">[NOTICE | EVENT | ANNOUNCEMENT | OTHER]</span>
                    <span class="priority priority-high">优先级：[高|中|低]</span>
                </div>
                <p class="message-content">[消息内容]</p>
                <div class="message-full-content">
                    <p>[完整通知内容]</p>
                </div>
            </div>
            <!-- 复制上述卡片结构添加更多消息 -->
        </div>
    </section>

    <!-- 4. 有趣对话或金句 -->
    <section class="interesting-dialogues">
        <h2>有趣对话或金句</h2>
        <div class="dialogues-container">
            <!-- 在这里填充对话内容，严格按照以下格式 -->
            <div class="dialogue-card">
                <div class="dialogue-type">[DIALOGUE | QUOTE]</div>
                <div class="dialogue-content">
                    <div class="message">
                        <div class="message-meta">
                            <span class="speaker">[说话者昵称]</span>
                            <span class="time">[发言时间]</span>
                        </div>
                        <p class="message-content">[消息内容]</p>
                    </div>
                    <div class="message">
                        <div class="message-meta">
                            <span class="speaker">[说话者昵称]</span>
                            <span class="time">[发言时间]</span>
                        </div>
                        <p class="message-content">[消息内容]</p>
                    </div>
                    <!-- 添加更多对话消息 -->
                </div>
                <div class="dialogue-highlight">[对话中的金句或亮点]</div>
                <div class="dialogue-topic">相关话题：[某某话题]</div>
            </div>
            <!-- 复制上述卡片结构添加更多对话 -->
        </div>
    </section>

    <!-- 5. 问题与解答 -->
    <section class="questions-answers">
        <h2>问题与解答</h2>
        <div class="qa-container">
            <!-- 在这里填充问答内容，严格按照以下格式 -->
            <div class="qa-card">
                <div class="question">
                    <div class="question-meta">
                        <span class="asker">[提问者昵称]</span>
                        <span class="time">[提问时间]</span>
                    </div>
                    <p class="question-content">[问题内容]</p>
                    <div class="question-tags">
                        <span class="tag">[相关标签1]</span>
                        <span class="tag">[相关标签2]</span>
                        <!-- 添加更多标签 -->
                    </div>
                </div>
                <div class="answers">
                    <div class="answer">
                        <div class="answer-meta">
                            <span class="responder">[回答者昵称]</span>
                            <span class="time">[回答时间]</span>
                            <span class="accepted-badge">最佳回答</span>
                        </div>
                        <p class="answer-content">[回答内容]</p>
                    </div>
                    <!-- 添加更多回答 -->
                </div>
            </div>
            <!-- 复制上述卡片结构添加更多问答 -->
        </div>
    </section>

    <!-- 6. 群内数据可视化 -->
    <section class="analytics">
        <h2>群内数据可视化</h2>
        
        <!-- 话题热度 -->
        <h3>话题热度</h3>
        <div class="heatmap-container">
            <!-- 在这里填充话题热度数据，严格按照以下格式 -->
            <div class="heat-item">
                <div class="heat-topic">[话题名称]</div>
                <div class="heat-percentage">[百分比]%</div>
                <div class="heat-bar">
                    <div class="heat-fill" style="width: [百分比]%; background-color: #3da9fc;"></div>
                </div>
                <div class="heat-count">[数量]条消息</div>
            </div>
            <!-- 复制上述结构添加更多热度项，每项使用不同颜色 -->
            <div class="heat-item">
                <div class="heat-topic">[话题名称]</div>
                <div class="heat-percentage">[百分比]%</div>
                <div class="heat-bar">
                    <div class="heat-fill" style="width: [百分比]%; background-color: #f25f4c;"></div>
                </div>
                <div class="heat-count">[数量]条消息</div>
            </div>
            <!-- 可用的颜色: #3da9fc, #f25f4c, #7209b7, #e53170, #00b4d8, #4cc9f0 -->
        </div>
        
        <!-- 话唠榜 -->
        <h3>话唠榜</h3>
        <div class="participants-container">
            <!-- 在这里填充话唠榜数据，严格按照以下格式 -->
            <div class="participant-item">
                <div class="participant-rank">1</div>
                <div class="participant-info">
                    <div class="participant-name">[群友昵称]</div>
                    <div class="participant-count">[数量]条消息</div>
                    <div class="participant-characteristics">
                        <span class="characteristic">[特点1]</span>
                        <span class="characteristic">[特点2]</span>
                        <!-- 添加更多特点 -->
                    </div>
                    <div class="participant-words">
                        <span class="word">[常用词1]</span>
                        <span class="word">[常用词2]</span>
                        <!-- 添加更多常用词 -->
                    </div>
                </div>
            </div>
            <!-- 复制上述结构添加更多参与者 -->
        </div>
        
        <!-- 熬夜冠军 -->
        <h3>熬夜冠军</h3>
        <div class="night-owls-container">
            <!-- 在这里填充熬夜冠军数据，严格按照以下格式 -->
            <div class="night-owl-item">
                <div class="owl-crown" title="熬夜冠军">👑</div>
                <div class="owl-info">
                    <div class="owl-name">[熬夜冠军昵称]</div>
                    <div class="owl-title">[熬夜冠军称号]</div>
                    <div class="owl-time">最晚活跃时间：[时间]</div>
                    <div class="owl-messages">深夜消息数：[数量]</div>
                    <div class="owl-last-message">[最后一条深夜消息内容]</div>
                    <div class="owl-note">注：熬夜时段定义为23:00-06:00，已考虑不同时区</div>
                </div>
            </div>
        </div>
    </section>

    <!-- 7. 词云 -->
    <section class="word-cloud">
        <h2>热门词云</h2>
        <div class="cloud-container">
            <!-- 词云容器 - 现在是云朵样式 -->
            <div class="cloud-wordcloud" id="word-cloud">
                <!-- 为每个词创建一个span元素，使用绝对定位放置 -->
                <!-- 以下是一些示例，请根据实际内容生成40-60个词 -->
                <span class="cloud-word" style="left: 300px; top: 120px; font-size: 38px; color: #00b4d8; transform: rotate(-15deg); font-weight: bold;">[关键词1]</span>
                
                <span class="cloud-word" style="left: 180px; top: 150px; font-size: 32px; color: #4cc9f0; transform: rotate(5deg); font-weight: bold;">[关键词2]</span>
                
                <span class="cloud-word" style="left: 400px; top: 180px; font-size: 28px; color: #f25f4c; transform: rotate(-5deg);">[关键词3]</span>
                
                <span class="cloud-word" style="left: 250px; top: 220px; font-size: 24px; color: #ff8906; transform: rotate(10deg);">[关键词4]</span>
                
                <span class="cloud-word" style="left: 350px; top: 90px; font-size: 22px; color: #e53170; transform: rotate(-10deg);">[关键词5]</span>
                
                <!-- 继续添加更多词 -->
            </div>
            
            <div class="cloud-legend">
                <div class="legend-item">
                    <span class="legend-color" style="background-color: #00b4d8;"></span>
                    <span class="legend-label">[分类1] 相关词汇</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: #4361ee;"></span>
                    <span class="legend-label">[分类2] 相关词汇</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background-color: #7209b7;"></span>
                    <span class="legend-label">[分类3] 相关词汇</span>
                </div>
            </div>
        </div>
    </section>

    <!-- 8. 页面底部 -->
    <footer>
        <p>数据来源：[群名称]聊天记录</p>
        <p>生成时间：<span class="generation-time">[当前时间]</span></p>
        <p>统计周期：[日期] [时间范围]</p>
        <p class="disclaimer">免责声明：本报告内容基于群聊公开讨论，如有不当内容或侵权问题请联系管理员处理。</p>
    </footer>
</body>
</html>