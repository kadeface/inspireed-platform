import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import MermaidComponent from './MermaidComponent.vue'

export interface MermaidOptions {
  HTMLAttributes: Record<string, any>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    mermaid: {
      /**
       * Insert a mermaid diagram
       */
      insertMermaid: (options: { code: string; type?: string }) => ReturnType
    }
  }
}

export const MermaidNode = Node.create<MermaidOptions>({
  name: 'mermaid',

  group: 'block',

  atom: true,

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  addAttributes() {
    return {
      code: {
        default: '',
      },
      type: {
        default: 'flowchart',
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="mermaid"]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', { 'data-type': 'mermaid', ...HTMLAttributes }]
  },

  addCommands() {
    return {
      insertMermaid:
        (options) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: options,
          })
        },
    }
  },

  addNodeView() {
    return VueNodeViewRenderer(MermaidComponent)
  },
})
