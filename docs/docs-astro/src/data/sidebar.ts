export interface SidebarItem {
  label: string;
  slug: string;
}

export interface SidebarGroup {
  label: string;
  items: SidebarItem[];
}

export type SidebarEntry = SidebarGroup | SidebarItem;

function isGroup(entry: SidebarEntry): entry is SidebarGroup {
  return 'items' in entry;
}

export { isGroup };

export const sidebar: SidebarEntry[] = [
  {
    label: 'Getting Started',
    items: [
      { label: 'Installation', slug: 'getting-started/installation' },
      { label: 'Quick Start', slug: 'getting-started/quickstart' },
      { label: 'Why EVOID?', slug: 'getting-started/why-evoid' },
      { label: 'What is IOP?', slug: 'getting-started/what-is-iop' },
    ],
  },
  {
    label: 'Learn',
    items: [
      { label: 'Intent', slug: 'learn/intent' },
      { label: 'Pipeline', slug: 'learn/pipeline' },
      { label: 'Processors', slug: 'learn/processors' },
      { label: 'Plugins', slug: 'learn/plugins' },
      { label: 'Configuration', slug: 'learn/configuration' },
    ],
  },
  {
    label: 'Syntax Styles',
    items: [
      { label: '@route', slug: 'styles/route' },
      { label: '@controller', slug: 'styles/controller' },
      { label: 'Native', slug: 'styles/native' },
    ],
  },
  {
    label: 'Tutorial',
    items: [
      { label: 'First Steps', slug: 'tutorial/first-steps' },
      { label: 'Path Parameters', slug: 'tutorial/path-params' },
      { label: 'Query Parameters', slug: 'tutorial/query-params' },
      { label: 'Request Body', slug: 'tutorial/request-body' },
      { label: 'Response Status Code', slug: 'tutorial/response-status-code' },
      { label: 'Body Multiple Parameters', slug: 'tutorial/body-multiple-params' },
      { label: 'Handling Errors', slug: 'tutorial/handling-errors' },
      { label: 'Path Operation Config', slug: 'tutorial/path-operation-config' },
      { label: 'Bigger Applications', slug: 'tutorial/bigger-applications' },
      { label: 'Metadata', slug: 'tutorial/metadata' },
      { label: 'Testing', slug: 'tutorial/testing' },
      { label: 'Intent Levels', slug: 'tutorial/intent-levels' },
      { label: 'Pipeline Extensions', slug: 'tutorial/pipeline-extensions' },
      { label: 'Pipeline Inspection', slug: 'tutorial/pipeline-inspection' },
      { label: 'Parallel Execution', slug: 'tutorial/parallel' },
      { label: 'Inter-Service Communication', slug: 'tutorial/messaging' },
      { label: 'Microservices Without Overhead', slug: 'tutorial/microservices' },
      { label: 'Custom Processors', slug: 'tutorial/custom-processors' },
      { label: 'Controller Style', slug: 'tutorial/controller-style' },
      { label: 'Native IOP', slug: 'tutorial/native-iop' },
    ],
  },
  {
    label: 'Validation & Serialization',
    items: [
      { label: 'Query Param Models', slug: 'tutorial/query-param-models' },
      { label: 'Body Fields', slug: 'tutorial/body-fields' },
      { label: 'Body Nested Models', slug: 'tutorial/body-nested-models' },
      { label: 'Schema Examples', slug: 'tutorial/schema-examples' },
      { label: 'Extra Data Types', slug: 'tutorial/extra-data-types' },
      { label: 'JSON Encoder', slug: 'tutorial/json-encoder' },
      { label: 'Body Updates', slug: 'tutorial/body-updates' },
      { label: 'Validation', slug: 'tutorial/validation' },
      { label: 'Serialization', slug: 'tutorial/serialization' },
      { label: 'Debugging', slug: 'tutorial/debugging' },
    ],
  },
  {
    label: 'Web Adapter Patterns',
    items: [
      { label: 'Custom Adapters', slug: 'tutorial/custom-adapters' },
      { label: 'Cookie Parameters', slug: 'tutorial/cookie-params' },
      { label: 'Header Parameters', slug: 'tutorial/header-params' },
      { label: 'Form Data', slug: 'tutorial/form-data' },
      { label: 'File Upload', slug: 'tutorial/file-upload' },
      { label: 'CORS', slug: 'tutorial/cors' },
      { label: 'Static Files', slug: 'tutorial/static-files' },
      { label: 'Streaming', slug: 'tutorial/streaming' },
    ],
  },
  {
    label: 'Patterns',
    items: [
      { label: 'Dependency Injection', slug: 'tutorial/dependency-injection' },
      { label: 'Middleware Patterns', slug: 'tutorial/middleware-patterns' },
      { label: 'Response Validation', slug: 'tutorial/response-validation' },
    ],
  },
  { label: 'API Reference', slug: 'api' },
  { label: 'Examples', slug: 'examples' },
];

/** Flatten all sidebar entries into an ordered list of slugs for prev/next */
export function getAllSlugs(): string[] {
  const slugs: string[] = [];
  for (const entry of sidebar) {
    if (isGroup(entry)) {
      for (const item of entry.items) {
        slugs.push(item.slug);
      }
    } else {
      slugs.push(entry.slug);
    }
  }
  return slugs;
}
