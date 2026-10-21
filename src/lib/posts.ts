import { getCollection, type CollectionEntry } from 'astro:content';
import type { Lang } from './i18n';

export type Post = CollectionEntry<'posts'>;

export function slugOf(post: Post): string {
  return post.id.split('/').pop()!.replace(/\.md$/, '');
}

export async function getPosts(lang: Lang): Promise<Post[]> {
  const posts = await getCollection('posts', ({ id }) => id.startsWith(lang + '/'));
  return posts.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

/** 找同一篇文章的另一语言版本 */
export async function findTranslation(lang: Lang, slug: string): Promise<Post | undefined> {
  const other = lang === 'zh' ? 'en' : 'zh';
  const posts = await getCollection('posts', ({ id }) => id.startsWith(other + '/' + slug + '.md'));
  return posts[0];
}
