# Deal Co-Pilot - Next.js Frontend

Modern, professional SaaS frontend built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

- **Modern UI** - Beautiful gradient design with smooth animations
- **Next.js 15** - Latest features with App Router
- **Tailwind CSS** - Utility-first styling
- **Fully Responsive** - Works on all devices
- **Real-time Updates** - Progress tracking with polling
- **Natural Language** - Simple, intuitive input
- **Beautiful Reports** - Professional formatting with citations

## Tech Stack

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles & Tailwind
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page
├── components/
│   ├── Header.tsx           # Navigation header
│   ├── HeroSection.tsx      # Input form
│   ├── LoadingSection.tsx   # Progress tracking
│   └── ResultsSection.tsx   # Report display
├── lib/
│   ├── api.ts               # API client functions
│   └── types.ts             # TypeScript types
├── public/                  # Static assets
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── tailwind.config.ts       # Tailwind config
└── next.config.ts           # Next.js config
```

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Open browser
open http://localhost:3000
```

### Production

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Configuration

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Proxy

The Next.js config includes automatic API proxying:

```typescript
// next.config.ts
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ];
}
```

### Tailwind Customization

Edit `tailwind.config.ts`:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#6366f1',  // Change primary color
      },
    },
  },
}
```

## Components

### Header
Navigation bar with logo and links.

### HeroSection
- Natural language input textarea
- Agent type selector (OpenAI/Gemini)
- Example prompt chips
- Submit button

### LoadingSection
- Animated spinner
- Progress bar (0-100%)
- Status messages
- Company info display

### ResultsSection
- Report header with metadata
- Download & new research buttons
- Formatted sections with icons
- Inline citations as links

## API Integration

### Create Research

```typescript
import { createResearch } from "@/lib/api";

const response = await createResearch(
  "Research Bizzi, SaaS, Vietnam, https://bizzi.vn/en/",
  "openai"
);
```

### Poll Status

```typescript
import { checkStatus } from "@/lib/api";

const status = await checkStatus(reportId);
```

### Get Report

```typescript
import { getReport } from "@/lib/api";

const report = await getReport(reportId);
```

### Download Report

```typescript
import { downloadReport } from "@/lib/api";

downloadReport(reportId, companyName);
```

## Key Features

### Real-time Progress

The app polls the backend every 2 seconds for status updates:

```typescript
const pollInterval = setInterval(async () => {
  const status = await checkStatus(reportId);
  if (status.status === "completed") {
    clearInterval(pollInterval);
    // Fetch and display report
  }
}, 2000);
```

### Formatted Content

Reports are formatted with:
- Bold text (**text**)
- Headings (##, ###)
- Bullet lists (-)
- Inline citations [Source: URL]

```typescript
function formatContent(content: string): string {
  // Convert markdown-like syntax to HTML
  // Add proper styling classes
  return formattedHTML;
}
```

### Responsive Design

- Mobile: Single column, stacked buttons
- Tablet: Optimized layouts
- Desktop: Full multi-column layouts

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Set environment variable in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` = your backend URL

### Docker

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Nginx

```nginx
server {
  listen 80;
  server_name yourdomain.com;

  location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
  }
}
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### API Connection Issues

Check that:
1. Backend is running on port 8000
2. `NEXT_PUBLIC_API_URL` is set correctly
3. CORS is enabled in FastAPI backend

### Build Errors

```bash
# Clear cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## Performance

- **First Load**: ~150-200ms
- **Route Changes**: ~50ms (client-side)
- **API Calls**: ~2-5 min (research generation)

## Security

### Production Checklist

- [ ] Set proper `NEXT_PUBLIC_API_URL`
- [ ] Enable HTTPS
- [ ] Add CSP headers
- [ ] Implement rate limiting
- [ ] Add authentication (if needed)
- [ ] Use environment secrets

## Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
```

## Contributing

1. Create a new component in `components/`
2. Add types to `lib/types.ts`
3. Use Tailwind classes for styling
4. Follow the existing component patterns

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [TypeScript](https://www.typescriptlang.org/)
- [Lucide Icons](https://lucide.dev/)

---

**Built with love using Next.js, TypeScript, and Tailwind CSS**

