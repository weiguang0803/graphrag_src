# -*- coding: utf-8 -*-
"""
在 Windows 机器上运行：把 graphrag_src/prompts/ 下所有 prompt 文件
替换为中文版，并先把原版备份为 *.en.bak。

"""
from pathlib import Path
import shutil

PROMPTS = Path(r"C:\Users\15922\Desktop\llm\graphrag\graphrag_src\prompts")
if not PROMPTS.exists():
    raise SystemExit(f"找不到 prompts 目录: {PROMPTS}")

def write(name: str, content: str):
    p = PROMPTS / name
    if not p.exists():
        print(f"[跳过-不存在] {name}")
        return
    bak = p.with_suffix(p.suffix + ".en.bak")
    if not bak.exists():
        shutil.copy2(p, bak)
        print(f"[备份] {name} -> {bak.name}")
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[写入中文版] {name}")

# ---------- 1. extract_graph.txt ----------
write("extract_graph.txt", r"""你是一个专门从文本中抽取实体和关系的AI助手。请从下面的文本中识别出实体及其之间的关系。

实体类型限定为：organization（组织）、person（人物）、geo（地点）、event（事件）。

要求：
1. 尽可能多地识别出实体和关系。
2. 为每个实体和关系写一段简短、准确的中文描述。
3. 以 JSON 格式输出。注意：JSON 的 key（如 "name"、"type"、"description"、"source"、"target"、"weight"）必须保持英文，不要翻译 key 名。

输出 JSON 格式示例：
{
  "entities": [
    {"name": "实体名", "type": "实体类型", "description": "实体描述"}
  ],
  "relationships": [
    {"source": "源实体名", "target": "目标实体名", "description": "关系描述", "weight": 1}
  ]
}

如果文本中没有找到任何实体或关系，输出空的 JSON：{"entities": [], "relationships": []}

重要：只输出纯 JSON，不要输出任何 JSON 以外的文字，不要加"好的""以下是结果"等前缀或解释。

------文本开始------
{input_text}
------文本结束------
""")

# ---------- 2. summarize_descriptions.txt ----------
write("summarize_descriptions.txt", r"""请为下面给出的实体或关系生成一段简洁、准确、通顺的中文描述。描述应基于提供的上下文，突出该实体/关系的核心特征与重要性。

上下文：
{context}

实体/关系名称：{entity_title}

请直接输出描述文本，不要加任何前缀、标题或解释。
""")

# ---------- 3. community_report_graph.txt ----------
write("community_report_graph.txt", r"""你是一个知识图谱分析助手。下面给出的是一个"社区"（一组高度相关的实体及其关系）的结构化信息。请基于这些信息，为这个社区撰写一份综合的、可读性强的中文报告，概括该社区的主题、核心实体、实体间的关系以及整体语义。

要求：
1. 报告用中文撰写，结构清晰。
2. 先给出一段总体概述，再分点介绍核心实体及其关系。
3. 如果信息不足以形成报告，如实说明。

社区结构化信息（JSON）：
{input_text}
""")

# ---------- 4. community_report_text.txt ----------
write("community_report_text.txt", r"""你是一个知识图谱分析助手。下面给出的是与某个社区相关的原始文本块。请基于这些文本，为这个社区撰写一份综合的、可读性强的中文报告，概括该社区的主题、关键事实和实体关联。

要求：
1. 报告用中文撰写，结构清晰。
2. 聚焦文本中实际出现的信息，不要臆造。
3. 先给出总体概述，再分点列出关键事实。

社区相关文本：
{input_text}
""")

# ---------- 5. local_search_system_prompt.txt ----------
write("local_search_system_prompt.txt", r"""你是一个专门基于知识图谱和检索文本回答问题的AI助手。你会收到：
1. 与问题相关的实体及其关系描述（来自知识图谱）
2. 相关的原文文本块（来自向量检索）
3. 对话历史（如果有）

请基于以上信息，用中文给出准确、详细、有据可依的回答。
- 优先使用提供的信息；信息足够时给出明确结论。
- 如果提供的信息不足以回答问题，请诚实说明"根据现有资料无法回答"，不要编造。
- 回答应条理清晰，必要时分点说明。
""")

# ---------- 6. global_search_map_system_prompt.txt ----------
write("global_search_map_system_prompt.txt", r"""你是一个分析助手，正在参与"全局搜索"。系统会把若干段"社区报告"逐段发给你，你需要评估：这段报告是否包含回答用户问题所需的信息。

要求：
- 如果这段报告包含相关信息，请用中文写一段简要的"要点摘要"，帮助最终回答用户问题，并在 JSON 中给出 0-100 的相关度评分。
- 如果这段报告与问题无关，输出空要点并在 JSON 中给出 0 分。

你必须严格以 JSON 格式输出，key 保持英文，例如：
{"score": 75, "points": ["要点1", "要点2"]}

不要输出任何 JSON 以外的文字。

用户问题：{question}
待评估的社区报告：
{context}
""")

