'use client';

import { Button } from 'antd';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">WriteWorld</h1>
      <div className="flex gap-4">
        <Button
          type="primary"
          onClick={() => router.push('/translation')}
        >
          翻译
        </Button>
        <Button disabled>写作</Button>
      </div>
    </main>
  );
}
