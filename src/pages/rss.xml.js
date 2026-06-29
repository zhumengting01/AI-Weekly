import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const posts = await getCollection('posts');
  const weekly = await getCollection('weekly');
  
  // Combine and sort by date (most recent first)
  const allItems = [
    ...posts.map(post => ({
      ...post,
      type: 'post',
      link: `/posts/${post.id}/`
    })),
    ...weekly.map(post => ({
      ...post,
      type: 'weekly',
      link: `/weekly/${post.id}/`
    }))
  ].sort((a, b) => 
    new Date(b.data.date).valueOf() - new Date(a.data.date).valueOf()
  );
  
  return rss({
    title: 'AI Weekly',
    description: '每周精选 AI 领域热点新闻、工具推荐和开源项目',
    site: 'https://ai-weeklys.vercel.app/',
    items: allItems.map((item) => ({
      title: item.data.title,
      pubDate: item.data.date,
      description: item.data.excerpt,
      link: item.link,
    })),
    customData: `<language>zh-cn</language>`,
  });
}
