import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const weeklyCollection = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/weekly' }),
  schema: z.object({
    title: z.string(),
    date: z.date(),
    periodStart: z.date().optional(),
    periodEnd: z.date().optional(),
    updatedDate: z.date().optional(),
    excerpt: z.string(),
    takeaways: z.array(z.string()).max(3).optional(),
    readerFor: z.string().optional(),
    sourcesCount: z.number().int().positive().optional(),
    image: z.string().optional(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    editorNote: z.string().optional(),
    corrections: z.array(z.string()).optional(),
  }),
});

export const collections = {
  weekly: weeklyCollection,
};
