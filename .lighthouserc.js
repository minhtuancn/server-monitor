module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:9081/en/login',
        'http://localhost:9081/en/dashboard',
      ],
      numberOfRuns: 1,
      settings: {
        // Skip PWA checks (not applicable for this app)
        skipAudits: ['service-worker', 'installable-manifest', 'apple-touch-icon'],
      },
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.7 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.8 }],
        'categories:seo': ['warn', { minScore: 0.8 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
