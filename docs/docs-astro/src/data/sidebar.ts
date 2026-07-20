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
      { label: 'Architecture', slug: 'getting-started/architecture' },
      { label: 'What is IOP?', slug: 'getting-started/what-is-iop' },
      { label: 'IOP Philosophy', slug: 'getting-started/iop-philosophy' },
      { label: 'Why EVOID?', slug: 'getting-started/why-evoid' },
      { label: 'EVOID vs Others', slug: 'getting-started/comparison' },
      { label: 'Deployment', slug: 'getting-started/deployment' },
      { label: 'FAQ', slug: 'getting-started/faq' },
      { label: 'Troubleshooting', slug: 'getting-started/troubleshooting' },
    ],
  },
  {
    label: 'Learn',
    items: [
      { label: 'Intent', slug: 'learn/intent' },
      { label: 'IOP Levels', slug: 'learn/iop-levels' },
      { label: 'Pipeline', slug: 'learn/pipeline' },
      { label: 'Processors', slug: 'learn/processors' },
      { label: 'Schema Export', slug: 'learn/schema-export' },
      { label: 'Plugin Hooks', slug: 'learn/plugin-hooks' },
      { label: 'Plugins', slug: 'learn/plugins' },
      { label: 'Plugin Ecosystem', slug: 'learn/plugin-ecosystem' },
      { label: 'Plugin Collection', slug: 'learn/plugin-collection' },
      { label: 'Plugin Standard', slug: 'learn/plugin-standard' },
      { label: 'Adapters', slug: 'learn/adapters' },
      { label: 'Testing', slug: 'learn/testing' },
      { label: 'Configuration', slug: 'learn/configuration' },
      { label: 'Python-Native Config', slug: 'learn/python-config' },
      { label: 'Security', slug: 'learn/security' },
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
    label: 'Tutorial: The Shop',
    items: [
      { label: 'Your First Intent', slug: 'tutorial/first-intent' },
      { label: 'The Menu', slug: 'tutorial/the-menu' },
      { label: 'Taking Orders', slug: 'tutorial/taking-orders' },
      { label: 'Kitchen Pipeline', slug: 'tutorial/kitchen-pipeline' },
      { label: 'Growing Pains', slug: 'tutorial/growing-pains' },
    ],
  },
  {
    label: 'Tutorial: Online Shop',
    items: [
      { label: 'Going Online', slug: 'tutorial/going-online' },
      { label: 'Menu API', slug: 'tutorial/menu-api' },
      { label: 'Order API', slug: 'tutorial/order-api' },
      { label: 'Validation', slug: 'tutorial/validation' },
      { label: 'Error Handling', slug: 'tutorial/error-handling' },
      { label: 'Dependency Injection', slug: 'tutorial/dependency-injection' },
      { label: 'Middleware', slug: 'tutorial/middleware' },
      { label: 'Status Codes', slug: 'tutorial/status-codes' },
      { label: 'Configuration', slug: 'tutorial/configuration' },
      { label: 'Testing', slug: 'tutorial/testing' },
      { label: 'Serialization', slug: 'tutorial/serialization' },
      { label: 'Shipping Online', slug: 'tutorial/shipping-online' },
    ],
  },
  {
    label: 'Tutorial: Franchise',
    items: [
      { label: 'Multi-Location', slug: 'tutorial/multi-location' },
      { label: 'Inter-Service', slug: 'tutorial/inter-service' },
      { label: 'Inventory Service', slug: 'tutorial/inventory-service' },
      { label: 'Real-time Updates', slug: 'tutorial/real-time' },
      { label: 'Plugin System', slug: 'tutorial/plugins' },
      { label: 'AI Analytics', slug: 'tutorial/ai-analytics' },
      { label: 'Parallel Orders', slug: 'tutorial/parallel-orders' },
      { label: 'Performance', slug: 'tutorial/performance' },
      { label: 'Production', slug: 'tutorial/production' },
      { label: "What's Next", slug: 'tutorial/whats-next' },
    ],
  },
  {
    label: 'Tutorial: Godot Games',
    items: [
      { label: 'Overview', slug: 'godot/overview' },
      { label: 'Shooter: Overview', slug: 'godot/shooter-overview' },
      { label: 'Shooter: Server', slug: 'godot/shooter-server' },
      { label: 'Shooter: Client', slug: 'godot/shooter-client' },
      { label: 'Shooter: Multiplayer', slug: 'godot/shooter-multiplayer' },
      { label: 'Shooter: Web Export', slug: 'godot/shooter-web' },
      { label: 'Tic-Tac-Toe: Overview', slug: 'godot/tictactoe-overview' },
      { label: 'Tic-Tac-Toe: Server', slug: 'godot/tictactoe-server' },
      { label: 'Tic-Tac-Toe: Client', slug: 'godot/tictactoe-client' },
      { label: 'Tic-Tac-Toe: Multiplayer', slug: 'godot/tictactoe-multiplayer' },
      { label: 'Tic-Tac-Toe: Web Deploy', slug: 'godot/tictactoe-web' },
    ],
  },
  {
    label: 'Reference',
    items: [
      { label: 'Cookie Parameters', slug: 'tutorial/cookie-params' },
      { label: 'Header Parameters', slug: 'tutorial/header-params' },
      { label: 'Form Data', slug: 'tutorial/form-data' },
      { label: 'File Upload', slug: 'tutorial/file-upload' },
      { label: 'CORS', slug: 'tutorial/cors' },
      { label: 'Static Files', slug: 'tutorial/static-files' },
      { label: 'Streaming', slug: 'tutorial/streaming' },
      { label: 'Custom Adapters', slug: 'tutorial/custom-adapters' },
    ],
  },
  { label: 'API Reference', slug: 'api' },
  { label: 'Examples', slug: 'examples' },
  { label: 'Changelog', slug: 'changelog' },
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