# ---------- 7. global_search_reduce_system_prompt.txt ----------
write("global_search_reduce_system_prompt.txt", r"""你是一个综合回答助手。系统已经对多份"社区报告"做了初步评估，并收集了若干候选要点（每条含相关度评分和内容）。请综合这些候选要点，用中文回答用户的问题。

要求：
1. 优先采信评分高、信息明确的要点。
2. 将相关信息组织成一篇连贯、有条理的中文回答。
3. 如果所有候选要点都不足以回答问题，请如实说明。

用户问题：{question}

候选要点（JSON 数组，每项含 score 与 points）：
{context}
""")

# ---------- 8. global_search_knowledge_system_prompt.txt ----------
write("global_search_knowledge_system_prompt.txt", r"""你是一个知识补充助手。在全局搜索的最后阶段，系统已生成一份基于社区报告的初步回答。请结合你自身的可靠知识，对回答中涉及的事实进行核对与适度补充，并用中文输出最终完善后的回答。

要求：
- 补充内容应确凿有据；不确定的地方不要编造。
- 保持回答条理清晰、语言通顺。

用户问题：{question}

初步回答：
{context}
""")

# ---------- 9. drift_search_system_prompt.txt ----------
write("drift_search_system_prompt.txt", r"""你是一个支持"探索式问答"的AI助手。用户会提出一个问题，你可以基于知识图谱检索到的实体、关系和原文文本块进行多步、迭代式的探索，逐步澄清并回答用户问题。

要求：
- 用中文回答，条理清晰。
- 基于提供的信息作答；信息不足时如实说明，并给出可以进一步追问的方向。
""")

# ---------- 10. drift_reduce_prompt.txt ----------
write("drift_reduce_prompt.txt", r"""下面是对用户问题进行多步探索后收集到的若干候选回答/要点。请综合这些候选内容，去重、整合，用中文输出一份最终、连贯的回答。

要求：
- 保留确凿、相关的信息，剔除重复或矛盾的内容。
- 回答应条理清晰、语言通顺。

候选内容：
{context}
""")

# ---------- 11. basic_search_system_prompt.txt ----------
write("basic_search_system_prompt.txt", r"""你是一个基于检索文本回答问题的AI助手。系统已根据用户问题检索出若干相关文本块。请基于这些文本块，用中文给出准确、详细的回答。

要求：
- 优先依据检索到的文本作答；文本不足以回答时，如实说明。
- 不要编造文本中不存在的信息。
- 回答条理清晰，必要时分点说明。
""")

# ---------- 12. basic_context_system_prompt.txt ----------
write("basic_context_system_prompt.txt", r"""以下是与用户问题相关的检索文本块，供你参考和引用：

{context}

请基于以上内容，用中文回答用户的问题。如信息不足，请如实说明。
""")

# ---------- 13. extract_claims.txt ----------
write("extract_claims.txt", r"""你是一个信息抽取助手。请从下面的文本中抽取"声明/事实性主张"（claims）——即那些可能对信息发现、实体属性或关系推理有价值的陈述。

要求：
1. 以 JSON 格式输出，key 保持英文。
2. 每条 claim 包含：subject（主体）、object（客体，可选）、type（主张类型）、description（主张的中文描述）、score（0-1 的可信度）。
3. 只抽取文本中实际出现、可支持的主张；不要臆造。

输出格式示例：
{"claims": [{"subject": "主体", "type": "主张类型", "description": "主张描述", "score": 0.9}]}
若没有合适的主张，输出 {"claims": []}。

文本：
{input_text}
""")

# ---------- 14. question_gen_system_prompt.txt ----------
write("question_gen_system_prompt.txt", r"""你是一个问题生成助手。给定一段文本（或一组文本块），请生成若干能够考察读者对该文本理解程度的中文问题。问题应具体、可回答，并覆盖文本中的关键事实与关系。

要求：
- 每个问题一行，简洁明确。
- 问题数量适中（3-6 个），聚焦核心内容。

文本：
{input_text}
""")

print("\n全部处理完成。原版已备份为 *.en.bak（如已存在则不再覆盖）。")
print("下一步：清空缓存并重新索引 ——")
print('  Remove-Item -Recurse -Force cache, output, logs')
print('  uv run poe index --root .')
""")
"""
print("脚本已生成，请在 Windows 上运行：python apply_chinese_prompts.py")
