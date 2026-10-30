export const topics = {
  models: { title: '模型发布', description: '模型能力、评测与推理效率的持续变化。', tags: ['大模型', '模型评估'], terms: ['模型', 'GPT', 'Gemini', 'Claude'] },
  agents: { title: '智能体', description: '智能体工具、工作流与自主执行能力。', tags: ['智能体'], terms: ['智能体', 'Agent'] },
  enterprise: { title: '企业应用', description: 'AI 在组织、桌面与专业流程中的落地。', tags: ['企业应用', '桌面应用'], terms: ['企业', '部署', '工作流'] },
  open_source: { title: '开源工具', description: '可用的开源模型、开发工具与社区项目。', tags: ['开源'], terms: ['开源', 'GitHub'] },
  research: { title: '科研进展', description: '论文、方法与可复现的研究成果。', tags: ['科研'], terms: ['研究', '论文', '评估'] },
  safety: { title: 'AI 安全', description: '安全评估、治理、对齐与可靠部署。', tags: [], terms: ['安全', '治理', '漏洞', '验证'] },
} as const;

export type TopicSlug = keyof typeof topics;

export function matchesTopic(entry: { data: { tags: string[]; title: string }; body?: string }, topic: TopicSlug) {
  const definition = topics[topic];
  const haystack = `${entry.data.title}\n${entry.body ?? ''}`.toLowerCase();
  return entry.data.tags.some((tag) => definition.tags.includes(tag as never))
    || definition.terms.some((term) => haystack.includes(term.toLowerCase()));
}
