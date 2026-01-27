import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center max-w-2xl">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
          IBKR Portfolio Manager
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600 dark:text-gray-300">
          A modern portfolio management interface for Interactive Brokers.
          Organize your investments with pies and slices, set up auto-invest,
          and build positions with smart triggers.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            href="/dashboard"
            className="btn-primary"
          >
            Get Started
          </Link>
          <Link
            href="/docs"
            className="text-sm font-semibold leading-6 text-gray-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400"
          >
            Learn more <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl">
        <FeatureCard
          title="Pie & Slice Structure"
          description="Organize your portfolio into themed pies with weighted slices for easy management."
        />
        <FeatureCard
          title="Auto-Invest"
          description="Automatically allocate deposits across your portfolio based on target weights."
        />
        <FeatureCard
          title="Position Building"
          description="Build positions gradually using time-based, price-based, or technical triggers."
        />
      </div>
    </main>
  );
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{description}</p>
    </div>
  );
}
