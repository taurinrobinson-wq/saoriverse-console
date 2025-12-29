"use client";

import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';

const BossFight = dynamic(() => import('@/components/BossFight'), { ssr: false });

export default function BossTestPage() {
    const router = useRouter();

    return (
        <div style={{ width: '100%', minHeight: '100vh', background: '#000', padding: 24 }}>
            <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
                <button onClick={() => router.push('/')} style={{ padding: '8px 12px', borderRadius: 8 }}>Back</button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
                <div style={{ width: '100%', maxWidth: 1200 }}>
                    <BossFight />
                </div>
            </div>
        </div>
    );
}
