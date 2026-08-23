import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        /** Emit `noindex,nofollow` instead of `index,follow`. The four legal
         *  drafts and the 404 use this; nothing else should. */
        noindex: z.boolean().default(false),
        /** Paint the legal review-draft band above the article. */
        legalDraft: z.boolean().default(false),
      }),
    }),
  }),
};
