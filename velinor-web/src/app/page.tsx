'use client';

import TitleScreen from '@/components/TitleScreen';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleGameStart = (playerName: string) => {
    router.push(`/game/velhara_market?player=${encodeURIComponent(playerName)}`);
  };

  return <TitleScreen onGameStart={handleGameStart} />;
}
