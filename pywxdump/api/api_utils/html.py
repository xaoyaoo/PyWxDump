# 创建html可视化页面
import json
import re


class HtmlController(object):
    def __init__(self):
        pass

    # 根据json返回html
    def create_html(self,json_data) -> str:
        json_data = r"```json\n{\n\"header\": {\n\"title\": \"群聊报告\",\n\"date\": \"2025-04-29\",\n\"metaInfo\": {\n\"totalMessages\": \"35\",\n\"activeUsers\": \"12\",\n\"timeRange\": \"07:03:10 - 15:36:25\"\n}\n},\n\"sections\": {\n\"hotTopics\": {\n\"items\": [\n{\n\"name\": \"AI技术讨论\",\n\"category\": \"科技\",\n\"summary\": \"群内围绕Qwen3开源、Vidu Q1体验、夸克AI相机等AI技术展开热烈讨论，涉及模型性能、应用场景和开发者体验。多位成员分享了相关技术文章和体验报告。\",\n\"keywords\": [\"Qwen3\", \"Vidu\", \"AI相机\"],\n\"mentions\": \"15\"\n},\n{\n\"name\": \"熬夜与工作压力\",\n\"category\": \"生活\",\n\"summary\": \"成员们讨论熬夜工作现象，分享各自熬夜经历，对比互联网大厂与普通开发者的工作强度差异，引发关于工作生活平衡的思考。\",\n\"keywords\": [\"熬夜\", \"加班\", \"工作强度\"],\n\"mentions\": \"8\"\n}\n]\n},\n\"tutorials\": {\n\"items\": [\n{\n\"type\": \"TUTORIAL\",\n\"title\": \"体验完刚上线的Vidu Q1，后劲有点大（附AI视频创作教程）\",\n\"sharedBy\": \"苍何\",\n\"time\": \"2025-04-29 09:39:42\",\n\"summary\": \"分享Vidu Q1 AI视频创作工具的体验和教程，介绍其清晰度和一致性的提升。\",\n\"keyPoints\": [\"AI视频清晰度提升\", \"一致性改进\"],\n\"url\": \"http://mp.weixin.qq.com/s?__biz=MzU4NTE1Mjg4MA==&mid=2247493267&idx=1&sn=0189fb501578ce8e27142fbe2f590d03&chksm=fc9a946728c367005c19cb5a335300d05d51a441f9f20424a0a72c904a47bdf003252576318a&mpshare=1&scene=1&srcid=04297l70B2zsuypDfjUh0rh5&sharer_shareinfo=181efb947f938ab90786c776bf7bbda7&sharer_shareinfo_first=181efb947f938ab90786c776bf7bbda7#rd\",\n\"domain\": \"mp.weixin.qq.com\",\n\"category\": \"AI工具\"\n},\n{\n\"type\": \"TUTORIAL\",\n\"title\": \"阿里新出的夸克AI相机，强大到我有点陌生\",\n\"sharedBy\": \"苍何\",\n\"time\": \"2025-04-29 09:42:38\",\n\"summary\": \"介绍夸克AI相机的新奇玩法和功能，展示其强大的AI图像处理能力。\",\n\"keyPoints\": [\"新奇玩法\", \"抽象功能\"],\n\"url\": \"http://mp.weixin.qq.com/s?__biz=MzU4NTE1Mjg4MA==&mid=2247493275&idx=1&sn=93556ddd1da7fb8733a23a7c4adbb76b&chksm=fc2a2d25774cce23c75acd8850b85c585c0bcf78d14b810e157efaec5106abf563cf58e26aef&mpshare=1&scene=1&srcid=0429vDf8NbEzNLBQQyFlABmU&sharer_shareinfo=28b94477ec8201b88aa30338e82e8999&sharer_shareinfo_first=28b94477ec8201b88aa30338e82e8999#rd\",\n\"domain\": \"mp.weixin.qq.com\",\n\"category\": \"AI应用\"\n},\n{\n\"type\": \"RESOURCE\",\n\"title\": \"仅2MB，Windows瞬间超级丝滑！\",\n\"sharedBy\": \"AHapi²⁰²⁵\",\n\"time\": \"2025-04-29 11:13:38\",\n\"summary\": \"分享一款轻量级Windows优化工具，声称能显著提升系统运行速度。\",\n\"keyPoints\": [\"2MB大小\", \"系统优化\"],\n\"url\": \"https://mp.weixin.qq.com/s/es77Jc6Du03ppJD5XJeQUg\",\n\"domain\": \"mp.weixin.qq.com\",\n\"category\": \"系统工具\"\n}\n]\n},\n\"importantMessages\": {\n\"items\": [\n{\n\"time\": \"2025-04-29 10:00:18\",\n\"sender\": \"苍何\",\n\"type\": \"NEWS\",\n\"priority\": \"高\",\n\"content\": \"2025年04月29日 AI科技早报：阿里开源8款Qwen3模型，腾讯开源Kuikly跨端框架，OpenAI推出ChatGPT购物功能等11条重要新闻。\",\n\"fullContent\": \"2025年04月29日 AI科技早报1、阿里开源8款Qwen3模型，集成MCP，性能超DeepSeek-R1、OpenAI o1。2、Qafind Labs发布ChatDLM扩散语言模型，推理速度高达2800 tokens/s。3、腾讯开源Kuikly跨端框架，基于Kotlin支持多平台开发，已应用于QQ。4、OpenAI 推出 ChatGPT 购物功能，用户可通过 ChatGPT 便捷购物。5、字节Seed团队提出PHD-Transformer，突破预训练长度扩展瓶颈。6、百度发布文心快码3.5版本与多模态AI智能体Zulu，助力工程师提效。7、Kimi与财新传媒合作，提供专业财经内容，推动AI+传统媒体融合。8、苹果加速「N50」智能眼镜项目，融合AI技术预计2027年亮相。9、研究显示OpenAI o3在病毒学领域超越94%人类专家，生物安全引关注。10、华为测试自研AI芯片Ascend 910D，旨在替代英伟达H100芯片。11、🔥【记得收藏】早报同步更新到开源 AI 知识库：https://u55dyuejxc.feishu.cn/wiki/FkmNwxYHDigJ3akIUGHc8MSTn4d\"\n}\n]\n},\n\"dialogues\": {\n\"items\": [\n{\n\"type\": \"DIALOGUE\",\n\"messages\": [\n{\n\"speaker\": \"好名字\",\n\"time\": \"2025-04-29 08:16:23\",\n\"content\": \"这个我弄完，ai做的小程序有bug，流程走不通，还改不了[捂脸]\"\n},\n{\n\"speaker\": \"贾👦🏻\",\n\"time\": \"2025-04-29 08:54:33\",\n\"content\": \"可以微调 不过源码需要买的\"\n},\n{\n\"speaker\": \"好名字\",\n\"time\": \"2025-04-29 09:13:32\",\n\"content\": \"微调一次，然后再想调就需要开会员了\"\n},\n{\n\"speaker\": \"贾👦🏻\",\n\"time\": \"2025-04-29 09:14:09\",\n\"content\": \"需求变更一个字 就需要重新购买[破涕为笑]\"\n}\n],\n\"highlight\": \"AI小程序开发中的商业化模式讨论\",\n\"relatedTopic\": \"AI开发工具\"\n},\n{\n\"type\": \"DIALOGUE\",\n\"messages\": [\n{\n\"speaker\": \"苍何\",\n\"time\": \"2025-04-29 09:26:49\",\n\"content\": \"我熬不动\"\n},\n{\n\"speaker\": \"AHapi²⁰²⁵\",\n\"time\": \"2025-04-29 09:27:25\",\n\"content\": \"不要卷别人[旺柴]别人写了 就不卷他们了\"\n},\n{\n\"speaker\": \"苍何\",\n\"time\": \"2025-04-29 09:27:55\",\n\"content\": \"新闻得第一时间，做不到写了也没啥用\"\n},\n{\n\"speaker\": \"苍何\",\n\"time\": \"2025-04-29 09:28:03\",\n\"content\": \"还不如写些应用\"\n},\n{\n\"speaker\": \"大风（Wind）\",\n\"time\": \"2025-04-29 09:28:23\",\n\"content\": \"看看哪些是5-7点发推文的，基本都是卷王了\"\n},\n{\n\"speaker\": \"沉默王二\",\n\"time\": \"2025-04-29 09:28:44\",\n\"content\": \"身体能扛住确实离谱\"\n},\n{\n\"speaker\": \"苍何\",\n\"time\": \"2025-04-29 09:29:03\",\n\"content\": \"是啊，太肝了\"\n}\n],\n\"highlight\": \"关于工作强度和熬夜文化的讨论\",\n\"relatedTopic\": \"工作生活平衡\"\n}\n]\n},\n\"qa\": {\n\"items\": [\n{\n\"question\": {\n\"asker\": \"银色子弹-捷\",\n\"time\": \"2025-04-29 11:10:26\",\n\"content\": \"问一下win11电脑，你长时间没清理，运行慢，一般用什么来清理电脑？ 不要360啊，那个太流氓了，想知道各位大佬有没有优秀的软件推荐一下\",\n\"tags\": [\"Windows优化\", \"系统清理\"]\n},\n\"answers\": [\n{\n\"responder\": \"昏沉沉的\",\n\"time\": \"2025-04-29 11:11:59\",\n\"content\": \"ccclean\",\n\"isAccepted\": false\n},\n{\n\"responder\": \"🤑程序儒\",\n\"time\": \"2025-04-29 11:13:07\",\n\"content\": \"360极速版、Wise Care 365\",\n\"isAccepted\": false\n},\n{\n\"responder\": \"AHapi²⁰²⁵\",\n\"time\": \"2025-04-29 11:13:38\",\n\"content\": \"仅2MB，Windows瞬间超级丝滑！这才是，真神器！\",\n\"isAccepted\": true\n}\n]\n},\n{\n\"question\": {\n\"asker\": \"ಠ_ಠ 闲鱼一条ಠ_ಠ\",\n\"time\": \"2025-04-29 11:37:49\",\n\"content\": \"请问哪位哥还有扣子的邀请码吗？\",\n\"tags\": [\"邀请码\", \"扣子空间\"]\n},\n\"answers\": [\n{\n\"responder\": \"贾👦🏻\",\n\"time\": \"2025-04-29 11:40:37\",\n\"content\": \"RootUser_2105656329 邀请你体验扣子空间，快来和 Agent 一起开始你的工作吧！https://www.coze.cn/space-preview?invite_code=SCL7DAL0\",\n\"isAccepted\": true\n},\n{\n\"responder\": \"9527\",\n\"time\": \"2025-04-29 11:47:43\",\n\"content\": \"RootUser_2106519373 邀请你体验扣子空间，快来和 Agent 一起开始你的工作吧！https://www.coze.cn/space-preview?invite_code=A8IT4MUE\",\n\"isAccepted\": false\n}\n]\n}\n]\n},\n\"analytics\": {\n\"heatmap\": [\n{\n\"topic\": \"AI技术\",\n\"percentage\": \"45%\",\n\"color\": \"#3da9fc\",\n\"count\": \"16\"\n},\n{\n\"topic\": \"工作讨论\",\n\"percentage\": \"25%\",\n\"color\": \"#4361ee\",\n\"count\": \"9\"\n},\n{\n\"topic\": \"工具推荐\",\n\"percentage\": \"15%\",\n\"color\": \"#00b4d8\",\n\"count\": \"5\"\n},\n{\n\"topic\": \"其他\",\n\"percentage\": \"15%\",\n\"color\": \"#7209b7\",\n\"count\": \"5\"\n}\n],\n\"chattyRanking\": [\n{\n\"rank\": 1,\n\"name\": \"苍何\",\n\"count\": \"7\",\n\"characteristics\": [\"技术分享\", \"新闻发布\"],\n\"commonWords\": [\"AI\", \"开源\", \"熬夜\"]\n},\n{\n\"rank\": 2,\n\"name\": \"AHapi²⁰²⁵\",\n\"count\": \"6\",\n\"characteristics\": [\"幽默评论\", \"资源分享\"],\n\"commonWords\": [\"旺柴\", \"加班\", \"神器\"]\n},\n{\n\"rank\": 3,\n\"name\": \"贾👦🏻\",\n\"count\": \"3\",\n\"characteristics\": [\"问题解答\", \"邀请码分享\"],\n\"commonWords\": [\"源码\", \"购买\", \"邀请\"]\n}\n],\n\"nightOwl\": {\n\"name\": \"苍何\",\n\"title\": \"熬夜冠军\",\n\"latestTime\": \"09:42:54\",\n\"messageCount\": \"7\",\n\"lastMessage\": \"我熬夜写了这一篇[旺柴]\"\n}\n},\n\"wordCloud\": {\n\"words\": [\n{\n\"text\": \"AI\",\n\"size\": 42,\n\"color\": \"#00b4d8\",\n\"rotation\": 0\n},\n{\n\"text\": \"熬夜\",\n\"size\": 36,\n\"color\": \"#4361ee\",\n\"rotation\": -15\n},\n{\n\"text\": \"开源\",\n\"size\": 32,\n\"color\": \"#00b4d8\",\n\"rotation\": 15\n},\n{\n\"text\": \"Qwen3\",\n\"size\": 28,\n\"color\": \"#3da9fc\",\n\"rotation\": -10\n},\n{\n\"text\": \"Vidu\",\n\"size\": 26,\n\"color\": \"#3da9fc\",\n\"rotation\": 10\n},\n{\n\"text\": \"清理\",\n\"size\": 24,\n\"color\": \"#7209b7\",\n\"rotation\": -5\n},\n{\n\"text\": \"邀请码\",\n\"size\": 22,\n\"color\": \"#7209b7\",\n\"rotation\": 5\n}\n],\n\"legend\": [\n{\"color\": \"#00b4d8\", \"label\": \"技术 相关词汇\"},\n{\"color\": \"#4361ee\", \"label\": \"生活 相关词汇\"},\n{\"color\": \"#7209b7\", \"label\": \"工具 相关词汇\"}\n]\n}\n},\n\"footer\": {\n\"dataSource\": \"群聊聊天记录\",\n\"generationTime\": \"2025-04-29 16:00:00\",\n\"statisticalPeriod\": \"2025-04-29 07:03:10 - 15:36:25\",\n\"disclaimer\": \"本报告内容基于群聊公开讨论，如有不当内容或侵权问题请联系管理员处理。\"\n}\n}\n```"

        # 加载模板
        html = """
            <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>[群/用户名称]日报 - [日期]</title>
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
                 /* 新增头像相关样式 */
            .user-avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                object-fit: cover;
                transition: transform 0.3s ease;
                position: relative;
                cursor: pointer;
                border: 2px solid var(--accent-primary);
            }

            /* 头像悬停效果 */
            .user-avatar:hover {
                transform: scale(1.1) rotate(5deg);
                z-index: 100;
            }

            /* 头像tooltip */
            .avatar-tooltip {
                visibility: hidden;
                background-color: var(--bg-tertiary);
                color: var(--text-primary);
                text-align: center;
                padding: 5px 10px;
                border-radius: 6px;
                position: absolute;
                z-index: 1000;
                bottom: 125%;
                left: 50%;
                transform: translateX(-50%);
                white-space: nowrap;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 14px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            }

            .user-avatar:hover .avatar-tooltip {
                visibility: visible;
                opacity: 1;
            }

            /* 热度用户专区 */
            .hot-users {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }

            .hot-user-item {
                position: relative;
                text-align: center;
            }

            /* 皇冠标识 */
            .hot-crown {
                position: absolute;
                top: -10px;
                right: -5px;
                font-size: 24px;
                color: #ffd700;
                filter: drop-shadow(0 2px 2px rgba(0,0,0,0.3));
            }
            </style>
        </head>
        <body>
            <header>
                <h1>[群/用户名称]日报</h1>
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
                    <!-- 在这里填充讨论热点内容 -->

                    <!-- 复制上述卡片结构添加更多话题 -->
                </div>
            </section>

            <!-- 2. 实用教程与资源分享 -->
            <section class="tutorials">
                <h2>实用教程与资源分享</h2>
                <div class="tutorials-container">
                    <!-- 在这里填充教程和资源内容，严格按照以下格式 -->
                    <!-- 在这里填充教程和资源内容 -->

                    <!-- 复制上述卡片结构添加更多资源 -->
                </div>
            </section>

            <!-- 3. 重要消息汇总 -->
            <section class="important-messages">
                <h2>重要消息汇总</h2>
                <div class="messages-container">
                    <!-- 在这里填充重要消息内容，严格按照以下格式 -->
                    <!-- 在这里填充重要消息内容 -->

                    <!-- 复制上述卡片结构添加更多消息 -->
                </div>
            </section>

            <!-- 4. 有趣对话或金句 -->
            <section class="interesting-dialogues">
                <h2>有趣对话或金句</h2>
                <div class="dialogues-container">
                    <!-- 在这里填充对话内容，严格按照以下格式 -->
                    <!-- 在这里填充对话内容 -->

                    <!-- 复制上述卡片结构添加更多对话 -->
                </div>
            </section>

            <!-- 5. 问题与解答 -->
            <section class="questions-answers">
                <h2>问题与解答</h2>
                <div class="qa-container">
                    <!-- 在这里填充问答内容，严格按照以下格式 -->
                    <!-- 在这里填充问答内容 -->

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

                    <!-- 复制上述结构添加更多热度项，每项使用不同颜色 -->
                    <!-- 在这里填充话题热度数据 -->

                    <!-- 可用的颜色: #3da9fc, #f25f4c, #7209b7, #e53170, #00b4d8, #4cc9f0 -->
                </div>

                <!-- 话唠榜 -->
                 <!-- 在话唠榜添加头像 -->
            <section class="analytics">
                <h3>话唠榜</h3>
                <div class="participants-container">
                <!-- 在这里填充话唠榜数据 -->

                </div>
            </section>


                <!-- 熬夜冠军 -->
                <h3>熬夜冠军</h3>
                <div class="night-owls-container">
                    <!-- 在这里填充熬夜冠军数据，严格按照以下格式 -->
                     <!-- 在这里填充熬夜冠军内容 -->

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
                        <!-- 在这里填充词云内容 -->

                        <!-- 继续添加更多词 -->
                    </div>

                    <div class="cloud-legend">

                    <!-- 在这里填充词云分类内容 -->

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
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // 获取所有词云元素
                    const cloudWords = document.querySelectorAll('.cloud-word');
                    const container = document.querySelector('.cloud-wordcloud');
                    const containerWidth = container.offsetWidth;
                    const containerHeight = container.offsetHeight;

                    // 为每个词云元素设置随机位置
                    cloudWords.forEach(word => {
                        const wordWidth = word.offsetWidth;
                        const wordHeight = word.offsetHeight;


                        // 计算随机位置，确保词云元素不会超出容器边界
                        const randomLeft = Math.random() * (containerWidth - wordWidth);
                        const randomTop = Math.random() * (containerHeight - wordHeight);

                        // 设置位置
                        word.style.left = `${randomLeft}px`;
                        word.style.top = `${randomTop}px`;

                        // 添加悬停效果
                        word.addEventListener('mouseover', function() {
                            this.style.transform = 'scale(1.1)';
                            this.style.zIndex = '10';
                        });

                        word.addEventListener('mouseout', function() {
                            this.style.transform = 'scale(1)';
                            this.style.zIndex = '1';
                        });
                    });
                });
            </script>

        </html>
            """

        json_data = json_data[7:-3]
        # 清洗json_data
        # 判断是否是转义的换行符
        if '\n' in json_data:
            json_data = json_data.replace('\n', '\n')


        else:
            json_data = json_data.replace(r'\"', '"').replace(r"\n", '\n')

        # print(json_data)

        # 使用正则表达式查找json字符串
        pattern = re.compile('{.*}', flags=re.IGNORECASE | re.MULTILINE | re.S)
        print(pattern.search(json_data).group())

        json_data = json.loads(pattern.search(json_data).group())
        # json_data = json.loads(json_data)

        # print(json_data)

        # print(json.dumps(json_data,indent=4, ensure_ascii=False))

        # 替换头部信息
        header = json_data['header']
        html = html.replace('[群/用户名称]日报', f"{header['title']}报告")
        html = html.replace('[日期]', header['date'])
        html = html.replace('总消息数：[数量]', f"总消息数：{header['metaInfo']['totalMessages']}")
        html = html.replace('活跃用户：[数量]', f"活跃用户：{header['metaInfo']['activeUsers']}")
        html = html.replace('时间范围：[时间范围]', f"时间范围：{header['metaInfo']['timeRange']}")

        # 处理热点话题
        hot_topics = []
        for topic in json_data['sections']['hotTopics']['items']:
            keywords = ''.join([f'<span class="keyword">{kw}</span>' for kw in topic['keywords']])
            hot_topics.append(f"""
                <div class="topic-card">
                    <h3>{topic['name']}</h3>
                    <div class="topic-category">{topic['category']}</div>
                    <p class="topic-summary">{topic['summary']}</p>
                    <div class="topic-keywords">
                        {keywords}
                    </div>
                    <div class="topic-mentions">提及次数：{topic['mentions']}</div>
                </div>""")
        html = html.replace('<!-- 在这里填充讨论热点内容 -->', '\n'.join(hot_topics))

        # 处理教程资源
        tutorials = []
        for tut in json_data['sections']['tutorials']['items']:
            points = ''.join([f'<li>{p}</li>' for p in tut['keyPoints']])
            tutorials.append(f"""
                <div class="tutorial-card">
                    <div class="tutorial-type">{tut['type']}</div>
                    <h3>{tut['title']}</h3>
                    <div class="tutorial-meta">
                        <span class="shared-by">分享者：{tut['sharedBy']}</span>
                        <span class="share-time">时间：{tut['time']}</span>
                    </div>
                    <p class="tutorial-summary">{tut['summary']}</p>
                    <div class="key-points">
                        <h4>要点：</h4>
                        <ul>{points}</ul>
                    </div>
                    <div class="tutorial-link">
                        <a href="{tut['url']}" class="link valid">查看原文: {tut['domain']}</a>
                    </div>
                    <div class="tutorial-category">分类：{tut['category']}</div>
                </div>""")
        html = html.replace('<!-- 在这里填充教程和资源内容 -->', '\n'.join(tutorials))

        # 处理重要消息
        messages = []
        for msg in json_data['sections']['importantMessages']['items']:
            messages.append(f"""
                <div class="message-card">
                    <div class="message-meta">
                        <span class="time">{msg['time']}</span>
                        <span class="sender">{msg['sender']}</span>
                        <span class="message-type">{msg['type']}</span>
                        <span class="priority priority-{msg['priority']}">优先级：{msg['priority']}</span>
                    </div>
                    <p class="message-content">{msg['content']}</p>
                    <div class="message-full-content">
                        <p>{msg['fullContent']}</p>
                    </div>
                </div>""")
        html = html.replace('<!-- 在这里填充重要消息内容 -->', '\n'.join(messages))

        # 处理对话
        dialogues = []
        for dia in json_data['sections']['dialogues']['items']:
            messages = ''.join([f"""
                <div class="message">
                    <div class="message-meta">
                        <span class="speaker">{m['speaker']}</span>
                        <span class="time">{m['time']}</span>
                    </div>
                    <p class="message-content">{m['content']}</p>
                </div>""" for m in dia['messages']])
            dialogues.append(f"""
                <div class="dialogue-card">
                    <div class="dialogue-type">{dia['type']}</div>
                    <div class="dialogue-content">
                        {messages}
                    </div>
                    <div class="dialogue-highlight">{dia['highlight']}</div>
                    <div class="dialogue-topic">相关话题：{dia['relatedTopic']}</div>
                </div>""")
        html = html.replace('<!-- 在这里填充对话内容 -->', '\n'.join(dialogues))

        # 处理问答
        qas = []
        for qa in json_data['sections']['qa']['items']:
            tags = ''.join([f'<span class="tag">{tag}</span>' for tag in qa['question']['tags']])
            answers = ''.join([f"""
                <div class="answer">
                    <div class="answer-meta">
                        <span class="responder">{ans['responder']}</span>
                        <span class="time">{ans['time']}</span>
                        {"<span class='accepted-badge'>最佳回答</span>" if ans['isAccepted'] else ""}
                    </div>
                    <p class="answer-content">{ans['content']}</p>
                </div>""" for ans in qa['answers']])
            qas.append(f"""
                <div class="qa-card">
                    <div class="question">
                        <div class="question-meta">
                            <span class="asker">{qa['question']['asker']}</span>
                            <span class="time">{qa['question']['time']}</span>
                        </div>
                        <p class="question-content">{qa['question']['content']}</p>
                        <div class="question-tags">
                            {tags}
                        </div>
                    </div>
                    <div class="answers">
                        {answers}
                    </div>
                </div>""")
        html = html.replace('<!-- 在这里填充问答内容 -->', '\n'.join(qas))

        # 处理数据可视化
        heatmap = []
        colors = ['#3da9fc', '#f25f4c', '#7209b7', '#e53170', '#00b4d8', '#4cc9f0']
        for i, topic in enumerate(json_data['sections']['analytics']['heatmap']):
            color = colors[i % len(colors)]
            heatmap.append(f"""
                <div class="heat-item">
                    <div class="heat-topic">{topic['topic']}</div>
                    <div class="heat-percentage">{topic['percentage']}%</div>
                    <div class="heat-bar">
                        <div class="heat-fill" style="width: {topic['percentage']}%; background-color: {color};"></div>
                    </div>
                    <div class="heat-count">{topic['count']}条消息</div>
                </div>""")
        html = html.replace('<!-- 在这里填充话题热度数据 -->', '\n'.join(heatmap))

        # 处理话唠榜
        chatty = []
        for rank in json_data['sections']['analytics']['chattyRanking']:
            words = ''.join([f'<span class="word">{w}</span>' for w in rank['commonWords']])
            characteristics = ''.join([f'<span class="characteristic">{c}</span>' for c in rank['characteristics']])
            chatty.append(f"""
                <div class="participant-item">
                    <div class="participant-rank">{rank['rank']}</div>
                    <div class="participant-info">
                        <div class="participant-name">{rank['name']}</div>
                        <div class="participant-count">发言数：{rank['count']}</div>
                        <div class="participant-characteristics">
                            {characteristics}
                        </div>
                        <div class="participant-words">
                            {words}
                        </div>
                    </div>
                </div>""")
        html = html.replace('<!-- 在这里填充话唠榜数据 -->', '\n'.join(chatty))

        # 处理熬夜冠军
        nightOwl = json_data['sections']['analytics']['nightOwl']

        f = f"""
            <div class="night-owl-item">
                        <div class="owl-crown" title="熬夜冠军">👑</div>
                 <div class="owl-info">
                            <div class="owl-name">{nightOwl['name']}</div>
                            <div class="owl-title">{nightOwl['title']}</div>
                            <div class="owl-time">最晚活跃时间：{nightOwl['latestTime']}</div>
                            <div class="owl-messages">深夜消息数：{nightOwl['messageCount']}</div>
                            <div class="owl-last-message">{nightOwl['lastMessage']}</div>
                            <div class="owl-note">注：熬夜时段定义为23:00-06:00，已考虑不同时区</div>
                        </div>"""

        html = html.replace('<!-- 在这里填充熬夜冠军内容 -->', '\n' + f + '\n')

        # 处理词云
        words = []
        for word in json_data['sections']['wordCloud']['words']:
            words.append(f"""
                <span class="cloud-word" style="left: {word.get('x', 300)}px; top: {word.get('y', 120)}px; 
                    font-size: {word['size']}px; color: {word['color']}; 
                    transform: rotate({word['rotation']}deg);">{word['text']}</span>""")
        html = html.replace('<!-- 在这里填充词云内容 -->', '\n'.join(words))

        # 处理词云的分类
        types = []
        for typ in json_data['sections']['wordCloud']['legend']:
            types.append(f""" <div class="legend-item">
                            <span class="legend-color" style="background-color: {typ['color']};"></span>
                            <span class="legend-label">{typ['label']}</span>
                        </div>
                        """
                         )

        html = html.replace('<!-- 在这里填充词云分类内容 -->', '\n'.join(types))

        # 处理页脚
        footer = json_data['footer']
        html = html.replace('[群名称]', footer['dataSource'])
        html = html.replace('[当前时间]', footer['generationTime'])
        html = html.replace('[日期] [时间范围]', footer['statisticalPeriod'])

        return html