// ==========================================
// File: src/App.tsx
// ==========================================
import React, { useState, useEffect } from 'react';
import {
 FiveElementsScore,
 ShanghanType,
 DailyQuest,
 Badge,
} from './types';
import {
 INITIAL_DAILY_QUESTS,
 INITIAL_BADGES,
 FIVE_ELEMENT_INFO,
 SHANGHAN_PROFILES,
} from './data/orientalData';

import { Header } from './components/Header';
import { QuestionnaireModal } from './components/QuestionnaireModal';
import { FiveElementsChart } from './components/FiveElementsChart';
import { ShanghanProfileCard } from './components/ShanghanProfile';
import { OrganClock } from './components/OrganClock';
import { YouTubeVideoSection } from './components/YouTubeVideoSection';
import { DailyQuestsAndFortune } from './components/DailyQuestsAndFortune';
import { AIConsultantModal } from './components/AIConsultantModal';
import { CodeCopyModal } from './components/CodeCopyModal';
import { copyAllCodeToClipboard } from './utils/codeCollector';
import { playClickSound } from './utils/sound';

import {
  Home,
  ArrowLeft,
 Sparkles,
  Code,
  Copy,
  Check,
 Award,
 HelpCircle,
 Bot,
 PieChart,
 BookOpen,
 Clock,
 PlaySquare,
 CheckSquare,
 Heart,
 ChevronRight,
 Flame,
 Utensils,
 Activity,
 ShieldCheck,
} from 'lucide-react';

export default function App() {
  const handleGoHome = () => {
    playClickSound();
    setActiveTab('dashboard');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
 // Persistence state in LocalStorage
 const [level, setLevel] = useState<number>(() => {
 const saved = localStorage.getItem('oriental_level');
 return saved ? parseInt(saved, 10) : 1;
 });

 const [xp, setXp] = useState<number>(() => {
 const saved = localStorage.getItem('oriental_xp');
 return saved ? parseInt(saved, 10) : 80;
 });

 const [streak, setStreak] = useState<number>(() => {
 const saved = localStorage.getItem('oriental_streak');
 return saved ? parseInt(saved, 10) : 3;
 });

 const [shanghanType, setShanghanType] = useState<ShanghanType>(() => {
 const saved = localStorage.getItem('oriental_shanghan');
 return (saved as ShanghanType) || 'taiyin';
 });

 const [fiveElements, setFiveElements] = useState<FiveElementsScore>(() => {
 const saved = localStorage.getItem('oriental_elements');
 return saved ? JSON.parse(saved) : { wood: 25, fire: 15, earth: 35, metal: 20, water: 25 };
 });

 const [quests, setQuests] = useState<DailyQuest[]>(() => {
 const saved = localStorage.getItem('oriental_quests');
 return saved ? JSON.parse(saved) : INITIAL_DAILY_QUESTS;
 });

 const [badges, setBadges] = useState<Badge[]>(INITIAL_BADGES);

 // Modals
 const [isQuizOpen, setIsQuizOpen] = useState(false);
 const [isAIConsultOpen, setIsAIConsultOpen] = useState(false);
  const [isCodeCopyOpen, setIsCodeCopyOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleDirectCopyCode = async () => {
    playClickSound();
    const success = await copyAllCodeToClipboard();
    if (success) {
      setToastMessage("✅ 全ソースコードをクリップボードにコピーしました！");
      setTimeout(() => setToastMessage(null), 3000);
    }
  };
  const [showFiveElements, setShowFiveElements] = useState(false);
 const [activeTab, setActiveTab] = useState<
 'dashboard' | 'elements' | 'shanghan' | 'clock' | 'youtube' | 'quests'
 >('dashboard');

 // Level XP calculations
 const maxXp = level * 300;

 // Save to localStorage
 useEffect(() => {
 localStorage.setItem('oriental_level', level.toString());
 localStorage.setItem('oriental_xp', xp.toString());
 localStorage.setItem('oriental_streak', streak.toString());
 localStorage.setItem('oriental_shanghan', shanghanType);
 localStorage.setItem('oriental_elements', JSON.stringify(fiveElements));
 localStorage.setItem('oriental_quests', JSON.stringify(quests));
 }, [level, xp, streak, shanghanType, fiveElements, quests]);

 // Level up handler
 const addXp = (amount: number) => {
 let newXp = xp + amount;
 let newLevel = level;
 let currentMax = newLevel * 300;

 while (newXp >= currentMax) {
 newXp -= currentMax;
 newLevel += 1;
 currentMax = newLevel * 300;
 }

 setXp(newXp);
 setLevel(newLevel);
 };

  const handleQuizComplete = (
    scores: FiveElementsScore,
    newShanghan: ShanghanType,
    earnedXp: number
  ) => {
    setFiveElements(scores);
    setShanghanType(newShanghan);
    addXp(earnedXp);
    setIsQuizOpen(false);
    setActiveTab('dashboard');

    setTimeout(() => {
      const el = document.getElementById('diagnosis-result-section');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 150);
  };

 const handleToggleQuest = (questId: string) => {
 setQuests((prev) =>
 prev.map((q) => {
 if (q.id === questId) {
 const nextState = !q.completed;
 if (nextState) {
 addXp(q.xpReward);
 }
 return { ...q, completed: nextState };
 }
 return q;
 })
 );
 };

 const getLevelTitle = (lvl: number) => {
 if (lvl >= 10) return '神農氏 (達人極意)';
 if (lvl >= 5) return '黄帝内経の弟子';
 if (lvl >= 3) return '傷寒論の智者';
 if (lvl >= 2) return '五行の調律師';
 return '養生見習い';
 };

 
  const renderBackToHomeHeader = (title: string) => (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-stone-800/80 mb-4">
      <button
        onClick={handleGoHome}
        className="px-4 py-2 rounded-xl bg-stone-900 hover:bg-stone-850 border border-amber-500/40 text-amber-300 font-bold text-xs sm:text-sm flex items-center gap-2 transition active:scale-95 cursor-pointer shadow-md"
      >
        <ArrowLeft className="w-4 h-4 text-amber-400" />
        <span>← トップページに戻る</span>
      </button>
      <span className="text-xs text-stone-400 font-bold">
        現在表示中: <span className="text-stone-200">{title}</span>
      </span>
    </div>
  );

  const renderBackToHomeFooter = () => (
    <div className="pt-6 border-t border-stone-800/80 flex justify-center">
      <button
        onClick={handleGoHome}
        className="px-6 py-3 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-stone-950 font-black text-xs sm:text-sm flex items-center justify-center gap-2 shadow-xl shadow-amber-950/40 transition active:scale-95 cursor-pointer border border-amber-300"
      >
        <Home className="w-4.5 h-4.5 text-stone-950" />
        <span>トップページ（総合ダッシュボード）に戻る</span>
      </button>
    </div>
  );

  const activeShanghanProfile = SHANGHAN_PROFILES[shanghanType];

 return (
 <div className="min-h-screen bg-stone-950 text-stone-100 font-sans selection:bg-amber-500 selection:text-stone-950 relative">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-amber-400 text-stone-950 font-black px-6 py-3 rounded-2xl shadow-2xl border-2 border-amber-200 animate-bounce flex items-center gap-2 text-sm sm:text-base">
          <Check className="w-5 h-5 text-stone-950 stroke-[3]" />
          <span>{toastMessage}</span>
        </div>
      )}
 {/* Top Header */}
 <Header
 level={level}
 xp={xp}
 maxXp={maxXp}
 streak={streak}
 levelTitle={getLevelTitle(level)}
 seasonName="四季養生"
 onOpenQuiz={() => setIsQuizOpen(true)}
 onOpenAIConsult={() => setIsAIConsultOpen(true)}
 onOpenFortune={() => setActiveTab('quests')}
        onOpenCodeCopy={() => setIsCodeCopyOpen(true)}
        onGoHome={handleGoHome}
 />

 {/* Main Container */}
 <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
        {/* Prominent Code Copy Banner (Always Visible) */}
        <div className="bg-gradient-to-r from-amber-950/90 via-stone-900 to-emerald-950/80 border-2 border-amber-500/60 rounded-3xl p-4 sm:p-5 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-center md:text-left">
            <div className="p-3 rounded-2xl bg-amber-500/20 border border-amber-400/40 text-amber-300 shrink-0 hidden sm:block">
              <Code className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center justify-center md:justify-start gap-2">
                <span className="text-[11px] font-black bg-amber-400 text-stone-950 px-2 py-0.5 rounded-full uppercase tracking-wider">
                  全コード出力機能
                </span>
                <span className="text-xs text-amber-300/80 font-mono">
                  （全 TypeScript / React ファイル一括統合）
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-extrabold text-stone-100 pt-0.5">
                アプリの全ソースコードを一括取得・コピー
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 w-full md:w-auto shrink-0">
            <button
              onClick={handleDirectCopyCode}
              className="flex-1 md:flex-none px-5 py-3 rounded-2xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:brightness-110 text-stone-950 font-black text-xs sm:text-sm flex items-center justify-center gap-2 shadow-xl shadow-amber-500/25 transition active:scale-95 border border-amber-200 cursor-pointer"
            >
              <Copy className="w-4.5 h-4.5 text-stone-950" />
              <span>全コードを一発コピー</span>
            </button>

            <button
              onClick={() => {
                playClickSound();
                setIsCodeCopyOpen(true);
              }}
              className="px-4 py-3 rounded-2xl bg-stone-850 hover:bg-stone-800 border border-stone-700 text-amber-300 font-bold text-xs sm:text-sm flex items-center justify-center gap-1.5 transition active:scale-95 cursor-pointer"
            >
              <Code className="w-4 h-4 text-amber-400" />
              <span>ファイル別閲覧</span>
            </button>
          </div>
        </div>
 {/* Navigation Tabs Bar */}
 <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-stone-800 scrollbar-none">
 {[
 { id: 'dashboard', label: ' 総合ダッシュボード', icon: PieChart },
 { id: 'elements', label: '️ 五行バランス', icon: Sparkles },
 { id: 'shanghan', label: ' 傷寒論 体質処方箋', icon: BookOpen },
 { id: 'clock', label: ' 黄帝内経 子午流注', icon: Clock },
 { id: 'youtube', label: '▶️ 養生動画＆レシピ', icon: PlaySquare },
 { id: 'quests', label: ' デイリークエスト＆おみくじ', icon: CheckSquare },
 ].map((tab) => (
 <button
 key={tab.id}
 onClick={() => setActiveTab(tab.id as any)}
 className={`px-4 py-2.5 rounded-2xl text-xs sm:text-sm font-bold transition flex items-center gap-2 shrink-0 ${
 activeTab === tab.id
 ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-stone-950 shadow-lg shadow-amber-950/40 scale-105'
 : 'bg-stone-900 hover:bg-stone-850 text-stone-300 border border-stone-800'
 }`}
 >
 <span>{tab.label}</span>
 </button>
 ))}
 </div>

 {/* Tab Views Content */}
 {activeTab === 'dashboard' && (
 <div className="space-y-8 animate-fade-in">
 {/* Hero Quick Status Banner */}
 <div className="bg-gradient-to-r from-stone-900 via-stone-900 to-amber-950/40 border border-stone-800 rounded-3xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
 <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
 <div className="space-y-2 max-w-2xl">
 <div className="flex items-center gap-2">
 <span className="text-xs font-bold text-amber-400 bg-amber-950 border border-amber-800/60 px-3 py-1 rounded-full">
 あなたの現在の診断体質
 </span>
 <span className="text-xs text-stone-400 font-mono">
 {activeShanghanProfile.kanjiName} ｜ {activeShanghanProfile.yinYangType}
 </span>
 </div>

 <h2 className="text-2xl sm:text-3xl font-extrabold text-stone-100">
 {activeShanghanProfile.name}
 </h2>

 <p className="text-xs sm:text-sm text-stone-300 leading-relaxed pt-1">
 “{activeShanghanProfile.tagline}”
 </p>
 </div>

 {/* Hero Actions */}
 <div className="flex flex-col sm:flex-row items-stretch gap-3 shrink-0">
 <button
 onClick={() => setIsQuizOpen(true)}
 className="bg-amber-500 hover:bg-amber-400 text-stone-950 font-bold px-5 py-3 rounded-2xl text-xs sm:text-sm flex items-center justify-center gap-2 shadow-xl shadow-amber-500/20 transition active:scale-95"
 >
 <HelpCircle className="w-4 h-4" />
 <span>アンケートを再回答する</span>
 </button>

 <button
 onClick={() => setIsAIConsultOpen(true)}
 className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-5 py-3 rounded-2xl text-xs sm:text-sm flex items-center justify-center gap-2 shadow-xl shadow-emerald-950/40 transition active:scale-95"
 >
 <Bot className="w-4 h-4" />
 <span>AIに養生相談する</span>
 </button>
 </div>
 </div>
 </div>

 {/* Diagnosis Result (Top) & Five Elements / Lucky Stones (Bottom) */}
 <div className="space-y-8">
 <div className="space-y-3">
 <div className="flex items-center gap-2">
 <span className="text-xs font-black text-amber-400 bg-amber-950 border border-amber-800 px-3 py-1 rounded-full">
 【診断結果】傷寒論 体質処方箋
 </span>
 </div>
 <ShanghanProfileCard userShanghanType={shanghanType} />
 </div>

 {/* 5 Elements Toggle Section */}
  <div className="space-y-4 pt-4 border-t border-stone-800">
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={() => {
          playClickSound();
          setShowFiveElements(!showFiveElements);
        }}
        className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-stone-850 hover:bg-stone-800 border border-emerald-500/40 text-emerald-300 font-bold text-sm sm:text-base flex items-center justify-center gap-2.5 shadow-xl transition active:scale-95 cursor-pointer group"
      >
        <Sparkles className="w-5 h-5 text-emerald-400 group-hover:rotate-12 transition-transform" />
        <span>【五行・生年月日】五行バランス ＆ ラッキー天然石・養生色・おすすめ物を見る</span>
        <span className="text-xs bg-emerald-950 border border-emerald-700/60 text-emerald-300 px-2.5 py-1 rounded-full font-mono ml-1">
          {showFiveElements ? '▲ 閉じる' : '▼ 表示する'}
        </span>
      </button>
    </div>

    {showFiveElements && (
      <div className="space-y-3 animate-fade-in pt-2">
        <FiveElementsChart
          score={fiveElements}
          onChangeScore={(newScore) => setFiveElements(newScore)}
        />
      </div>
    )}
  </div>
 </div>

 {/* Organ Clock Section */}
 <OrganClock />

 {/* YouTube Video Quick Access */}
 <YouTubeVideoSection />

 {/* Daily Quests */}
 <DailyQuestsAndFortune
 quests={quests}
 badges={badges}
 userLevel={level}
 onToggleQuest={handleToggleQuest}
 onAwardXp={addXp}
 onOpenFortuneModal={() => {}}
 />
 </div>
 )}

 {activeTab === 'elements' && (
 <div className="animate-fade-in space-y-6">
 <FiveElementsChart
 score={fiveElements}
 onChangeScore={(newScore) => setFiveElements(newScore)}
 />
 </div>
 )}

 {activeTab === 'shanghan' && (
 <div className="animate-fade-in space-y-6">
 <ShanghanProfileCard userShanghanType={shanghanType} />
 </div>
 )}

 {activeTab === 'clock' && (
 <div className="animate-fade-in space-y-6">
 <OrganClock />
 </div>
 )}

 {activeTab === 'youtube' && (
 <div className="animate-fade-in space-y-6">
 <YouTubeVideoSection />
 </div>
 )}

 {activeTab === 'quests' && (
 <div className="animate-fade-in space-y-6">
 <DailyQuestsAndFortune
 quests={quests}
 badges={badges}
 userLevel={level}
 onToggleQuest={handleToggleQuest}
 onAwardXp={addXp}
 onOpenFortuneModal={() => {}}
 />
 </div>
 )}
 </main>

 {/* Footer */}
 <footer className="mt-16 border-t border-stone-800 bg-stone-950 py-8 text-center text-xs text-stone-500">
 <div className="max-w-7xl mx-auto px-4 space-y-2">
 <p className="font-bold text-stone-400">
 東洋養生ナビ ─ 黄帝内経 × 傷寒論 現代無薬食運動養生アプリ
 </p>
 <p className="text-[11px] text-stone-600">
 ※ 本アプリのアドバイスは中国伝統医学の文献に基づく養生（ヘルスケア）目的であり、医療行為や処方箋ではありません。
 </p>
 </div>
 </footer>

 {/* Modals */}
 <QuestionnaireModal
 isOpen={isQuizOpen}
 onClose={() => setIsQuizOpen(false)}
 onComplete={handleQuizComplete}
 />

 <AIConsultantModal
 isOpen={isAIConsultOpen}
 onClose={() => setIsAIConsultOpen(false)}
 userShanghanType={shanghanType}
 fiveElementsScore={fiveElements}
 />
 </div>
 );
}



// ==========================================
// File: src/types.ts
// ==========================================
export type ElementType = 'wood' | 'fire' | 'earth' | 'metal' | 'water';

export interface FiveElementsScore {
  wood: number;  // 木 (肝/胆) - Spring
  fire: number;  // 火 (心/小腸) - Summer
  earth: number; // 土 (脾/胃) - Late Summer / Doyou
  metal: number; // 金 (肺/大腸) - Autumn
  water: number; // 水 (腎/膀胱) - Winter
}

export type ShanghanType =
  | 'taiyang'  // 太陽病型 (表寒 - 風寒に弱い、肩こり)
  | 'shaoyang' // 少陽病型 (半表半裏 - 寒熱往来、ストレス口苦)
  | 'yangming' // 陽明病型 (裏熱 - 暑がり、口渇、胃腸熱)
  | 'taiyin'   // 太陰病型 (裏寒湿 - 胃腸弱、冷え、水溜まり)
  | 'shaoyin'  // 少陰病型 (深部虚寒 - 手足極冷、体力減退)
  | 'jueyin';  // 厥陰病型 (上熱下寒 - 冷えのぼせ、交感神経緊張)

export interface ShanghanProfile {
  id: ShanghanType;
  name: string;
  kanjiName: string;
  tagline: string;
  description: string;
  coldHeatBalance: 'cold' | 'mild-cold' | 'neutral' | 'mild-heat' | 'heat';
  yinYangType: '陰虚' | '陽虚' | '気虚' | '血虚' | '気滞' | '水滞' | '湿熱';
  keySymptoms: string[];
  dietAdvice: string[];
  exerciseAdvice: string[];
  recommendedIngredients: string[];
  recommendedStretch: string[];
  encouragement?: string;
  acupoints: { name: string; location: string; effect: string }[];
}

export interface QuizOption {
  text: string;
  badgeText?: string;
  elements: Partial<FiveElementsScore>;
  shanghanPoints: Partial<Record<ShanghanType, number>>;
  xp: number;
}

export interface QuizQuestion {
  id: number;
  question: string;
  subtitle: string;
  options: QuizOption[];
}

export interface YouTubeVideo {
  id: string;
  youtubeId: string;
  title: string;
  category: 'exercise' | 'recipe' | 'acupoint' | 'qigong';
  targetElement: ElementType;
  duration: string;
  description: string;
  thumbnailUrl: string;
  tags: string[];
}

export interface DailyQuest {
  id: string;
  title: string;
  description: string;
  xpReward: number;
  completed: boolean;
  category: 'diet' | 'exercise' | 'mind' | 'sleep';
  iconName: string;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  requiredLevel: number;
}

export interface FortuneResult {
  title: string;
  rarity: '大吉' | '中吉' | '吉' | '養生吉';
  neijingQuote: string;
  quoteTranslation: string;
  luckyFood: string;
  luckyTime: string;
  luckyAcupoint: string;
  xpBonus: number;
}

export interface OrganClockSlot {
  timeRange: string;
  startHour: number;
  endHour: number;
  organKanji: string;
  organName: string;
  meridian: string;
  element: ElementType;
  actionAdvice: string;
  avoidAdvice: string;
  emoji: string;
}



// ==========================================
// File: src/./sound.ts
// ==========================================
// Web Audio API Sound Utility for Interactive Feedback

let audioCtx: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  if (!audioCtx) {
    const AudioContextClass =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

/**
 * Play a short, pleasant button click sound effect
 */
export function playClickSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    const now = ctx.currentTime;

    // Pitch sweep for crisp click feedback
    osc.frequency.setValueAtTime(600, now);
    osc.frequency.exponentialRampToValueAtTime(1200, now + 0.05);

    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.07);
  } catch (e) {
    // Ignore audio autoplay restrictions
  }
}

/**
 * Play a celebratory soft oriental chime sound for major completions
 */
export function playChimeSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const freqs = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
    const now = ctx.currentTime;

    freqs.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now + idx * 0.08);

      const startTime = now + idx * 0.08;
      gain.gain.setValueAtTime(0, startTime);
      gain.gain.linearRampToValueAtTime(0.1, startTime + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.8);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(startTime);
      osc.stop(startTime + 0.85);
    });
  } catch (e) {
    // Ignore audio restrictions
  }
}



// ==========================================
// File: src/./streamlitCode.ts
// ==========================================
export const STREAMLIT_REQUIREMENTS = `streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0`;

export const STREAMLIT_APP_PY = `# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import random

# Page configuration
st.set_page_config(
    page_title="東洋養生ナビ - 黄帝内経 × 傷寒論",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Oriental Medical Theme)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0c0a09;
        color: #f5f5f4;
    }
    .main-header {
        background: linear-gradient(135deg, #1c1917 0%, #292524 100%);
        border: 1px solid #78350f;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .header-title {
        color: #fbbf24;
        font-size: 2.2rem;
        font-weight: 900;
        margin: 0;
    }
    .header-subtitle {
        color: #a8a29e;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    .oriental-card {
        background-color: #1c1917;
        border: 1px solid #44403c;
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .badge-amber {
        background-color: #451a03;
        color: #fbbf24;
        border: 1px solid #92400e;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-emerald {
        background-color: #064e3b;
        color: #34d399;
        border: 1px solid #047857;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%);
        color: #0c0a09;
        font-weight: 800;
        border: 1px solid #fef3c7;
        border-radius: 0.75rem;
        padding: 0.5rem 1.25rem;
    }
    .stButton>button:hover {
        filter: brightness(1.1);
        color: #0c0a09;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session State Initializations
if "wood" not in st.session_state:
    st.session_state.wood = 65
if "fire" not in st.session_state:
    st.session_state.fire = 70
if "earth" not in st.session_state:
    st.session_state.earth = 50
if "metal" not in st.session_state:
    st.session_state.metal = 60
if "water" not in st.session_state:
    st.session_state.water = 55

if "shanghan_type" not in st.session_state:
    st.session_state.shanghan_type = "太陽病（たいようびょう）"

if "fortune" not in st.session_state:
    st.session_state.fortune = None

if "xp" not in st.session_state:
    st.session_state.xp = 120

# Header Banner
st.markdown(
    """
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge-amber">東洋医学 × 現代食養生</span>
                <h1 class="header-title">🌿 東洋養生ナビ (Streamlit版)</h1>
                <p class="header-subtitle">黄帝内経（子午流注） & 傷寒論 六病体質診断 ─ 無薬・食養生・生活習慣アドバイザー</p>
            </div>
            <div>
                <span class="badge-emerald">Level 2 養生実践者 (XP: {} / 300)</span>
            </div>
        </div>
    </div>
    """.format(st.session_state.xp),
    unsafe_allow_html=True,
)

# Sidebar Navigation
st.sidebar.title("🧭 養生ナビゲーション")
page = st.sidebar.radio(
    "メニューを選択",
    [
        "📊 総合ダッシュボード & 五行診断",
        "🩺 傷寒論 体質診断アンケート",
        "⏰ 黄帝内経 子午流注（24時間時計）",
        "🥠 デイリーおみくじ & 養生クエスト",
        "📋 GitHub用 Python (Streamlit) 全コード",
    ],
)

# ------------------------------------------------------------------
# Page 1: 総合ダッシュボード & 五行診断
# ------------------------------------------------------------------
if page == "📊 総合ダッシュボード & 五行診断":
    st.subheader("📊 あなたの五行バランス (5 Elements Balance)")
    st.write("生年月日または現在の体調から、木・火・土・金・水バランスを調整・確認できます。")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ 五行スコア調整")
        st.session_state.wood = st.slider("🌲 木 (Wood / 肝・胆)", 0, 100, st.session_state.wood)
        st.session_state.fire = st.slider("🔥 火 (Fire / 心・小腸)", 0, 100, st.session_state.fire)
        st.session_state.earth = st.slider("⛰️ 土 (Earth / 脾・胃)", 0, 100, st.session_state.earth)
        st.session_state.metal = st.slider("⚔️ 金 (Metal / 肺・大腸)", 0, 100, st.session_state.metal)
        st.session_state.water = st.slider("💧 水 (Water / 腎・膀胱)", 0, 100, st.session_state.water)

        # Birthdate Calculation Form
        st.markdown("---")
        st.markdown("#### 🎂 生年月日による自動判定")
        birth_date = st.date_input("生年月日を選択", datetime.date(1995, 5, 15))
        if st.button("生年月日から五行を算出"):
            year = birth_date.year
            month = birth_date.month
            day = birth_date.day
            st.session_state.wood = (year * 3 + day) % 60 + 40
            st.session_state.fire = (month * 7 + year) % 55 + 45
            st.session_state.earth = (day * 5 + month) % 50 + 50
            st.session_state.metal = (year + month + day) % 65 + 35
            st.session_state.water = (day * 11) % 60 + 40
            st.success("生年月日からの五行バランスを更新しました！")
            if hasattr(st, "rerun"):
                st.rerun()
            elif hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Plotly Radar Chart
        categories = ["木 (肝)", "火 (心)", "土 (脾)", "金 (肺)", "水 (腎)"]
        values = [
            st.session_state.wood,
            st.session_state.fire,
            st.session_state.earth,
            st.session_state.metal,
            st.session_state.water,
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(251, 191, 36, 0.25)",
                line=dict(color="#fbbf24", width=3),
                name="現在の五行バランス",
            )
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#a8a29e"),
                angularaxis=dict(color="#fbbf24", font=dict(size=14, color="#fbbf24")),
                bgcolor="#1c1917",
            ),
            paper_bgcolor="#0c0a09",
            plot_bgcolor="#0c0a09",
            margin=dict(l=40, r=40, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # 5 Elements Lucky Prescriptions
    st.markdown("---")
    st.subheader("💎 あなたの五行 ラッキー属性 & 養生処方")
    
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    
    with col_a:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 🌲 木 (Wood)")
        st.write(f"**スコア**: {st.session_state.wood}")
        st.write("**ラッキー天然石**: アベンチュリン, エメラルド")
        st.write("**養生色**: 青・緑")
        st.write("**おすすめ食材**: 酢・シソ・緑黄色野菜")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔥 火 (Fire)")
        st.write(f"**スコア**: {st.session_state.fire}")
        st.write("**ラッキー天然石**: カーネリアン, ルビー")
        st.write("**養生色**: 赤・朱色")
        st.write("**おすすめ食材**: トマト・ゴーヤ・小豆")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ⛰️ 土 (Earth)")
        st.write(f"**スコア**: {st.session_state.earth}")
        st.write("**ラッキー天然石**: タイガーアイ, トパーズ")
        st.write("**養生色**: 黄・ベージュ")
        st.write("**おすすめ食材**: かぼちゃ・サツマイモ・蜂蜜")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚔️ 金 (Metal)")
        st.write(f"**スコア**: {st.session_state.metal}")
        st.write("**ラッキー天然石**: 水晶, パール")
        st.write("**養生色**: 白・シルバー")
        st.write("**おすすめ食材**: 大根・豆腐・白ごま")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_e:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 💧 水 (Water)")
        st.write(f"**スコア**: {st.session_state.water}")
        st.write("**ラッキー天然石**: ラピスラズリ, オニキス")
        st.write("**養生色**: 黒・紺色")
        st.write("**おすすめ食材**: 黒ごま・黒豆・昆布")
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 2: 傷寒論 体質診断アンケート
# ------------------------------------------------------------------
elif page == "🩺 傷寒論 体質診断アンケート":
    st.subheader("🩺 傷寒論（しょうかんろん）六病 体質診断")
    st.write("以下の質問に回答すると、あなたに最適な傷寒論タイプと無薬食養生アドバイスを出力します。")

    with st.form("shanghan_form"):
        st.markdown("#### 1. 風邪の初期症状や現在の体調で一番近いものは？")
        q1 = st.radio(
            "選択してください",
            [
                "ゾクゾクする寒気、首や肩のこり、頭痛がある（太陽病）",
                "高熱、顔の火照り、強い喉の渇き、大汗をかく（陽明病）",
                "寒気と熱っぽさが交互に来る、口が苦い、脇腹が張る（少陽病）",
                "お腹が冷えて張る、軟便や下痢をしやすい（太陰病）",
                "手足が氷のように冷える、体がだるく横になりたい（少陰病）",
                "上熱下寒（のぼせと足冷え）、激しい頭痛や嘔気（厥陰病）",
            ],
        )

        st.markdown("#### 2. 日常の胃腸や冷えの状態は？")
        q2 = st.multiselect(
            "当てはまるものを全て選択",
            [
                "首や背中が冷えやすい",
                "冷たい水や炭酸飲料をよく飲みたくなる",
                "ストレスで胃がキリキリ痛みやすい",
                "温かいスープやお粥を食べると落ち着く",
                "朝起きるのが辛く体力がない",
                "手足の末端が一年中冷えている",
            ],
        )

        submitted = st.form_submit_button("診断結果を出す")

    if submitted:
        if "太陽病" in q1:
            st.session_state.shanghan_type = "太陽病（たいようびょう）"
        elif "陽明病" in q1:
            st.session_state.shanghan_type = "陽明病（ようめいびょう）"
        elif "少陽病" in q1:
            st.session_state.shanghan_type = "少陽病（しょうようびょう）"
        elif "太陰病" in q1:
            st.session_state.shanghan_type = "太陰病（たいいんびょう）"
        elif "少陰病" in q1:
            st.session_state.shanghan_type = "少陰病（しょういんびょう）"
        else:
            st.session_state.shanghan_type = "厥陰病（けついんびょう）"

    # Display Current Shanghan Prescription
    st.markdown("---")
    st.markdown(f"### 📜 診断結果: <span style='color:#fbbf24;'>{st.session_state.shanghan_type}</span>", unsafe_allow_html=True)

    shanghan_data = {
        "太陽病（たいようびょう）": {
            "desc": "体表に寒邪が侵入している状態。発汗・発散により表邪を取り除くことが養生の鍵です。",
            "prescription": "生姜湯・ねぎ湯・葛湯",
            "acupoint": "風池（ふうち）・大椎（だいつい）",
            "foods": "生姜、ネギ、葛粉、シナモン、紫蘇",
            "habit": "首の後ろと肩を蒸しタオルで温め、じんわり汗をかいて早めに就寝する。",
        },
        "陽明病（ようめいびょう）": {
            "desc": "体内（胃腸）に強い熱がこもっている状態。清熱と生津（水分補給）が必要です。",
            "prescription": "夏みかん・緑茶・豆腐養生",
            "acupoint": "曲池（きょくち）・内庭（ないてい）",
            "foods": "大根、豆腐、トマト、きゅうり、緑茶、梨",
            "habit": "油っこい食事を控え、水分補給をこまめに行い胃腸の熱を冷ます。",
        },
        "少陽病（しょうようびょう）": {
            "desc": "半表半裏（自律神経・気機）の滞り。和解・理気による気のスムーズな巡りが重要です。",
            "prescription": "紫蘇レモン・陳皮ハーブ茶",
            "acupoint": "陽陵泉（ようりょうせん）・太衝（たいしょう）",
            "foods": "陳皮、紫蘇、柑橘類、セロリ、ジャスミン茶",
            "habit": "深呼吸を意識し、香りの良いハーブティーでストレスを緩和する。",
        },
        "太陰病（たいいんびょう）": {
            "desc": "脾胃（消化器）が冷えて水分代謝が低下している状態。温中健脾（腹部を温める）が必須。",
            "prescription": "人参かぼちゃ粥・乾姜スープ",
            "acupoint": "足三里（あしさんり）・中脘（ちゅうかん）",
            "foods": "かぼちゃ、サツマイモ、長芋、生姜、ヒノヒカリ粥",
            "habit": "冷たい飲食を徹底的に避け、腹巻きや湯たんぽでお腹を保温する。",
        },
        "少陰病（しょういんびょう）": {
            "desc": "心腎の陽気が著しく低下した寒証。温陽補気（根本的な熱の補給）が必要です。",
            "prescription": "黒ごま足湯・シナモン紅茶",
            "acupoint": "湧泉（ゆうせん）・関元（かんげん）",
            "foods": "黒ごま、ニラ、羊肉、シナモン、核桃（クルミ）",
            "habit": "就寝前に熱めの足湯を行い、22時までに布団に入り体力を回復する。",
        },
        "厥陰病（けついんびょう）": {
            "desc": "寒熱が錯雑し、手足の末端が極度に冷える状態。暖肝温経（血行促進と寒気の解消）が重要。",
            "prescription": "当帰なつめ茶・和漢スパイス湯",
            "acupoint": "太衝（たいしょう）・三陰交（さんいんこう）",
            "foods": "なつめ、当帰茶、山椒、生姜、黒糖",
            "habit": "手首・足首・首の「三つの首」を温め、軽いストレッチで血流を促す。",
        },
    }

    info = shanghan_data.get(st.session_state.shanghan_type, shanghan_data["太陽病（たいようびょう）"])

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 📖 体質の特徴")
        st.write(info["desc"])
        st.markdown("#### 🍵 無薬 食養生処方")
        st.write(f"**おすすめ養生食**: {info['prescription']}")
        st.write(f"**適した食材**: {info['foods']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_res2:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 📍 おすすめ特効穴（ツボ）")
        st.write(f"**ツボ名**: {info['acupoint']}")
        st.markdown("#### 🧘 生活習慣アドバイス")
        st.write(info["habit"])
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 3: 黄帝内経 子午流注（24時間時計）
# ------------------------------------------------------------------
elif page == "⏰ 黄帝内経 子午流注（24時間時計）":
    st.subheader("⏰ 黄帝内経 子午流注（しごるちゅう）24時間 臓腑時間")
    st.write("古代中国医学の知恵「子午流注」に基づき、2時間ごとの経絡・臓腑の活発化時間帯に合わせた生活リズムを提案します。")

    now = datetime.datetime.now()
    current_hour = now.hour

    clock_data = [
        {"time": "23:00-01:00", "organ": "子時 (胆経)", "desc": "細胞の修復と骨髄の造血。熟睡が必要不可欠。"},
        {"time": "01:00-03:00", "organ": "丑時 (肝経)", "desc": "血液の浄化と解毒。起きてはいけない時間。"},
        {"time": "03:00-05:00", "organ": "寅時 (肺経)", "desc": "気血を全身へ巡らせる。深い呼吸が効果的。"},
        {"time": "05:00-07:00", "organ": "卯時 (大腸経)", "desc": "排泄の最高時間。コップ1杯のぬるま湯を飲む。"},
        {"time": "07:00-09:00", "organ": "辰時 (胃経)", "desc": "消化吸収が高まる。温かく栄養豊富な朝食をとる。"},
        {"time": "09:00-11:00", "organ": "巳時 (脾経)", "desc": "食べたものを気血に変える。頭脳労働に最適。"},
        {"time": "11:00-13:00", "organ": "午時 (心経)", "desc": "気血の循環と精神の安定。15-30分の昼寝を推し進める。"},
        {"time": "13:00-15:00", "organ": "未時 (小腸経)", "desc": "清濁の分別（水分補給）。白湯を多めに飲む。"},
        {"time": "15:00-17:00", "organ": "申時 (膀胱経)", "desc": "代謝活動のピーク。運動や仕事・勉強の効率最大。"},
        {"time": "17:00-19:00", "organ": "酉時 (腎経)", "desc": "生命力（精）の蓄積。軽い散歩や足湯で腎を補う。"},
        {"time": "19:00-21:00", "organ": "戌時 (心包経)", "desc": "心をリラックス。家族や親しい人と穏やかに過ごす。"},
        {"time": "21:00-23:00", "organ": "亥時 (三焦経)", "desc": "全身の気を整え睡眠へ。電子機器を避け就寝準備。"},
    ]

    st.markdown(f"**現在時刻**: {now.strftime('%H:%M')} (日本標準時)")

    for c in clock_data:
        start_h = int(c["time"].split(":")[0])
        end_h = int(c["time"].split("-")[1].split(":")[0])
        
        is_current = False
        if start_h == 23:
            is_current = (current_hour >= 23 or current_hour < 1)
        elif start_h <= current_hour < end_h:
            is_current = True

        border_color = "#fbbf24" if is_current else "#44403c"
        bg_color = "#451a03" if is_current else "#1c1917"

        st.markdown(
            f"""
            <div style="background-color: {bg_color}; border: 2px solid {border_color}; border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.1rem; font-weight: 800; color: #fbbf24;">{c['time']} 【{c['organ']}】</span>
                    {'<span class="badge-amber">🔥 NOW アクティブ</span>' if is_current else ''}
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #d6d3d1;">{c['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------
# Page 4: デイリーおみくじ & 養生クエスト
# ------------------------------------------------------------------
elif page == "🥠 デイリーおみくじ & 養生クエスト":
    st.subheader("🥠 東洋養生 おみくじ & 今日のクエスト")

    col_f1, col_f2 = st.columns([1, 1])

    with col_f1:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 🥠 本日の養生おみくじ")

        if st.button("おみくじを引く"):
            fortunes = [
                {"result": "大吉 (大平穏)", "text": "気血が満ち溢れる最高の一日。白湯を飲んで心身を整えましょう。"},
                {"result": "中吉 (中和養生)", "text": "脾胃をいたわる日。消化の良い温かい食べ物が吉を呼びます。"},
                {"result": "小吉 (静心養気)", "text": "少し肩の力を抜いて、深呼吸と足湯でリフレッシュしましょう。"},
                {"result": "吉 (順天応時)", "text": "自然のリズムに合わせて早寝早起きを。散歩がおすすめ。"},
            ]
            st.session_state.fortune = random.choice(fortunes)

        if st.session_state.fortune:
            f = st.session_state.fortune
            st.markdown(f"### <span style='color:#fbbf24;'>{f['result']}</span>", unsafe_allow_html=True)
            st.write(f["text"])
        else:
            st.write("「おみくじを引く」ボタンを押して、今日の養生メッセージを受け取ってください。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_f2:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ✅ 本日の養生クエスト (+20 XP)")

        q_c1 = st.checkbox("朝起きたらコップ1杯の白湯（ぬるま湯）を飲む")
        q_c2 = st.checkbox("昼休みや休憩時に3分間の深呼吸（腹式呼吸）")
        q_c3 = st.checkbox("就寝前にぬるめのお湯で足湯を行う")

        if st.button("クエスト完了を記録 (+XP)"):
            count = sum([q_c1, q_c2, q_c3])
            st.session_state.xp += count * 20
            st.success(f"{count} 個のクエスト完了！ XPを +{count * 20} 獲得しました。")
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 5: GitHub用 Python (Streamlit) 全コード
# ------------------------------------------------------------------
elif page == "📋 GitHub用 Python (Streamlit) 全コード":
    st.subheader("📋 Streamlit (Python) ソースコード全取得")
    st.write("GitHubやStreamlit Cloudにそのままデプロイできる app.py および requirements.txt のコードです。")

    st.markdown("#### 1. requirements.txt の内容")
    st.code(
        """streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0""",
        language="text",
    )

    st.markdown("#### 2. app.py の全ソースコード")
    st.write("「コード閲覧＆GitHub用コピー」ボタンから直接コピー・保存いただけます。")
`;



// ==========================================
// File: src/components/AcupointDiagramModal.tsx
// ==========================================
import React, { useState } from 'react';
import { Target, X, Compass, Sparkles, Hand, HeartPulse, ShieldCheck, CheckCircle2 } from 'lucide-react';

export interface AcupointDetail {
 id: string;
 name: string;
 reading: string;
 region: 'hand' | 'leg' | 'foot' | 'neck' | 'sole' | 'wrist' | 'head' | 'elbow';
 location: string;
 effect: string;
 method: string;
 meridian: string;
}

export const ACUPOINT_DATABASE: Record<string, AcupointDetail> = {
 '合谷 (ごうこく)': {
 id: 'gokoku',
 name: '合谷 (ごうこく)',
 reading: 'ごうこく',
 region: 'hand',
 location: '手の甲の親指と人差し指の骨が交わる V字状の凹みの中央',
 effect: '万能のツボ。風邪の初頭、頭痛、寒気、肩こり、ストレス緩和、大腸の巡りを改善',
 method: '反対側の親指で骨のキワに向かって、少し痛気持ちいい強さで5秒×3回じんわり押します。',
 meridian: '手陽明大腸経 (風邪の邪気を追い払う第一選択)',
 },
 '足三里 (あしさんり)': {
 id: 'ashisanri',
 name: '足三里 (あしさんり)',
 reading: 'あしさんり',
 region: 'leg',
 location: '膝のお皿のすぐ下、外側の凹みから指幅4本分（人差し指〜小指）下に下がった場所',
 effect: '無病長寿・胃腸強化の代表ツボ。冷え、消化不良、むくみ、身体の疲れを一気に解消',
 method: '親指をあて、膝に向かって軽く押し上げるように3〜5秒押し揉みます。',
 meridian: '足陽明胃経 (東洋医学最高峰の消化器・滋養強壮ツボ)',
 },
 '太衝 (たいしょう)': {
 id: 'taisho',
 name: '太衝 (たいしょう)',
 reading: 'たいしょう',
 region: 'foot',
 location: '足の甲の親指と第2指の骨の間を、足首に向かって撫で上げた時に指が止まる窪み',
 effect: 'ストレスによるイライラ、肝のたかぶり、眼精疲労、自律神経の不調を即座に鎮める',
 method: '親指を深く当て、息を吐きながら足首の方向に斜めにゆっくり推圧します。',
 meridian: '足厥陰肝経 (気の滞り・精神の緊張をほぐす特効穴)',
 },
 '風池 (ふうち)': {
 id: 'fuchi',
 name: '風池 (ふうち)',
 reading: 'ふうち',
 region: 'neck',
 location: '首の後ろ、髪の生え際にある大きな2本の筋の外側の窪み（耳の後ろの骨の下）',
 effect: '首肩の頑固なコリ、頭重感、目のかすみ、冷気による悪寒の予防',
 method: '両手で頭を包み込み、親指をくぼみに当てて頭頂部に向けて押し上げます。',
 meridian: '足少陽胆経 (風の邪気が池のように溜まるのを防ぐ)',
 },
 '湧泉 (ゆうせん)': {
 id: 'yusen',
 name: '湧泉 (ゆうせん)',
 reading: 'ゆうせん',
 region: 'sole',
 location: '足の裏の指を屈曲させた時、中央よりやや上の「人」の字形にくぼむ中央部',
 effect: '湧き出る泉のように生命エネルギー（腎）をチャージ。冷え症、疲労困憊、足の冷え',
 method: '両手の大指を重ねて当て、体重をかけながらギューッと力強く押し込みます。青竹踏みも効果的。',
 meridian: '足少陰腎経 (生まれ持った命の源を潤す重要ツボ)',
 },
 '内関 (ないかん)': {
 id: 'neikan',
 name: '内関 (ないかん)',
 reading: 'ないかん',
 region: 'wrist',
 location: '手のひら側の手首の横じわから、指幅3本分（人差し指・中指・薬指）肘寄りの中央部',
 effect: '自律神経をリセット、胸のつかえ、吐き気、冷えのぼせ、動悸や乗り物酔いを防ぐ',
 method: '親指の腹で心地よい圧力をかけながら、円を描くようにやさしくマッサージします。',
 meridian: '手厥陰心包経 (心を穏やかに守るバリア)',
 },
 '曲池 (きょくち)': {
 id: 'kyokuchi',
 name: '曲池 (きょくち)',
 reading: 'きょくち',
 region: 'elbow',
 location: '肘を直角に曲げたときにできる外側の横じわの先端の窪み',
 effect: '体内のこもった過剰な熱を清熱・放熱。肌荒れ、肩こり、過剰な食欲を抑える',
 method: '反対の手の親指で窪みに押し当て、骨に向かって響くように押圧します。',
 meridian: '手陽明大腸経 (清熱・解毒の代表ツボ)',
 },
 '百会 (ひゃくえ)': {
 id: 'hyakue',
 name: '百会 (ひゃくえ)',
 reading: 'ひゃくえ',
 region: 'head',
 location: '両方の耳の先端を結んだ線と、顔のセンターライン（正中線）が頭頂部で交わる場所',
 effect: '百（多数）の気が集まる交差点。頭に上がった熱を下げ、自律神経の整和、不眠解消',
 method: '中指の腹を当て、垂直下に向かって心地よい強さで優しく押します。',
 meridian: '督脈 (全身の陽気をコントロールする交差点)',
 },
};

interface AcupointDiagramModalProps {
 acupointName: string;
 isOpen: boolean;
 onClose: () => void;
}

export const AcupointDiagramModal: React.FC<AcupointDiagramModalProps> = ({
 acupointName,
 isOpen,
 onClose,
}) => {
 if (!isOpen) return null;

 // Search exact or fallback
 const pointKey =
 Object.keys(ACUPOINT_DATABASE).find((key) => key.includes(acupointName) || acupointName.includes(key.split(' ')[0])) ||
 '足三里 (あしさんり)';

 const detail = ACUPOINT_DATABASE[pointKey] || ACUPOINT_DATABASE['足三里 (あしさんり)'];

 // Render SVG Vector Diagram per Region
 const renderSvgDiagram = () => {
 switch (detail.region) {
 case 'hand':
 // Hand Diagram for Gokoku (合谷)
 return (
 <svg viewBox="0 0 300 240" className="w-full h-48 sm:h-56">
 {/* Hand Contour */}
 <path
 d="M100 220 Q90 160 80 130 Q70 100 50 80 Q35 65 50 50 Q70 35 90 70 Q105 50 120 30 Q130 15 145 30 Q155 50 155 80 Q165 50 180 30 Q195 15 205 35 Q210 60 200 90 Q215 70 230 60 Q245 50 250 70 Q250 90 220 120 Q190 150 180 220 Z"
 fill="#292524"
 stroke="#fbbf24"
 strokeWidth="3"
 />
 {/* V-shape Bone Structure */}
 <path d="M75 120 Q105 130 135 150 M135 150 Q160 120 180 90" fill="none" stroke="#78716c" strokeWidth="2" strokeDasharray="4 4" />
 <text x="100" y="180" fill="#a8a29e" fontSize="11" fontWeight="bold">親指骨</text>
 <text x="170" y="170" fill="#a8a29e" fontSize="11" fontWeight="bold">人差し指骨</text>

 {/* Acupoint Hotspot Target */}
 <circle cx="120" cy="125" r="16" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="120" cy="125" r="10" fill="#ef4444" stroke="#ffffff" strokeWidth="3" />
 <circle cx="120" cy="125" r="3" fill="#ffffff" />

 {/* Callout Pointer Line */}
 <line x1="120" y1="125" x2="60" y2="180" stroke="#f59e0b" strokeWidth="2" />
 <rect x="15" y="170" width="90" height="30" rx="8" fill="#451a03" stroke="#f59e0b" strokeWidth="1" />
 <text x="60" y="190" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 合谷 (ツボ)
 </text>
 </svg>
 );

 case 'leg':
 // Leg Diagram for Ashisanri (足三里)
 return (
 <svg viewBox="0 0 300 240" className="w-full h-48 sm:h-56">
 {/* Knee & Leg Contour */}
 <path
 d="M120 20 Q140 20 160 30 Q180 50 180 80 Q175 110 170 150 Q165 190 160 220 L110 220 Q115 180 120 140 Q125 90 120 80 Q110 50 120 20 Z"
 fill="#292524"
 stroke="#fbbf24"
 strokeWidth="3"
 />
 {/* Knee Cap (Patella) */}
 <ellipse cx="145" cy="65" rx="20" ry="15" fill="#44403c" stroke="#d6d3d1" strokeWidth="2" />
 <text x="145" y="69" fill="#f5f5f4" fontSize="10" fontWeight="bold" textAnchor="middle">膝皿</text>

 {/* Finger Width Scale (指4本分) */}
 <rect x="165" y="80" width="10" height="40" fill="#a855f7" fillOpacity="0.4" rx="2" />
 <text x="180" y="105" fill="#c084fc" fontSize="11" fontWeight="bold">指幅4本下</text>

 {/* Acupoint Hotspot Target */}
 <circle cx="158" cy="120" r="16" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="158" cy="120" r="10" fill="#ef4444" stroke="#ffffff" strokeWidth="3" />
 <circle cx="158" cy="120" r="3" fill="#ffffff" />

 {/* Callout */}
 <line x1="158" y1="120" x2="230" y2="150" stroke="#f59e0b" strokeWidth="2" />
 <rect x="185" y="145" width="100" height="30" rx="8" fill="#451a03" stroke="#f59e0b" strokeWidth="1" />
 <text x="235" y="165" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 足三里 (ツボ)
 </text>
 </svg>
 );

 case 'foot':
 case 'sole':
 // Foot Sole / Foot Top Diagram for Taisho / Yusen
 return (
 <svg viewBox="0 0 300 240" className="w-full h-48 sm:h-56">
 {/* Foot Contour */}
 <path
 d="M100 220 Q80 180 80 130 Q80 80 100 50 Q115 30 135 20 Q155 15 175 30 Q195 50 195 90 Q190 140 180 180 Q170 220 130 220 Z"
 fill="#292524"
 stroke="#fbbf24"
 strokeWidth="3"
 />
 {/* Toe contours */}
 <circle cx="120" cy="30" r="12" fill="#44403c" stroke="#fbbf24" strokeWidth="1.5" />
 <circle cx="145" cy="25" r="10" fill="#44403c" stroke="#fbbf24" strokeWidth="1.5" />
 <circle cx="165" cy="28" r="9" fill="#44403c" stroke="#fbbf24" strokeWidth="1.5" />
 <circle cx="180" cy="35" r="8" fill="#44403c" stroke="#fbbf24" strokeWidth="1.5" />

 {/* Hotspot position based on sole vs top */}
 {detail.region === 'sole' ? (
 <>
 <circle cx="138" cy="95" r="16" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="138" cy="95" r="10" fill="#ef4444" stroke="#ffffff" strokeWidth="3" />
 <line x1="138" y1="95" x2="210" y2="120" stroke="#f59e0b" strokeWidth="2" />
 <rect x="170" y="115" width="110" height="30" rx="8" fill="#451a03" stroke="#f59e0b" strokeWidth="1" />
 <text x="225" y="135" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 湧泉 (足裏中央)
 </text>
 </>
 ) : (
 <>
 <circle cx="132" cy="65" r="16" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="132" cy="65" r="10" fill="#ef4444" stroke="#ffffff" strokeWidth="3" />
 <line x1="132" y1="65" x2="50" y2="90" stroke="#f59e0b" strokeWidth="2" />
 <rect x="10" y="85" width="110" height="30" rx="8" fill="#451a03" stroke="#f59e0b" strokeWidth="1" />
 <text x="65" y="105" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 太衝 (指間窪み)
 </text>
 </>
 )}
 </svg>
 );

 case 'neck':
 case 'head':
 // Head / Neck Diagram
 return (
 <svg viewBox="0 0 300 240" className="w-full h-48 sm:h-56">
 {/* Head & Neck Contour Back View */}
 <path
 d="M90 120 Q90 40 150 40 Q210 40 210 120 Q210 160 190 180 L190 220 L110 220 L110 180 Q90 160 90 120 Z"
 fill="#292524"
 stroke="#fbbf24"
 strokeWidth="3"
 />
 {/* Ears */}
 <ellipse cx="85" cy="110" rx="8" ry="16" fill="#44403c" stroke="#fbbf24" strokeWidth="1.5" />
 <ellipse cx="215" cy="110" rx="8" ry="16" fill="#44403c" stroke="#fbbf24" strokeWidth="1.5" />

 {detail.region === 'head' ? (
 <>
 {/* Hyakue on top */}
 <circle cx="150" cy="42" r="16" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="150" cy="42" r="10" fill="#ef4444" stroke="#ffffff" strokeWidth="3" />
 <line x1="150" y1="42" x2="230" y2="30" stroke="#f59e0b" strokeWidth="2" />
 <rect x="180" y="20" width="110" height="30" rx="8" fill="#451a03" stroke="#f59e0b" strokeWidth="1" />
 <text x="235" y="40" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 百会 (頭頂部)
 </text>
 </>
 ) : (
 <>
 {/* Fuchi on neck base */}
 <circle cx="125" cy="165" r="14" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="125" cy="165" r="8" fill="#ef4444" stroke="#ffffff" strokeWidth="2.5" />
 <circle cx="175" cy="165" r="14" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="175" cy="165" r="8" fill="#ef4444" stroke="#ffffff" strokeWidth="2.5" />
 <text x="150" y="205" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 風池 (左右のうなじ窪み)
 </text>
 </>
 )}
 </svg>
 );

 default:
 // Default Wrist / Elbow Diagram
 return (
 <svg viewBox="0 0 300 240" className="w-full h-48 sm:h-56">
 {/* Arm & Wrist Contour */}
 <path
 d="M100 220 L100 60 Q100 40 125 30 L175 30 Q200 40 200 60 L200 220 Z"
 fill="#292524"
 stroke="#fbbf24"
 strokeWidth="3"
 />
 {/* Wrist Crease Line */}
 <line x1="100" y1="80" x2="200" y2="80" stroke="#a8a29e" strokeWidth="2" strokeDasharray="3 3" />
 <text x="150" y="75" fill="#a8a29e" fontSize="11" fontWeight="bold" textAnchor="middle">手首の横じわ</text>

 <circle cx="150" cy="130" r="16" fill="#f59e0b" fillOpacity="0.3" className="animate-ping" />
 <circle cx="150" cy="130" r="10" fill="#ef4444" stroke="#ffffff" strokeWidth="3" />
 <line x1="150" y1="130" x2="230" y2="150" stroke="#f59e0b" strokeWidth="2" />
 <rect x="180" y="145" width="105" height="30" rx="8" fill="#451a03" stroke="#f59e0b" strokeWidth="1" />
 <text x="232" y="165" fill="#fef3c7" fontSize="12" fontWeight="bold" textAnchor="middle">
 {detail.name.split(' ')[0]}
 </text>
 </svg>
 );
 }
 };

 return (
 <div className="fixed inset-[#0] z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
 <div className="bg-stone-900 border-2 border-amber-500/60 rounded-3xl max-w-lg w-full p-5 sm:p-6 text-stone-100 shadow-2xl space-y-4 relative overflow-hidden">
 <button
 onClick={onClose}
 className="absolute top-4 right-4 p-2 rounded-full bg-stone-800 text-stone-400 hover:text-stone-100 hover:bg-stone-700 transition"
 >
 <X className="w-5 h-5" />
 </button>

 {/* Title */}
 <div className="flex items-center gap-2.5 text-amber-400">
 <Target className="w-6 h-6 animate-pulse" />
 <div>
 <span className="text-xs font-bold text-amber-300 bg-amber-950 border border-amber-700 px-2.5 py-0.5 rounded-md">
 経絡ツボ簡略位置図
 </span>
 <h3 className="text-xl font-black text-stone-100">{detail.name}</h3>
 </div>
 </div>

 {/* SVG Diagram Canvas */}
 <div className="bg-stone-950 border border-stone-800 rounded-2xl p-2 relative shadow-inner flex items-center justify-center">
 {renderSvgDiagram()}
 </div>

 {/* Location & Meridian */}
 <div className="space-y-2 text-xs sm:text-sm">
 <div className="bg-stone-850 p-3 rounded-xl border border-stone-750">
 <span className="font-extrabold text-amber-300 block mb-0.5"> 取穴（ツボの位置）:</span>
 <p className="text-stone-200 leading-relaxed font-medium">{detail.location}</p>
 </div>

 <div className="bg-stone-850 p-3 rounded-xl border border-stone-750">
 <span className="font-extrabold text-amber-300 block mb-0.5"> 効能と特徴:</span>
 <p className="text-stone-200 leading-relaxed font-medium">{detail.effect}</p>
 </div>

 <div className="bg-amber-950/40 border border-amber-600/40 p-3 rounded-xl">
 <span className="font-extrabold text-amber-300 flex items-center gap-1 mb-0.5">
 <CheckCircle2 className="w-4 h-4 text-amber-400" />
 <span>効果的なツボ押し・マッサージ方法:</span>
 </span>
 <p className="text-amber-100 leading-relaxed font-medium">{detail.method}</p>
 </div>
 </div>

 <button
 onClick={onClose}
 className="w-full bg-amber-500 hover:bg-amber-400 text-stone-950 font-black py-2.5 rounded-xl transition text-sm shadow-md"
 >
 確認しました（閉じる）
 </button>
 </div>
 </div>
 );
};



// ==========================================
// File: src/components/AIConsultantModal.tsx
// ==========================================
import React, { useState } from 'react';
import { X, Send, Bot, Sparkles, User, RefreshCw, AlertCircle, Utensils, Activity } from 'lucide-react';
import { FiveElementsScore, ShanghanType } from '../types';

interface AIConsultantModalProps {
  isOpen: boolean;
  onClose: () => void;
  userShanghanType: ShanghanType;
  fiveElementsScore: FiveElementsScore;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
}

const PRESET_PROMPTS = [
  '冷え性と肩こりが気になる日の、おすすめ食材とツボを教えて！',
  '最近夜寝つきが悪い時の夕食は何が良い？（薬は使いたくない）',
  '雨の日や湿気が多い日に体が重だるくなる理由とストレッチは？',
  '胃が重くて食欲が出ない日の簡単お粥スープと足三里ケアは？',
];

export const AIConsultantModal: React.FC<AIConsultantModalProps> = ({
  isOpen,
  onClose,
  userShanghanType,
  fiveElementsScore,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'こんにちは！中国の古典名著『黄帝内経』と『傷寒論』の知恵を現代に活かす、AI東洋養生アドバイザーです。\n\n当アプリでは【薬物・漢方薬を勧めない無薬食養生】を徹底しております。お体の気になる症状や日常のお悩み、季節の食事・運動についてお気軽にご質問ください！',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputText;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/ai-consultation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: textToSend,
          constitution: userShanghanType,
          fiveElements: fiveElementsScore,
          season: '四季養生',
        }),
      });

      const data = await response.json();

      if (response.ok && data.reply) {
        const aiMsg: ChatMessage = {
          id: `ai-${Date.now()}`,
          sender: 'ai',
          text: data.reply,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, aiMsg]);
      } else {
        const errorMsg: ChatMessage = {
          id: `ai-err-${Date.now()}`,
          sender: 'ai',
          text: data.error || '申し訳ございません。回答の取得中にエラーが発生しました。時間を置いて再度お試しください。',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `ai-err-${Date.now()}`,
        sender: 'ai',
        text: '通信エラーが発生しました。サーバーとの接続をご確認ください。',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
        setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl bg-stone-900 border border-emerald-500/30 rounded-3xl shadow-2xl overflow-hidden text-stone-100 flex flex-col h-[85vh]">
        {/* Modal Top Bar */}
        <div className="px-6 py-4 bg-stone-950 border-b border-stone-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 p-0.5 shadow-md flex items-center justify-center">
              <div className="w-full h-full bg-stone-950 rounded-[14px] flex items-center justify-center text-emerald-400">
                <Bot className="w-5 h-5" />
              </div>
            </div>
            <div>
              <h3 className="font-bold text-emerald-300 text-sm sm:text-base flex items-center gap-2">
                AI黄帝内経・食運動養生アドバイザー
              </h3>
              <p className="text-xs text-stone-400">
                『黄帝内経』『傷寒論』の知恵に基づく非薬物養生AI
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-400 hover:text-stone-200 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Messages List */}
        <div className="p-5 overflow-y-auto flex-1 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-2.5 ${
                msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
                  msg.sender === 'user'
                    ? 'bg-amber-500 text-stone-950'
                    : 'bg-emerald-950 text-emerald-400 border border-emerald-700/50'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[82%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed space-y-2 ${
                  msg.sender === 'user'
                    ? 'bg-amber-600 text-stone-950 font-medium rounded-tr-none'
                    : 'bg-stone-800/90 border border-stone-700/70 text-stone-200 rounded-tl-none whitespace-pre-wrap'
                }`}
              >
                <div>{msg.text}</div>
                <div
                  className={`text-[10px] text-right font-mono ${
                    msg.sender === 'user' ? 'text-stone-900/70' : 'text-stone-400'
                  }`}
                >
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-xs text-emerald-400 p-3 bg-emerald-950/40 border border-emerald-800/40 rounded-2xl w-fit">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>黄帝内経と傷寒論の文献を参照中...</span>
            </div>
          )}
        </div>

        {/* Preset Prompt Chips */}
        <div className="px-5 py-2 bg-stone-950/60 border-t border-stone-800 flex items-center gap-1.5 overflow-x-auto text-xs scrollbar-none">
          <span className="text-stone-500 shrink-0 text-[11px]">おすすめの質問:</span>
          {PRESET_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(p)}
              disabled={isLoading}
              className="px-2.5 py-1 rounded-xl bg-stone-800 hover:bg-stone-750 text-stone-300 border border-stone-700/60 shrink-0 text-[11px] transition"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Chat Input Bar */}
        <div className="p-4 bg-stone-950 border-t border-stone-800 flex items-center gap-2">
          <input
            type="text"
            placeholder="お悩みの症状や食事・運動について質問を入力..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            disabled={isLoading}
            className="flex-1 bg-stone-800 border border-stone-700 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-500"
          />

          <button
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputText.trim()}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-stone-950 font-bold p-2.5 sm:px-4 sm:py-2.5 rounded-xl text-xs transition flex items-center gap-1.5 shrink-0 shadow-md"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">送信</span>
          </button>
        </div>
      </div>
    </div>
  );
};



// ==========================================
// File: src/components/BirthdateFiveElementsCard.tsx
// ==========================================
import React, { useState, useEffect } from 'react';
import { ElementType } from '../types';
import { FIVE_ELEMENT_INFO } from '../data/orientalData';
import { Calendar, Sparkles, Utensils, Palette, Heart, Check, Info, Gem } from 'lucide-react';
import { playClickSound } from '../utils/sound';

export const FIVE_ELEMENT_RECS: Record<
  ElementType,
  {
    kanji: string;
    name: string;
    organ: string;
    stemNames: string;
    colors: string[];
    colorHexs: string[];
    colorBg: string;
    colorText: string;
    colorDesc: string;
    foods: string[];
    foodDesc: string;
    flavor: string;
    goodItems: string[];
    stones: string[];
    stoneDesc: string;
  }
> = {
  wood: {
    kanji: '木',
    name: '木 (もく・甲/乙)',
    organ: '肝・胆（自律神経・目・感情）',
    stemNames: '生まれ年の末尾が 4, 5 の方',
    colors: ['青色', '緑色', 'エメラルドグリーン', '萌黄色'],
    colorHexs: ['#10B981', '#059669', '#047857'],
    colorBg: 'bg-emerald-950/80 border-emerald-700/80',
    colorText: 'text-emerald-300',
    colorDesc: '青・緑色は「肝」の気をのびやかに巡らせ、目や首肩の緊張、ストレスやイライラを和らげます。身につける小物や植物を取り入れるのがおすすめ。',
    foods: ['酸味（レモン・酢の物・シトラス）', 'ほうれん草・ブロッコリー・小松菜', '緑茶・ジャスミン茶', 'しそ・ハーブ・春菊'],
    foodDesc: '爽やかな酸味と緑の野菜が「肝」の鬱滞（うったい）を解き、目の疲れや頭重感をすっきりクリアにします。',
    flavor: '酸味（すっぱい）',
    goodItems: ['観葉植物', '緑のハンカチ', 'シトラスアロマ', 'ホットアイマスク'],
    stones: ['翡翠（ヒスイ）', 'アベンチュリン（緑水晶）', 'エメラルド', 'ペリドット', 'グリーンアゲート'],
    stoneDesc: '新緑の生命力を宿す緑の天然石。「肝」の気をのびやかに伸ばし、イライラ・ストレス・目の疲れを優しく穏やかに癒やします。',
  },
  fire: {
    kanji: '火',
    name: '火 (か・丙/丁)',
    organ: '心・小腸（循環器・精神・睡眠）',
    stemNames: '生まれ年の末尾が 6, 7 の方',
    colors: ['赤色', '朱色', 'ピンク', 'ローズ'],
    colorHexs: ['#EF4444', '#DC2626', '#B91C1C'],
    colorBg: 'bg-red-950/80 border-red-700/80',
    colorText: 'text-red-300',
    colorDesc: '赤・朱色は「心（血脈・情熱）」を温めて全身の血液循環と意欲を高めます。冷えややる気低下を感じる時は赤い服やアクセントカラーを！',
    foods: ['苦味（ゴーヤ・緑茶）', 'トマト・赤パプリカ', '小豆（あずき）・ナツメ', '赤身魚・マグロ', 'はとむぎ'],
    foodDesc: 'ほんのりした苦味と赤い食材が余分な熱を鎮め、血脈を整えて穏やかな睡眠と心の安定をもたらします。',
    flavor: '苦味（にがい）',
    goodItems: ['赤いファッション小物', 'お香・温かいお茶', 'ウォーキングシューズ', 'キャンドル'],
    stones: ['カーネリアン（紅玉髄）', 'ルビー', 'ガーネット（柘榴石）', 'レッドジャスパー', 'ロードクロサイト'],
    stoneDesc: '情熱と血脈を温める赤い天然石。「心」の血行を高め、冷えや感情の沈みを吹き飛ばして全身に明るいパワーと輝きを与えます。',
  },
  earth: {
    kanji: '土',
    name: '土 (ど・戊/己)',
    organ: '脾・胃（消化吸収・エネルギー生出）',
    stemNames: '生まれ年の末尾が 8, 9 の方',
    colors: ['黄色', '茶色', 'ベージュ', '山吹色'],
    colorHexs: ['#F59E0B', '#D97706', '#B45309'],
    colorBg: 'bg-amber-950/80 border-amber-700/80',
    colorText: 'text-amber-300',
    colorDesc: '黄色・茶系色は「脾胃（お腹ボイラー）」を温めて活性化し、食べ物から気血を作る胃腸の働きをサポートします。',
    foods: ['自然な甘味（かぼちゃ・さつまいも・山芋）', '大豆・豆腐・味噌', '温かいお粥', '温かいスープ・お味噌汁', '栗・キャベツ'],
    foodDesc: '素材本来の優しい甘みが胃腸の消化吸収を高め、お腹の冷えや食後のだるさ・湿気重だるさを優しくケアします。',
    flavor: '甘味（ほのかな甘み）',
    goodItems: ['腹巻・温熱カイロ', '陶器のマグカップ', 'ベージュのストール', '土鍋料理'],
    stones: ['タイガーアイ（虎目石）', 'シトリン（黄水晶）', 'アンバー（琥珀）', 'イエローカルサイト', 'アラゴナイト'],
    stoneDesc: '大地の温もりと安心感をもたらす黄・黄金のパワーストーン。「脾胃（胃腸）」をしっかり温めて不安や思考過多を和らげます。',
  },
  metal: {
    kanji: '金',
    name: '金 (ごん・庚/辛)',
    organ: '肺・大腸（呼吸器・皮膚・免疫バリア）',
    stemNames: '生まれ年の末尾が 0, 1 の方',
    colors: ['白色', '銀色', 'パールホワイト', 'ライトグレー'],
    colorHexs: ['#E2E8F0', '#94A3B8', '#64748B'],
    colorBg: 'bg-slate-900/90 border-slate-700/80',
    colorText: 'text-slate-200',
    colorDesc: '白色・銀色は「肺（呼吸器・肌バリア）」を潤し、外部からの風邪や乾燥ダメージをブロックするバリア（衛気）を強化します。',
    foods: ['辛味（生姜・大根・長ネギ・ニンニク）', 'レンコン（蓮根）・山芋', '梨（ナシ）・白きくらげ', '豆腐・白ごま', 'ハチミツ白湯'],
    foodDesc: '白い食材とほんのり辛い薬味が喉や呼吸器・皮膚を乾燥から守り、免疫バリア（衛気）を強く育てます。',
    flavor: '辛味（ピリッと辛い）',
    goodItems: ['白い服やマスク', '加湿器・アロマディフューザー', 'シルクの寝具', '乾布摩擦タオル'],
    stones: ['水晶（ロッククリスタル）', 'ムーンストーン（月長石）', 'ホワイトオニキス', 'シルバーアゲート', 'セルサイト'],
    stoneDesc: '清浄な免疫バリアと浄化力を与える白・透明の天然石。「肺・大腸」を浄化し、乾燥や邪気（ウイルス・寒気）から身を守ります。',
  },
  water: {
    kanji: '水',
    name: '水 (すい・壬/癸)',
    organ: '肾・膀胱（生命力・エイジングケア・骨）',
    stemNames: '生まれ年の末尾が 2, 3 の方',
    colors: ['黒色', '紺色', 'ネイビー', 'ダークグレー'],
    colorHexs: ['#3B82F6', '#1E40AF', '#172554'],
    colorBg: 'bg-blue-950/80 border-blue-700/80',
    colorText: 'text-blue-300',
    colorDesc: '黒・紺色は「腎（生命力の根っこ）」の精を深く養い、深部の冷えや老化・疲労を防ぎます。黒いファッションやシックな色合いが吉。',
    foods: ['鹹味（塩け・海の恵み）', '黒ごま・黒豆', 'ひじき・昆布・わかめ', '牡蠣・あさり', 'くるみ・ごぼう・黒きくらげ'],
    foodDesc: 'ミネラル豊富な黒い食材と海のエキスが下半身や腰の冷えを深部から温め、生命力と若々しさを蓄積します。',
    flavor: '鹹味（しおけ）',
    goodItems: ['青竹踏み・ツボ押しグッズ', '足湯バケツ', '黒い靴下・レッグウォーマー', 'オルゴール音楽'],
    stones: ['ラピスラズリ（瑠璃）', 'サファイア', 'アクアマリン', 'ブラックオニキス', 'モリオン（黒水晶）'],
    stoneDesc: '深い海の知恵と生命の源を護る紺・黒・青の天然石。「腎」の精気を強力に守り、深い疲労回復とエイジングケア・アンチエイジングを促します。',
  },
};

export const getElementFromYear = (year: number): ElementType => {
  const lastDigit = Math.abs(year) % 10;
  if (lastDigit === 4 || lastDigit === 5) return 'wood';
  if (lastDigit === 6 || lastDigit === 7) return 'fire';
  if (lastDigit === 8 || lastDigit === 9) return 'earth';
  if (lastDigit === 0 || lastDigit === 1) return 'metal';
  return 'water';
};

interface BirthdateFiveElementsCardProps {
  onSelectElement?: (element: ElementType) => void;
  compact?: boolean;
}

export const BirthdateFiveElementsCard: React.FC<BirthdateFiveElementsCardProps> = ({
  onSelectElement,
  compact = false,
}) => {
  const [year, setYear] = useState<number>(() => {
    const saved = localStorage.getItem('oriental_birth_year');
    return saved ? parseInt(saved, 10) : 1990;
  });

  const [month, setMonth] = useState<number>(() => {
    const saved = localStorage.getItem('oriental_birth_month');
    return saved ? parseInt(saved, 10) : 5;
  });

  const [day, setDay] = useState<number>(() => {
    const saved = localStorage.getItem('oriental_birth_day');
    return saved ? parseInt(saved, 10) : 15;
  });

  const [selectedElement, setSelectedElement] = useState<ElementType>(() => {
    const saved = localStorage.getItem('oriental_birth_element');
    return (saved as ElementType) || getElementFromYear(year);
  });

  // When year changes, update computed element
  const handleYearChange = (newYear: number) => {
    playClickSound();
    setYear(newYear);
    const computed = getElementFromYear(newYear);
    setSelectedElement(computed);
    if (onSelectElement) onSelectElement(computed);
  };

  useEffect(() => {
    localStorage.setItem('oriental_birth_year', year.toString());
    localStorage.setItem('oriental_birth_month', month.toString());
    localStorage.setItem('oriental_birth_day', day.toString());
    localStorage.setItem('oriental_birth_element', selectedElement);
  }, [year, month, day, selectedElement]);

  const handleSelectTab = (el: ElementType) => {
    playClickSound();
    setSelectedElement(el);
    if (onSelectElement) onSelectElement(el);
  };

  const rec = FIVE_ELEMENT_RECS[selectedElement];
  const calculatedElement = getElementFromYear(year);

  const yearsList = [];
  for (let y = 1930; y <= 2026; y++) {
    yearsList.push(y);
  }

  const elementsList: ElementType[] = ['wood', 'fire', 'earth', 'metal', 'water'];

  return (
    <div className="bg-stone-900 border-2 border-amber-500/50 rounded-3xl p-5 sm:p-7 shadow-2xl space-y-6 text-stone-100">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 border-b border-stone-800 pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-black text-amber-300 bg-amber-950 border border-amber-700/80 px-3 py-1 rounded-full flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-amber-400" />
              生年月日 ＆ 本命五行判定
            </span>
            {selectedElement === calculatedElement && (
              <span className="text-[11px] font-bold text-emerald-300 bg-emerald-950/80 border border-emerald-700 px-2.5 py-0.5 rounded-full">
                生年月日から自動算定
              </span>
            )}
          </div>
          <h3 className="text-xl sm:text-2xl font-black text-stone-100 flex items-center gap-2 pt-1">
            あなたの体に「何色・何物・ラッキー石」が良いのかわかる五行診断
          </h3>
          <p className="text-xs sm:text-sm text-stone-300">
            生年月日を選ぶと陰陽五行の「本命五行」が定まり、あなたの身体に合う【養生色（何色）】【おすすめ食材・物（何物）】と【ラッキー天然石（パワーストーン）】がひと目でわかります。
          </p>
        </div>
      </div>

      {/* Birthdate Dropdown Input Bar */}
      <div className="bg-stone-950/80 p-4 rounded-2xl border border-stone-800 space-y-3">
        <label className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
          <Calendar className="w-4 h-4 text-amber-400" />
          <span>生年月日の選択:</span>
        </label>
        <div className="grid grid-cols-3 gap-2.5 sm:gap-4">
          {/* Year */}
          <div>
            <span className="block text-[11px] text-stone-400 font-bold mb-1">年 (西暦)</span>
            <select
              value={year}
              onChange={(e) => handleYearChange(Number(e.target.value))}
              className="w-full bg-stone-850 text-amber-200 border border-stone-700 font-bold text-sm sm:text-base px-3 py-2 rounded-xl focus:outline-none focus:border-amber-400 transition cursor-pointer"
            >
              {yearsList.map((y) => (
                <option key={y} value={y}>
                  {y}年 (末尾: {y % 10})
                </option>
              ))}
            </select>
          </div>

          {/* Month */}
          <div>
            <span className="block text-[11px] text-stone-400 font-bold mb-1">月</span>
            <select
              value={month}
              onChange={(e) => {
                playClickSound();
                setMonth(Number(e.target.value));
              }}
              className="w-full bg-stone-850 text-amber-200 border border-stone-700 font-bold text-sm sm:text-base px-3 py-2 rounded-xl focus:outline-none focus:border-amber-400 transition cursor-pointer"
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <option key={m} value={m}>
                  {m}月
                </option>
              ))}
            </select>
          </div>

          {/* Day */}
          <div>
            <span className="block text-[11px] text-stone-400 font-bold mb-1">日</span>
            <select
              value={day}
              onChange={(e) => {
                playClickSound();
                setDay(Number(e.target.value));
              }}
              className="w-full bg-stone-850 text-amber-200 border border-stone-700 font-bold text-sm sm:text-base px-3 py-2 rounded-xl focus:outline-none focus:border-amber-400 transition cursor-pointer"
            >
              {Array.from({ length: 31 }, (_, i) => i + 1).map((d) => (
                <option key={d} value={d}>
                  {d}日
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 5 Elements Selection Bar (5行がわかる選択欄) */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-extrabold text-stone-300 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>5行がわかる選択欄（木・火・土・金・水 切り替え）:</span>
          </span>
          <span className="text-[11px] text-stone-400">
            {year}年生まれの本命: <strong className="text-amber-300">{FIVE_ELEMENT_RECS[calculatedElement].kanji} ({FIVE_ELEMENT_RECS[calculatedElement].organ})</strong>
          </span>
        </div>

        <div className="grid grid-cols-5 gap-1.5 sm:gap-2">
          {elementsList.map((el) => {
            const item = FIVE_ELEMENT_RECS[el];
            const isSelected = selectedElement === el;
            const isCalculated = calculatedElement === el;

            return (
              <button
                key={el}
                onClick={() => handleSelectTab(el)}
                className={`p-2 sm:p-3 rounded-2xl border-2 transition-all flex flex-col items-center justify-center gap-1 relative active:scale-95 cursor-pointer ${
                  isSelected
                    ? 'bg-amber-950 border-amber-400 text-amber-100 shadow-lg scale-105 z-10'
                    : 'bg-stone-850 hover:bg-stone-800 border-stone-750 text-stone-300'
                }`}
              >
                {isCalculated && (
                  <span className="absolute -top-2 bg-emerald-400 text-stone-950 text-[9px] font-black px-1.5 py-0.2 rounded-full border border-emerald-200 shadow-sm">
                    本命
                  </span>
                )}
                <span className="text-xl sm:text-2xl font-black">{item.kanji}</span>
                <span className="text-[10px] sm:text-xs font-bold truncate max-w-full">{item.name.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Body Benefit Details Card */}
      <div className={`p-5 rounded-2xl border-2 space-y-5 ${rec.colorBg}`}>
        {/* Title & Kanji Badge */}
        <div className="flex items-center justify-between border-b border-stone-700/60 pb-3 flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-stone-950 border-2 border-amber-400/80 flex items-center justify-center font-black text-2xl text-amber-300 shadow-md">
              {rec.kanji}
            </div>
            <div>
              <h4 className={`text-lg sm:text-xl font-black ${rec.colorText}`}>
                【{rec.kanji}の性質】{rec.name}
              </h4>
              <p className="text-xs text-stone-300">
                主応臓腑: <strong>{rec.organ}</strong> ｜ {rec.stemNames}
              </p>
            </div>
          </div>

          <div className="bg-stone-950/80 px-3 py-1 rounded-xl border border-stone-700 text-xs text-amber-300 font-bold">
            味覚: {rec.flavor}
          </div>
        </div>

        {/* 1. 何色が体に良いのか (ラッキーカラー・養生色) */}
        <div className="bg-stone-950/80 p-4 rounded-xl border border-stone-800 space-y-2.5">
          <div className="flex items-center gap-2 text-sm font-black text-amber-300">
            <Palette className="w-4 h-4 text-amber-400 shrink-0" />
            <span>体に合う『何色』（養生ラッキーカラー）:</span>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {rec.colors.map((c, i) => (
              <span
                key={i}
                className="text-xs font-extrabold px-3 py-1 rounded-xl bg-stone-900 border border-stone-700 text-stone-100 flex items-center gap-1.5 shadow-sm"
              >
                <span
                  className="w-3 h-3 rounded-full border border-stone-400"
                  style={{ backgroundColor: rec.colorHexs[i % rec.colorHexs.length] }}
                />
                <span>{c}</span>
              </span>
            ))}
          </div>

          <p className="text-xs sm:text-sm text-stone-200 leading-relaxed pt-1">
            {rec.colorDesc}
          </p>
        </div>

        {/* 2. 何物が体に良いのか (おすすめ食材・物) */}
        <div className="bg-stone-950/80 p-4 rounded-xl border border-stone-800 space-y-2.5">
          <div className="flex items-center gap-2 text-sm font-black text-emerald-300">
            <Utensils className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>体に合う『何物』（おすすめ養生食材・味わい）:</span>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {rec.foods.map((fd, i) => (
              <span
                key={i}
                className="text-xs font-bold px-3 py-1.5 rounded-xl bg-emerald-950/90 text-emerald-200 border border-emerald-800/80 flex items-center gap-1"
              >
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>{fd}</span>
              </span>
            ))}
          </div>

          <p className="text-xs sm:text-sm text-stone-200 leading-relaxed pt-1">
            {rec.foodDesc}
          </p>
        </div>

        {/* 3. ラッキー天然石・パワーストーン (新設!) */}
        <div className="bg-stone-950/80 p-4 rounded-xl border border-stone-800 space-y-2.5">
          <div className="flex items-center gap-2 text-sm font-black text-sky-300">
            <Gem className="w-4 h-4 text-sky-400 shrink-0" />
            <span>体に合う『ラッキー天然石・パワーストーン』:</span>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {rec.stones.map((st, i) => (
              <span
                key={i}
                className="text-xs font-black px-3 py-1.5 rounded-xl bg-sky-950/90 text-sky-200 border border-sky-700/80 flex items-center gap-1.5 shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                <span>{st}</span>
              </span>
            ))}
          </div>

          <p className="text-xs sm:text-sm text-stone-200 leading-relaxed pt-1">
            {rec.stoneDesc}
          </p>
        </div>

        {/* 4. おすすめ養生アイテム・生活物 */}
        <div className="bg-stone-950/80 p-4 rounded-xl border border-stone-800 space-y-2">
          <div className="flex items-center gap-2 text-xs font-black text-amber-200">
            <Heart className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>日常で取り入れたい養生アイテム（生活物）:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {rec.goodItems.map((item, idx) => (
              <span
                key={idx}
                className="text-xs font-medium bg-stone-900 border border-stone-700 text-amber-100/90 px-2.5 py-1 rounded-lg"
              >
                • {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};



// ==========================================
// File: src/components/CodeCopyModal.tsx
// ==========================================
import React, { useState, useMemo } from 'react';
import { X, Copy, Check, Code, FileCode, Search, Download, Layers, Terminal } from 'lucide-react';
import { playClickSound } from '../utils/sound';
import { getAllSourceFiles, getCombinedAllCode } from '../utils/codeCollector';
import { STREAMLIT_APP_PY, STREAMLIT_REQUIREMENTS } from '../utils/streamlitCode';

interface CodeCopyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CodeCopyModal: React.FC<CodeCopyModalProps> = ({ isOpen, onClose }) => {
  const [selectedFile, setSelectedFile] = useState<string>('STREAMLIT_APP');
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const fileList = useMemo(() => getAllSourceFiles(), []);

  const filteredFiles = useMemo(() => {
    if (!searchTerm) return fileList;
    return fileList.filter(
      (f) =>
        f.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [fileList, searchTerm]);

  const allCombinedCode = useMemo(() => getCombinedAllCode(), []);

  const activeContent = useMemo(() => {
    if (selectedFile === 'STREAMLIT_APP') return STREAMLIT_APP_PY;
    if (selectedFile === 'STREAMLIT_REQ') return STREAMLIT_REQUIREMENTS;
    if (selectedFile === 'ALL') return allCombinedCode;
    const found = fileList.find((f) => f.path === selectedFile);
    return found ? found.content : '';
  }, [selectedFile, allCombinedCode, fileList]);

  if (!isOpen) return null;

  const handleCopy = (text: string) => {
    playClickSound();
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    playClickSound();
    const element = document.createElement('a');
    const file = new Blob([activeContent], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    let filename = 'app.py';
    if (selectedFile === 'STREAMLIT_REQ') filename = 'requirements.txt';
    else if (selectedFile === 'ALL') filename = 'oriental_yojo_all_code.txt';
    else if (selectedFile !== 'STREAMLIT_APP') filename = selectedFile.replace('/', '_');

    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-stone-950/85 backdrop-blur-md animate-fade-in">
      <div className="bg-stone-900 border border-amber-500/40 rounded-3xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl text-stone-100 overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-stone-800 flex flex-wrap items-center justify-between bg-stone-900/90 shrink-0 gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-amber-500/20 border border-amber-400/40 text-amber-300 shadow-lg shadow-amber-500/10">
              <Code className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-black bg-gradient-to-r from-amber-200 via-amber-400 to-emerald-300 bg-clip-text text-transparent">
                コード閲覧＆GitHub用コピー
              </h3>
              <p className="text-xs text-stone-400">
                Streamlit (Python) 版コード または React (TypeScript) 版コードを自由にコピー・保存できます
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleCopy(activeContent)}
              className={`px-5 py-2.5 rounded-xl text-xs sm:text-sm font-black flex items-center gap-2 transition cursor-pointer shadow-lg active:scale-95 ${
                copied
                  ? 'bg-emerald-600 text-white border border-emerald-400 shadow-emerald-900/50'
                  : 'bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 text-stone-950 border border-amber-200 hover:brightness-110 shadow-amber-500/20'
              }`}
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>コピー完了！</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 text-stone-950" />
                  <span>
                    {selectedFile === 'STREAMLIT_APP'
                      ? 'app.py を一括コピー'
                      : selectedFile === 'STREAMLIT_REQ'
                      ? 'requirements.txt をコピー'
                      : selectedFile === 'ALL'
                      ? '全Reactコードを一括コピー'
                      : 'このファイルをコピー'}
                  </span>
                </>
              )}
            </button>

            <button
              onClick={handleDownload}
              className="p-2.5 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-300 border border-stone-700 transition cursor-pointer"
              title="テキストファイルとして保存"
            >
              <Download className="w-4.5 h-4.5" />
            </button>

            <button
              onClick={() => {
                playClickSound();
                onClose();
              }}
              className="p-2.5 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-400 hover:text-stone-200 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Content Grid */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 min-h-0 divide-y md:divide-y-0 md:divide-x divide-stone-800 overflow-hidden">
          
          {/* File Selector Sidebar */}
          <div className="md:col-span-4 lg:col-span-3 p-4 bg-stone-950/60 flex flex-col gap-3 min-h-0 overflow-y-auto">
            
            {/* Python Streamlit Section */}
            <div className="text-[11px] font-black text-amber-400 uppercase tracking-wider px-1">
              🐍 Python / Streamlit 版 (GitHub用)
            </div>

            <button
              onClick={() => {
                playClickSound();
                setSelectedFile('STREAMLIT_APP');
              }}
              className={`p-3 rounded-2xl border text-left flex items-center gap-3 transition cursor-pointer ${
                selectedFile === 'STREAMLIT_APP'
                  ? 'bg-amber-950 border-amber-500 text-amber-300 font-bold shadow-lg shadow-amber-950/60'
                  : 'bg-stone-900 hover:bg-stone-850 border-stone-800 text-stone-300'
              }`}
            >
              <Terminal className="w-5 h-5 text-emerald-400 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold truncate">app.py (Streamlitメイン)</div>
                <div className="text-[10px] text-amber-300/80">Streamlit Cloudデプロイ用</div>
              </div>
            </button>

            <button
              onClick={() => {
                playClickSound();
                setSelectedFile('STREAMLIT_REQ');
              }}
              className={`p-2.5 rounded-xl border text-left flex items-center gap-2.5 transition cursor-pointer text-xs ${
                selectedFile === 'STREAMLIT_REQ'
                  ? 'bg-amber-950 border-amber-500 text-amber-300 font-bold'
                  : 'bg-stone-900 hover:bg-stone-850 border-stone-800 text-stone-400'
              }`}
            >
              <FileCode className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="truncate">requirements.txt</span>
            </button>

            <div className="border-t border-stone-800 my-1" />

            {/* React TypeScript Section */}
            <div className="text-[11px] font-black text-amber-400 uppercase tracking-wider px-1">
              ⚛️ React / TypeScript 版
            </div>

            <button
              onClick={() => {
                playClickSound();
                setSelectedFile('ALL');
              }}
              className={`p-3 rounded-2xl border text-left flex items-center gap-3 transition cursor-pointer ${
                selectedFile === 'ALL'
                  ? 'bg-amber-950 border-amber-500 text-amber-300 font-bold shadow-lg shadow-amber-950/60'
                  : 'bg-stone-900 hover:bg-stone-850 border-stone-800 text-stone-300'
              }`}
            >
              <Layers className="w-5 h-5 text-amber-400 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold truncate">全Reactファイル統合 (ALL)</div>
                <div className="text-[10px] text-amber-300/80">全 {fileList.length} ファイル一括</div>
              </div>
            </button>

            {/* Search */}
            <div className="relative pt-1">
              <Search className="w-4 h-4 absolute left-3 top-3.5 text-stone-500" />
              <input
                type="text"
                placeholder="ファイル名検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-stone-900 border border-stone-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-stone-200 placeholder-stone-500 focus:outline-none focus:border-amber-500/50"
              />
            </div>

            <div className="space-y-1 overflow-y-auto pr-1">
              {filteredFiles.map((f) => (
                <button
                  key={f.path}
                  onClick={() => {
                    playClickSound();
                    setSelectedFile(f.path);
                  }}
                  className={`w-full px-3 py-1.5 rounded-xl text-left flex items-center gap-2 transition cursor-pointer text-xs ${
                    selectedFile === f.path
                      ? 'bg-emerald-950 border border-emerald-500/70 text-emerald-300 font-bold'
                      : 'bg-stone-900/60 hover:bg-stone-850 border border-stone-800/80 text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5 shrink-0 opacity-70 text-amber-400" />
                  <span className="truncate font-mono text-[11px]">{f.path}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Code View Area */}
          <div className="md:col-span-8 lg:col-span-9 flex flex-col bg-stone-950 min-h-0 overflow-hidden">
            <div className="px-4 py-2.5 bg-stone-900/80 border-b border-stone-800 flex items-center justify-between text-xs text-stone-400 font-mono shrink-0">
              <span className="text-amber-300 font-bold">
                {selectedFile === 'STREAMLIT_APP'
                  ? 'app.py (Streamlit Python メインアプリ)'
                  : selectedFile === 'STREAMLIT_REQ'
                  ? 'requirements.txt'
                  : selectedFile === 'ALL'
                  ? '全Reactソースコード結合'
                  : selectedFile}
              </span>
              <span>{activeContent.split('\n').length} 行</span>
            </div>

            <div className="flex-1 p-4 overflow-auto font-mono text-xs text-stone-300 bg-stone-950 leading-relaxed selection:bg-amber-900 selection:text-amber-100">
              <pre className="whitespace-pre-wrap break-words">{activeContent}</pre>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-stone-800 bg-stone-900/95 flex items-center justify-between text-xs text-stone-400 shrink-0">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>
              {selectedFile.startsWith('STREAMLIT')
                ? 'Python / Streamlit Cloud用コード表示中'
                : 'React / TypeScript Webアプリコード表示中'}
            </span>
          </div>

          <button
            onClick={() => handleCopy(activeContent)}
            className="text-amber-300 hover:text-amber-200 font-bold flex items-center gap-1.5 transition cursor-pointer bg-amber-950/80 border border-amber-700/60 px-3 py-1.5 rounded-lg"
          >
            <Copy className="w-3.5 h-3.5 text-amber-400" />
            <span>表示中コードをコピー</span>
          </button>
        </div>

      </div>
    </div>
  );
};



// ==========================================
// File: src/components/DailyQuestsAndFortune.tsx
// ==========================================
import React, { useState } from 'react';
import { DailyQuest, Badge, FortuneResult } from '../types';
import { FORTUNES } from '../data/orientalData';
import { CheckCircle2, Circle, Sparkles, Award, Trophy, RotateCcw, Calendar, Flame, Coffee, Activity, Moon } from 'lucide-react';

interface DailyQuestsAndFortuneProps {
 quests: DailyQuest[];
 badges: Badge[];
 userLevel: number;
 onToggleQuest: (questId: string) => void;
 onAwardXp: (amount: number) => void;
 onOpenFortuneModal: () => void;
}

export const DailyQuestsAndFortune: React.FC<DailyQuestsAndFortuneProps> = ({
 quests,
 badges,
 userLevel,
 onToggleQuest,
 onAwardXp,
}) => {
 const [currentFortune, setCurrentFortune] = useState<FortuneResult | null>(null);
 const [isSpinning, setIsSpinning] = useState(false);
 const [hasDrawnToday, setHasDrawnToday] = useState(false);

 const completedCount = quests.filter((q) => q.completed).length;

 const handleDrawFortune = () => {
 if (isSpinning) return;
 setIsSpinning(true);

 setTimeout(() => {
 const randomF = FORTUNES[Math.floor(Math.random() * FORTUNES.length)];
 const rarities: FortuneResult['rarity'][] = ['大吉', '中吉', '吉', '養生吉'];
 const result: FortuneResult = {
 ...randomF,
 rarity: rarities[Math.floor(Math.random() * rarities.length)],
 };

 setCurrentFortune(result);
 setIsSpinning(false);
 setHasDrawnToday(true);
 onAwardXp(result.xpBonus);
 }, 1200);
 };

 const getQuestIcon = (name: string) => {
 switch (name) {
 case 'Coffee':
 return <Coffee className="w-4 h-4 text-amber-400" />;
 case 'Activity':
 return <Activity className="w-4 h-4 text-teal-400" />;
 case 'Moon':
 return <Moon className="w-4 h-4 text-indigo-400" />;
 default:
 return <Sparkles className="w-4 h-4 text-emerald-400" />;
 }
 };

 return (
 <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
 {/* Daily Quests Section (Left 7 cols) */}
 <div className="md:col-span-7 bg-stone-900/90 border border-stone-800 rounded-3xl p-5 sm:p-6 text-stone-100 shadow-xl space-y-5">
 <div className="flex items-center justify-between">
 <div className="flex items-center gap-2.5">
 <div className="w-10 h-10 rounded-2xl bg-amber-950 border border-amber-500/40 flex items-center justify-center text-amber-400 text-lg">
 
 </div>
 <div>
 <h3 className="font-bold text-base sm:text-lg text-stone-100">
 本日の五行養生クエスト
 </h3>
 <p className="text-xs text-stone-400">
 毎日遊んで達成！ 達成数: {completedCount} / {quests.length}
 </p>
 </div>
 </div>

 <div className="text-xs font-bold text-amber-400 bg-amber-950/80 border border-amber-800/60 px-3 py-1 rounded-xl">
 {Math.round((completedCount / quests.length) * 100)}% 完了
 </div>
 </div>

 {/* Quest Items */}
 <div className="space-y-2.5">
 {quests.map((quest) => (
 <div
 key={quest.id}
 onClick={() => onToggleQuest(quest.id)}
 className={`p-3.5 rounded-2xl border transition duration-200 cursor-pointer flex items-center justify-between gap-3 ${
 quest.completed
 ? 'bg-emerald-950/30 border-emerald-800/60 text-stone-300'
 : 'bg-stone-800/60 hover:bg-stone-750 border-stone-700/60 text-stone-100'
 }`}
 >
 <div className="flex items-center gap-3">
 <button className="text-stone-400 hover:text-amber-400 transition">
 {quest.completed ? (
 <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-950" />
 ) : (
 <Circle className="w-5 h-5 text-stone-500" />
 )}
 </button>

 <div className="space-y-0.5">
 <div className="flex items-center gap-2">
 {getQuestIcon(quest.iconName)}
 <h4
 className={`text-xs sm:text-sm font-bold ${
 quest.completed ? 'line-through text-stone-400' : 'text-stone-100'
 }`}
 >
 {quest.title}
 </h4>
 </div>
 <p className="text-[11px] text-stone-400 leading-relaxed">
 {quest.description}
 </p>
 </div>
 </div>

 <span className="text-xs font-bold text-amber-300 bg-stone-900 border border-stone-700 px-2.5 py-1 rounded-xl shrink-0">
 +{quest.xpReward} XP
 </span>
 </div>
 ))}
 </div>
 </div>

 {/* Daily Fortune Spinner & Badges (Right 5 cols) */}
 <div className="md:col-span-5 space-y-6">
 {/* Fortune Wheel Box */}
 <div className="bg-stone-900/90 border border-amber-500/30 rounded-3xl p-5 text-stone-100 shadow-xl space-y-4">
 <div className="flex items-center justify-between">
 <div className="flex items-center gap-2">
 <Sparkles className="w-5 h-5 text-amber-400" />
 <h3 className="font-bold text-sm sm:text-base text-amber-300">
 今日の黄帝内経みくじ
 </h3>
 </div>
 <span className="text-[10px] bg-amber-950 text-amber-400 border border-amber-800/50 px-2 py-0.5 rounded-full font-bold">
 1日1回挑戦
 </span>
 </div>

 {currentFortune ? (
 <div className="bg-stone-800/80 border border-amber-500/40 rounded-2xl p-4 space-y-3 animate-fade-in">
 <div className="flex items-center justify-between">
 <span className="text-xs font-bold text-stone-300">
 {currentFortune.title}
 </span>
 <span className="text-xs font-extrabold text-amber-300 bg-amber-950 px-2.5 py-0.5 rounded-full border border-amber-700/50">
 【{currentFortune.rarity}】
 </span>
 </div>

 <div className="bg-stone-950/80 p-3 rounded-xl border border-stone-800 space-y-1">
 <p className="text-xs font-serif font-bold text-amber-200">
 {currentFortune.neijingQuote}
 </p>
 <p className="text-[11px] text-stone-300 leading-relaxed">
 {currentFortune.quoteTranslation}
 </p>
 </div>

 <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
 <div className="bg-stone-900 p-2 rounded-lg border border-stone-800">
 <span className="text-stone-400 block"> 本日のラッキー食材</span>
 <span className="font-bold text-emerald-300">{currentFortune.luckyFood}</span>
 </div>
 <div className="bg-stone-900 p-2 rounded-lg border border-stone-800">
 <span className="text-stone-400 block"> 黄金時間帯</span>
 <span className="font-bold text-teal-300">{currentFortune.luckyTime}</span>
 </div>
 </div>

 <div className="text-center pt-1">
 <span className="text-xs font-bold text-amber-400">
 +{currentFortune.xpBonus} XP 獲得しました！
 </span>
 </div>
 </div>
 ) : (
 <div className="bg-stone-800/60 border border-stone-700/60 rounded-2xl p-6 text-center space-y-3">
 <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-amber-600 via-emerald-600 to-teal-500 p-0.5 shadow-lg flex items-center justify-center">
 <div className="w-full h-full bg-stone-950 rounded-[14px] flex items-center justify-center text-amber-300 text-2xl font-bold">
 ️
 </div>
 </div>
 <div>
 <h4 className="text-sm font-bold text-stone-100">
 古典名作からのおみくじ＆本日の養生運勢
 </h4>
 <p className="text-xs text-stone-400 mt-0.5">
 引くと本日のラッキー食材とボーナスXPを獲得できます！
 </p>
 </div>

 <button
 onClick={handleDrawFortune}
 disabled={isSpinning}
 className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-stone-950 font-bold py-2.5 rounded-xl text-xs transition active:scale-95 shadow-lg flex items-center justify-center gap-2"
 >
 {isSpinning ? (
 <>
 <RotateCcw className="w-4 h-4 animate-spin text-stone-950" />
 <span>おみくじ抽集中...</span>
 </>
 ) : (
 <>
 <Sparkles className="w-4 h-4" />
 <span>養生おみくじを引く (+100 XP)</span>
 </>
 )}
 </button>
 </div>
 )}
 </div>

 {/* Badges Box */}
 <div className="bg-stone-900/90 border border-stone-800 rounded-3xl p-5 text-stone-100 shadow-xl space-y-3">
 <div className="flex items-center gap-2">
 <Trophy className="w-5 h-5 text-amber-400" />
 <h3 className="font-bold text-sm sm:text-base text-stone-100">
 養生勲章バッジ（レベル解放）
 </h3>
 </div>

 <div className="grid grid-cols-5 gap-2">
 {badges.map((b) => {
 const isUnlocked = userLevel >= b.requiredLevel;

 return (
 <div
 key={b.id}
 title={`${b.name}: ${b.description}`}
 className={`p-2 rounded-2xl border text-center transition flex flex-col items-center justify-center gap-1 ${
 isUnlocked
 ? 'bg-amber-950/40 border-amber-500/50 text-amber-300 shadow'
 : 'bg-stone-800/40 border-stone-700/40 text-stone-600 opacity-50'
 }`}
 >
 <span className="text-xl">{b.icon}</span>
 <span className="text-[10px] font-bold line-clamp-1">{b.name}</span>
 </div>
 );
 })}
 </div>
 </div>
 </div>
 </div>
 );
};



// ==========================================
// File: src/components/FiveElementsChart.tsx
// ==========================================
import React, { useState } from 'react';
import { FiveElementsScore, ElementType } from '../types';
import { FIVE_ELEMENT_INFO } from '../data/orientalData';
import { Utensils, Activity, Sliders, Info, ShieldCheck, Sparkles } from 'lucide-react';
import { BirthdateFiveElementsCard } from './BirthdateFiveElementsCard';

interface FiveElementsChartProps {
 score: FiveElementsScore;
 onChangeScore?: (newScore: FiveElementsScore) => void;
}

export const FiveElementsChart: React.FC<FiveElementsChartProps> = ({
 score,
 onChangeScore,
}) => {
 const [selectedElement, setSelectedElement] = useState<ElementType>('earth');
 const [isEditMode, setIsEditMode] = useState(false);

 const elements: ElementType[] = ['wood', 'fire', 'earth', 'metal', 'water'];

 // Calculate Radar Polygon Points
 // Pentagon angles: Wood (top 90deg/270), Fire (top-right), Earth (bottom-right), Metal (bottom-left), Water (top-left)
 const angles = [270, 342, 54, 126, 198]; // Degrees
 const center = 120;
 const maxRadius = 85;

 const getCoordinates = (index: number, value: number) => {
 const angleRad = (angles[index] * Math.PI) / 180;
 const r = (Math.min(100, Math.max(0, value)) / 100) * maxRadius;
 const x = center + r * Math.cos(angleRad);
 const y = center + r * Math.sin(angleRad);
 return { x, y };
 };

 const polyPoints = elements
 .map((el, i) => {
 const val = score[el] || 20;
 const { x, y } = getCoordinates(i, val);
 return `${x},${y}`;
 })
 .join(' ');

 // Grid background polygons (20%, 40%, 60%, 80%, 100%)
 const gridPolygons = [0.2, 0.4, 0.6, 0.8, 1.0].map((scale) => {
 return angles
 .map((deg) => {
 const rad = (deg * Math.PI) / 180;
 const x = center + maxRadius * scale * Math.cos(rad);
 const y = center + maxRadius * scale * Math.sin(rad);
 return `${x},${y}`;
 })
 .join(' ');
 });

 // Highest and lowest
 let maxEl: ElementType = 'wood';
 let minEl: ElementType = 'wood';
 let maxVal = -1;
 let minVal = 999;

 elements.forEach((el) => {
 const v = score[el] || 0;
 if (v > maxVal) {
 maxVal = v;
 maxEl = el;
 }
 if (v < minVal) {
 minVal = v;
 minEl = el;
 }
 });

 const currentInfo = FIVE_ELEMENT_INFO[selectedElement];

 const handleSliderChange = (el: ElementType, newVal: number) => {
 if (onChangeScore) {
 onChangeScore({
 ...score,
 [el]: newVal,
 });
 }
 };

 return (
 <div className="bg-stone-900/90 border border-stone-800 rounded-3xl p-5 sm:p-6 text-stone-100 shadow-xl space-y-6">
 {/* Title */}
 <div className="flex items-center justify-between flex-wrap gap-2">
 <div className="flex items-center gap-2.5">
 <div className="w-10 h-10 rounded-2xl bg-emerald-950 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-lg">
 五
 </div>
 <div>
 <h3 className="font-bold text-base sm:text-lg text-stone-100 flex items-center gap-2">
 五行（木・火・土・金・水）バランスチェック
 </h3>
 <p className="text-xs text-stone-400">
 黄帝内経の五臓六腑相生相剋の理に基づく五行図チャート
 </p>
 </div>
 </div>

 <button
 onClick={() => setIsEditMode(!isEditMode)}
 className="text-xs bg-stone-800 hover:bg-stone-700 text-amber-300 border border-amber-500/30 px-3 py-1.5 rounded-xl font-medium flex items-center gap-1.5 transition"
 >
 <Sliders className="w-3.5 h-3.5" />
 {isEditMode ? '完了' : '手動調整'}
 </button>
 </div>

 <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
 {/* Polygon Chart Area */}
 <div className="md:col-span-5 flex flex-col items-center justify-center">
 <div className="relative w-[240px] h-[240px] sm:w-[260px] sm:h-[260px] flex items-center justify-center">
 <svg viewBox="0 0 240 240" className="w-full h-full overflow-visible">
 {/* Grid Pentagon Lines */}
 {gridPolygons.map((pts, i) => (
 <polygon
 key={i}
 points={pts}
 fill="none"
 stroke="rgba(255,255,255,0.08)"
 strokeWidth="1"
 />
 ))}

 {/* Axis Lines */}
 {angles.map((deg, i) => {
 const rad = (deg * Math.PI) / 180;
 const x = center + maxRadius * Math.cos(rad);
 const y = center + maxRadius * Math.sin(rad);
 return (
 <line
 key={i}
 x1={center}
 y1={center}
 x2={x}
 y2={y}
 stroke="rgba(255,255,255,0.12)"
 strokeWidth="1"
 strokeDasharray="2,2"
 />
 );
 })}

 {/* Value Polygon Fill */}
 <polygon
 points={polyPoints}
 fill="rgba(16, 185, 129, 0.25)"
 stroke="#10B981"
 strokeWidth="2.5"
 className="transition-all duration-500"
 />

 {/* Data Points */}
 {elements.map((el, i) => {
 const val = score[el] || 20;
 const { x, y } = getCoordinates(i, val);
 const info = FIVE_ELEMENT_INFO[el];
 const isSel = selectedElement === el;

 return (
 <circle
 key={el}
 cx={x}
 cy={y}
 r={isSel ? "6" : "4.5"}
 fill={info.color}
 stroke="#1c1917"
 strokeWidth="2"
 className="cursor-pointer transition-all duration-300 hover:scale-125"
 onClick={() => setSelectedElement(el)}
 />
 );
 })}

 {/* Element Label Nodes */}
 {elements.map((el, i) => {
 const info = FIVE_ELEMENT_INFO[el];
 const labelRad = (angles[i] * Math.PI) / 180;
 const lx = center + (maxRadius + 22) * Math.cos(labelRad);
 const ly = center + (maxRadius + 22) * Math.sin(labelRad);
 const isSelected = selectedElement === el;

 return (
 <g
 key={`lbl-${el}`}
 transform={`translate(${lx}, ${ly})`}
 className="cursor-pointer"
 onClick={() => setSelectedElement(el)}
 >
 <circle
 r="14"
 fill={isSelected ? info.color : "#292524"}
 stroke={info.color}
 strokeWidth="1.5"
 />
 <text
 textAnchor="middle"
 dy="4"
 fontSize="11"
 fontWeight="bold"
 fill={isSelected ? "#1c1917" : "#f5f5f4"}
 >
 {info.kanji}
 </text>
 </g>
 );
 })}
 </svg>
 </div>

 {/* Quick Stats Badges */}
 <div className="flex items-center gap-2 mt-4 text-xs">
 <span className="px-2.5 py-1 rounded-lg bg-emerald-950/80 border border-emerald-800/60 text-emerald-300">
 優勢: <strong>{FIVE_ELEMENT_INFO[maxEl].kanji} ({FIVE_ELEMENT_INFO[maxEl].organ})</strong>
 </span>
 <span className="px-2.5 py-1 rounded-lg bg-amber-950/80 border border-amber-800/60 text-amber-300">
 補強: <strong>{FIVE_ELEMENT_INFO[minEl].kanji} ({FIVE_ELEMENT_INFO[minEl].organ})</strong>
 </span>
 </div>
 </div>

 {/* Element Details & Customizer Area */}
 <div className="md:col-span-7 space-y-4">
 {/* Element Selection Pills */}
 <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
 {elements.map((el) => {
 const info = FIVE_ELEMENT_INFO[el];
 const isSelected = selectedElement === el;
 return (
 <button
 key={el}
 onClick={() => setSelectedElement(el)}
 className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 ${
 isSelected
 ? 'bg-amber-500 text-stone-950 shadow-md scale-105'
 : 'bg-stone-800 hover:bg-stone-750 text-stone-300 border border-stone-700/60'
 }`}
 >
 <span
 className="w-2.5 h-2.5 rounded-full inline-block"
 style={{ backgroundColor: info.color }}
 />
 {info.name}
 </button>
 );
 })}
 </div>

 {/* Edit Sliders Mode */}
 {isEditMode ? (
 <div className="bg-stone-800/60 border border-stone-700/60 rounded-2xl p-4 space-y-3">
 <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
 <Sliders className="w-3.5 h-3.5" /> 五行エネルギーの手動バランス調整
 </h4>
 {elements.map((el) => {
 const info = FIVE_ELEMENT_INFO[el];
 const val = score[el] || 20;
 return (
 <div key={el} className="flex items-center gap-3 text-xs">
 <span className="w-16 font-bold" style={{ color: info.color }}>
 {info.kanji} ({info.organ})
 </span>
 <input
 type="range"
 min="5"
 max="100"
 value={val}
 onChange={(e) => handleSliderChange(el, Number(e.target.value))}
 className="flex-1 accent-amber-500 h-1.5 bg-stone-900 rounded-lg cursor-pointer"
 />
 <span className="w-8 text-right font-mono text-stone-300">{val}%</span>
 </div>
 );
 })}
 </div>
 ) : (
 /* Selected Element Deep Dive Card */
 <div className="bg-stone-800/60 border border-stone-700/60 rounded-2xl p-4 space-y-4">
 <div className="flex items-center justify-between border-b border-stone-700/50 pb-3">
 <div>
 <div className="flex items-center gap-2">
 <span
 className="w-3 h-3 rounded-full"
 style={{ backgroundColor: currentInfo.color }}
 />
 <h4 className="font-bold text-stone-100 text-base">
 {currentInfo.name} ── {currentInfo.organ}
 </h4>
 </div>
 <p className="text-xs text-stone-400 mt-0.5">
 季節: {currentInfo.season} ｜ 感情: {currentInfo.emotion} ｜ 味覚: {currentInfo.flavor}
 </p>
 </div>

 <div className="text-right">
 <span className="text-xl font-mono font-bold text-amber-400">
 {score[selectedElement] || 20}%
 </span>
 </div>
 </div>

 <p className="text-xs text-stone-300 leading-relaxed bg-stone-900/60 p-3 rounded-xl border border-stone-800">
 {currentInfo.desc}
 </p>

 {/* Food & Exercise Advice Columns */}
 <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
 {/* Food Column */}
 <div className="bg-stone-900/80 border border-emerald-900/40 rounded-xl p-3 space-y-2">
 <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-xs">
 <Utensils className="w-3.5 h-3.5" />
 <span>おすすめ食養生（薬なし無薬食）</span>
 </div>
 <div className="flex flex-wrap gap-1.5 pt-1">
 {currentInfo.goodFoods.map((f, idx) => (
 <span
 key={idx}
 className="text-xs bg-emerald-950/80 text-emerald-200 border border-emerald-800/60 px-2.5 py-1 rounded-lg font-medium flex items-center gap-1"
 >
 <span></span>
 <span>{f}</span>
 </span>
 ))}
 </div>
 </div>

 {/* Exercise Column */}
 <div className="bg-stone-900/80 border border-teal-900/40 rounded-xl p-3 space-y-2">
 <div className="flex items-center gap-1.5 text-teal-400 font-bold text-xs">
 <Activity className="w-3.5 h-3.5" />
 <span>おすすめ運動＆経絡ストレッチ</span>
 </div>
 <div className="flex flex-wrap gap-1.5 pt-1">
 {currentInfo.goodExercises.map((ex, idx) => (
 <span
 key={idx}
 className="text-xs bg-teal-950/80 text-teal-200 border border-teal-800/60 px-2.5 py-1 rounded-lg font-medium flex items-center gap-1"
 >
 <span></span>
 <span>{ex}</span>
 </span>
 ))}
 </div>
 </div>
 </div>
 </div>
 )}
 </div>
 </div>

 {/* Birthdate & 5-Elements Color & Food Card */}
 <div className="pt-2">
 <BirthdateFiveElementsCard />
 </div>
 </div>
 );
};



// ==========================================
// File: src/components/Header.tsx
// ==========================================
import React from 'react';
import { Sparkles, Flame, BookOpen, HelpCircle, Compass, Bot, Code, Home } from 'lucide-react';
import { RelaxBGMPlayer } from './RelaxBGMPlayer';
import { playClickSound } from '../utils/sound';

interface HeaderProps {
  level: number;
  xp: number;
  maxXp: number;
  streak: number;
  levelTitle: string;
  seasonName: string;
  onOpenQuiz: () => void;
  onOpenAIConsult: () => void;
  onOpenFortune: () => void;
  onOpenCodeCopy?: () => void;
  onGoHome?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  level,
  xp,
  maxXp,
  streak,
  levelTitle,
  seasonName,
  onOpenQuiz,
  onOpenAIConsult,
  onOpenFortune,
  onOpenCodeCopy,
  onGoHome,
}) => {
  const xpPercent = Math.min(100, Math.round((xp / maxXp) * 100));

  return (
    <header className="sticky top-0 z-30 bg-stone-900/90 backdrop-blur-md border-b border-stone-800 text-stone-100 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20 gap-2">
          {/* Logo & Title (Clickable to Go Home) */}
          <div
            onClick={() => {
              if (onGoHome) {
                playClickSound();
                onGoHome();
              }
            }}
            className="flex items-center gap-3 cursor-pointer group"
            title="トップページ（総合ダッシュボード）に戻る"
          >
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-gradient-to-tr from-amber-600 via-emerald-600 to-teal-500 p-0.5 shadow-md flex items-center justify-center group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-stone-950 rounded-[14px] flex items-center justify-center text-amber-400 font-bold text-lg sm:text-xl border border-amber-500/30">
                養
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-xl font-bold bg-gradient-to-r from-amber-200 via-amber-400 to-emerald-300 bg-clip-text text-transparent group-hover:underline decoration-amber-400/50">
                  東洋養生ナビ
                </h1>
                <span className="hidden sm:inline-block text-xs px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 font-medium">
                  黄帝内経×傷寒論
                </span>
              </div>
              <p className="text-xs text-stone-400 hidden sm:block">
                五行バランス＆無薬・食運動養生ゲーム
              </p>
            </div>
          </div>

          {/* Gamification Stats */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Level & XP */}
            <div className="bg-stone-800/80 border border-stone-700/60 rounded-xl px-2.5 py-1.5 sm:px-3.5 sm:py-2 flex items-center gap-2.5">
              <div className="flex flex-col items-end">
                <div className="flex items-center gap-1">
                  <span className="text-xs text-amber-400 font-bold">Lv.{level}</span>
                  <span className="text-[11px] text-stone-300 font-medium hidden md:inline">
                    {levelTitle}
                  </span>
                </div>
                {/* XP Progress Bar */}
                <div className="w-20 sm:w-28 h-1.5 bg-stone-900 rounded-full overflow-hidden border border-stone-700/50 mt-0.5">
                  <div
                    className="h-full bg-gradient-to-r from-amber-500 via-emerald-400 to-teal-300 transition-all duration-500"
                    style={{ width: `${xpPercent}%` }}
                  />
                </div>
              </div>
              <div className="text-[10px] sm:text-xs text-stone-400">
                {xp}/{maxXp} XP
              </div>
            </div>

            {/* Streak Counter */}
            <div className="bg-amber-950/40 border border-amber-800/50 rounded-xl px-2.5 py-1.5 sm:px-3 sm:py-2 flex items-center gap-1.5 text-amber-400">
              <Flame className="w-4 h-4 fill-amber-500 text-amber-500 animate-pulse" />
              <span className="text-xs sm:text-sm font-bold">{streak}日</span>
              <span className="text-[10px] text-amber-300/80 hidden lg:inline">連続</span>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              {onGoHome && (
                <button
                  onClick={() => {
                    playClickSound();
                    onGoHome();
                  }}
                  className="bg-amber-950/80 hover:bg-amber-900/90 text-amber-300 border border-amber-600/50 p-2 sm:px-3 sm:py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition active:scale-95 cursor-pointer shadow-sm"
                  title="トップページに戻る"
                >
                  <Home className="w-4 h-4 text-amber-400" />
                  <span className="hidden sm:inline">トップ</span>
                </button>
              )}

              {/* Relax BGM Player */}
              <RelaxBGMPlayer />

              <button
                onClick={() => {
                  playClickSound();
                  onOpenAIConsult();
                }}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white p-2 sm:px-3 sm:py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 shadow-md shadow-emerald-950/40 transition active:scale-95 cursor-pointer"
                title="AI養生アドバイザー"
              >
                <Bot className="w-4 h-4 text-emerald-200" />
                <span className="hidden sm:inline">AI養生相談</span>
              </button>

              <button
                onClick={() => {
                  playClickSound();
                  onOpenFortune();
                }}
                className="bg-stone-800 hover:bg-stone-700 text-amber-300 border border-amber-500/30 p-2 sm:px-3 sm:py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 transition active:scale-95 cursor-pointer"
                title="今日の養生みくじ"
              >
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="hidden md:inline">養生みくじ</span>
              </button>

              <button
                onClick={() => {
                  playClickSound();
                  onOpenQuiz();
                }}
                className="bg-amber-600 hover:bg-amber-500 text-stone-950 font-bold p-2 sm:px-3 sm:py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md transition active:scale-95 cursor-pointer"
                title="体質＆五行アンケート"
              >
                <HelpCircle className="w-4 h-4" />
                <span className="hidden md:inline">体質診断</span>
              </button>

              {onOpenCodeCopy && (
                <button
                  onClick={() => {
                    playClickSound();
                    onOpenCodeCopy();
                  }}
                  className="bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:brightness-110 text-stone-950 px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-xl text-xs font-black flex items-center gap-1.5 transition active:scale-95 cursor-pointer shadow-md shadow-amber-500/20 border border-amber-200"
                  title="全ソースコードをコピー"
                >
                  <Code className="w-4 h-4 text-stone-950 shrink-0" />
                  <span className="font-extrabold text-xs">全コードコピー</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};



// ==========================================
// File: src/components/OrganClock.tsx
// ==========================================
import React, { useState, useEffect } from 'react';
import { OrganClockSlot } from '../types';
import { ORGAN_CLOCK_SLOTS, FIVE_ELEMENT_INFO } from '../data/orientalData';
import { Clock, Sun, Moon, AlertCircle, Sparkles, Compass } from 'lucide-react';

export const OrganClock: React.FC = () => {
  const [currentHour, setCurrentHour] = useState<number>(new Date().getHours());
  const [selectedSlotIndex, setSelectedSlotIndex] = useState<number>(0);

  // Auto detect current time slot
  useEffect(() => {
    const now = new Date().getHours();
    setCurrentHour(now);

    const slotIdx = ORGAN_CLOCK_SLOTS.findIndex((slot) => {
      if (slot.startHour < slot.endHour) {
        return now >= slot.startHour && now < slot.endHour;
      } else {
        // Over midnight e.g. 23:00 - 01:00
        return now >= 23 || now < 1;
      }
    });

    if (slotIdx !== -1) {
      setSelectedSlotIndex(slotIdx);
    }
  }, []);

  const activeSlot = ORGAN_CLOCK_SLOTS[selectedSlotIndex] || ORGAN_CLOCK_SLOTS[0];
  const elementInfo = FIVE_ELEMENT_INFO[activeSlot.element];

  return (
    <div className="bg-stone-900/90 border border-stone-800 rounded-3xl p-5 sm:p-6 text-stone-100 shadow-xl space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-2xl bg-teal-950 border border-teal-500/40 flex items-center justify-center text-teal-400 text-lg">
            時
          </div>
          <div>
            <h3 className="font-bold text-base sm:text-lg text-stone-100 flex items-center gap-2">
              「黄帝内経」24時間 子午流注（体内時計）
            </h3>
            <p className="text-xs text-stone-400">
              時間帯ごとに活性化する十二経絡（五臓六腑）に合わせた自然のリズム養生
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 bg-stone-800 border border-stone-700 px-3 py-1.5 rounded-xl text-xs font-mono text-amber-300">
          <Clock className="w-3.5 h-3.5 text-amber-400" />
          <span>現在時刻: {currentHour.toString().padStart(2, '0')}:00</span>
        </div>
      </div>

      {/* 24-Hour Time Slots Dial Horizontal Scroll */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
        {ORGAN_CLOCK_SLOTS.map((slot, idx) => {
          const isSelected = selectedSlotIndex === idx;

          // Check if this is the actual real-time slot
          const isRealNow =
            slot.startHour < slot.endHour
              ? currentHour >= slot.startHour && currentHour < slot.endHour
              : currentHour >= 23 || currentHour < 1;

          return (
            <button
              key={idx}
              onClick={() => setSelectedSlotIndex(idx)}
              className={`p-3 rounded-2xl flex flex-col items-center gap-1 transition shrink-0 min-w-[100px] relative border ${
                isSelected
                  ? 'bg-gradient-to-b from-amber-600 to-amber-500 text-stone-950 border-amber-400 shadow-lg scale-105 font-bold'
                  : isRealNow
                  ? 'bg-amber-950/60 text-amber-200 border-amber-500/60'
                  : 'bg-stone-800/80 hover:bg-stone-750 text-stone-300 border-stone-700/60'
              }`}
            >
              {isRealNow && (
                <span className="absolute -top-2 bg-amber-400 text-stone-950 font-bold text-[9px] px-1.5 py-0.2 rounded-full shadow">
                  NOW
                </span>
              )}
              <span className="text-xl">{slot.emoji}</span>
              <span className="text-xs font-mono">{slot.timeRange}</span>
              <span className="text-xs font-bold">{slot.organKanji}経</span>
            </button>
          );
        })}
      </div>

      {/* Selected Time Slot Details Card */}
      <div className="bg-stone-800/60 border border-stone-700/60 rounded-2xl p-5 space-y-4 relative overflow-hidden">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{activeSlot.emoji}</span>
              <div>
                <h4 className="font-bold text-lg text-amber-300">
                  {activeSlot.timeRange} ── {activeSlot.organName}
                </h4>
                <p className="text-xs text-stone-400">
                  五行: {elementInfo.name} ｜ 経絡: {activeSlot.meridian}
                </p>
              </div>
            </div>
          </div>

          <span
            className="text-xs font-bold px-3 py-1 rounded-xl border"
            style={{
              backgroundColor: `${elementInfo.color}20`,
              borderColor: elementInfo.color,
              color: elementInfo.color,
            }}
          >
            {elementInfo.kanji}のエネルギー（{elementInfo.organ}）
          </span>
        </div>

        {/* Action & Avoid Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Action Advice */}
          <div className="bg-stone-900/80 border border-emerald-900/50 rounded-xl p-3.5 space-y-1.5">
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-xs">
              <Sparkles className="w-4 h-4" />
              <span>この時間帯のおすすめ養生</span>
            </div>
            <p className="text-xs text-stone-200 leading-relaxed">
              {activeSlot.actionAdvice}
            </p>
          </div>

          {/* Avoid Advice */}
          <div className="bg-stone-900/80 border border-rose-900/50 rounded-xl p-3.5 space-y-1.5">
            <div className="flex items-center gap-1.5 text-rose-400 font-bold text-xs">
              <AlertCircle className="w-4 h-4" />
              <span>この時間帯に避けるべきこと</span>
            </div>
            <p className="text-xs text-stone-200 leading-relaxed">
              {activeSlot.avoidAdvice}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};



// ==========================================
// File: src/components/QuestionnaireModal.tsx
// ==========================================
import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  CheckCircle,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  RefreshCw,
  Trophy,
  SkipForward,
  PlusCircle,
  BarChart2,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { FiveElementsScore, ShanghanType } from '../types';
import { QUIZ_QUESTIONS } from '../data/orientalData';
import { playClickSound, playChimeSound } from '../utils/sound';

interface QuestionnaireModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (scores: FiveElementsScore, shanghan: ShanghanType, earnedXp: number) => void;
}

const OPTION_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

export const QuestionnaireModal: React.FC<QuestionnaireModalProps> = ({
  isOpen,
  onClose,
  onComplete,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [showResultAnimation, setShowResultAnimation] = useState(false);
  const [earnedXpTotal, setEarnedXpTotal] = useState(0);
  const [targetQuestionCount, setTargetQuestionCount] = useState(20);
  const [showCheckpoint, setShowCheckpoint] = useState(false);
  const [showBirthdateStep, setShowBirthdateStep] = useState(false);

  // Audio TTS states
  const [isSpeakingQuestion, setIsSpeakingQuestion] = useState(false);
  const [autoRead, setAutoRead] = useState(false);

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const questionBoxRef = useRef<HTMLDivElement>(null);

  // Speak current question aloud
  const speakCurrentQuestion = (questionObj = QUIZ_QUESTIONS[currentStep]) => {
    if (!('speechSynthesis' in window) || !questionObj) return;

    window.speechSynthesis.cancel();

    const optionsText = questionObj.options
      .map((opt, i) => `選択肢 ${OPTION_LETTERS[i] || i + 1}。 ${opt.text}`)
      .join('。 ');

    const textToSpeak = `第 ${questionObj.id} 問。 ${questionObj.question}。 ${optionsText}`;

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = 'ja-JP';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onend = () => setIsSpeakingQuestion(false);
    utterance.onerror = () => setIsSpeakingQuestion(false);

    setIsSpeakingQuestion(true);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeakingQuestion(false);
    }
  };

  const toggleSpeakQuestion = () => {
    if (isSpeakingQuestion) {
      stopSpeaking();
    } else {
      speakCurrentQuestion();
    }
  };

  // Auto-scroll & Auto TTS on step change
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if (autoRead && !showCheckpoint && !showBirthdateStep && !showResultAnimation && isOpen) {
      speakCurrentQuestion();
    } else {
      stopSpeaking();
    }
  }, [currentStep, showCheckpoint, showBirthdateStep, showResultAnimation, autoRead, isOpen]);

  // Clean up speech on close or unmount
  useEffect(() => {
    return () => {
      stopSpeaking();
    };
  }, [isOpen]);

  // Reset state when opening modal
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
      setAnswers([]);
      setShowResultAnimation(false);
      setShowCheckpoint(false);
      setShowBirthdateStep(false);
      setTargetQuestionCount(20);
      setEarnedXpTotal(0);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const maxAvailable = QUIZ_QUESTIONS.length;
  const currentQ = QUIZ_QUESTIONS[currentStep] || QUIZ_QUESTIONS[0];
  const totalQuestionsToDisplay = Math.min(targetQuestionCount, maxAvailable);

  const handleSelectOption = (optionIndex: number) => {
    playClickSound();
    stopSpeaking();
    const newAnswers = [...answers];
    newAnswers[currentStep] = optionIndex;
    setAnswers(newAnswers);
    if (currentQ?.options[optionIndex]) {
      setEarnedXpTotal((prev) => prev + (currentQ.options[optionIndex].xp || 20));
    }

    const nextStep = currentStep + 1;
    if (nextStep < totalQuestionsToDisplay) {
      setCurrentStep(nextStep);
    } else if (targetQuestionCount < maxAvailable && nextStep >= targetQuestionCount) {
      setShowCheckpoint(true);
    } else {
      setShowBirthdateStep(true);
    }
  };

  const handleExtendQuestions = (addCount: number) => {
    playClickSound();
    const nextTarget = Math.min(targetQuestionCount + addCount, maxAvailable);
    setTargetQuestionCount(nextTarget);
    setShowCheckpoint(false);
    setCurrentStep(currentStep + 1);
  };

  const handlePrevStep = () => {
    playClickSound();
    if (showBirthdateStep) {
      setShowBirthdateStep(false);
      return;
    }
    if (showCheckpoint) {
      setShowCheckpoint(false);
      return;
    }
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFinishEarly = () => {
    playClickSound();
    setShowBirthdateStep(true);
  };

  const calculateResults = (finalAnswers: number[]) => {
    playChimeSound();
    setShowCheckpoint(false);
    setShowBirthdateStep(false);

    const elementScores: FiveElementsScore = { wood: 15, fire: 15, earth: 15, metal: 15, water: 15 };
    const shanghanScores: Record<ShanghanType, number> = {
      taiyang: 0,
      shaoyang: 0,
      yangming: 0,
      taiyin: 0,
      shaoyin: 0,
      jueyin: 0,
    };

    finalAnswers.forEach((answerIdx, qIdx) => {
      if (answerIdx === undefined || !QUIZ_QUESTIONS[qIdx]) return;
      const selectedOpt = QUIZ_QUESTIONS[qIdx].options[answerIdx];
      if (!selectedOpt) return;

      // Accumulate element points
      Object.entries(selectedOpt.elements).forEach(([el, pts]) => {
        if (pts) {
          elementScores[el as keyof FiveElementsScore] += pts;
        }
      });

      // Accumulate shanghan points
      Object.entries(selectedOpt.shanghanPoints).forEach(([shType, pts]) => {
        if (pts) {
          shanghanScores[shType as ShanghanType] += pts;
        }
      });
    });

    // Find top shanghan type
    let topShanghan: ShanghanType = 'taiyin';
    let maxPts = -1;
    (Object.keys(shanghanScores) as ShanghanType[]).forEach((sType) => {
      if (shanghanScores[sType] > maxPts) {
        maxPts = shanghanScores[sType];
        topShanghan = sType;
      }
    });

    const totalXp = Math.max(200, finalAnswers.length * 20);
    setShowResultAnimation(true);

    setTimeout(() => {
      onComplete(elementScores, topShanghan, totalXp);
    }, 1800);
  };

  const resetQuiz = () => {
    setCurrentStep(0);
    setAnswers([]);
    setShowResultAnimation(false);
    setShowCheckpoint(false);
    setShowBirthdateStep(false);
    setTargetQuestionCount(20);
    setEarnedXpTotal(0);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-2xl bg-stone-900 border border-amber-500/40 rounded-3xl shadow-2xl overflow-hidden text-stone-100 flex flex-col max-h-[92vh]">
        {/* Modal Top Header */}
        <div className="px-5 py-3.5 bg-stone-950 border-b border-stone-800 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-2xl sm:text-3xl">☯</span>
            <div>
              <h3 className="font-extrabold text-amber-300 text-sm sm:text-base">
                傷寒論＆五行 簡単体質診断アンケート
              </h3>
              <p className="text-xs text-stone-400">
                直感で選ぶだけ！無薬食養生＆経絡レシピがわかる
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-400 hover:text-stone-200 transition"
            title="閉じる"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar & Audio Control Bar */}
        {!showCheckpoint && !showBirthdateStep && !showResultAnimation && (
          <div className="bg-stone-950/80 px-4 sm:px-5 py-2.5 border-b border-stone-800/80 flex items-center justify-between gap-2.5 text-xs shrink-0 flex-wrap">
            <div className="flex-1 flex items-center gap-2.5 min-w-[180px]">
              <span className="font-mono font-black text-amber-400 text-sm sm:text-base shrink-0">
                第 {currentStep + 1} / {totalQuestionsToDisplay} 問
              </span>
              <div className="w-full bg-stone-800 h-3 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-amber-500 via-emerald-400 to-teal-400 h-3 transition-all duration-300 rounded-full"
                  style={{
                    width: `${((currentStep + 1) / totalQuestionsToDisplay) * 100}%`,
                  }}
                />
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {/* Auto Read Toggle Button */}
              <button
                onClick={() => setAutoRead(!autoRead)}
                className={`text-xs font-extrabold px-2.5 py-1 rounded-xl transition flex items-center gap-1 border ${
                  autoRead
                    ? 'bg-amber-500 text-stone-950 border-amber-300 shadow-sm'
                    : 'bg-stone-850 hover:bg-stone-800 text-stone-300 border-stone-700'
                }`}
                title="問題の自動読み上げ"
              >
                <Volume2 className="w-3.5 h-3.5" />
                <span>自動読み上げ: {autoRead ? 'ON' : 'OFF'}</span>
              </button>

              {answers.length > 0 && (
                <button
                  onClick={handleFinishEarly}
                  className="text-xs font-bold text-amber-300 bg-amber-950/90 hover:bg-amber-900 border border-amber-700/60 px-3 py-1 rounded-xl transition flex items-center gap-1.5 shrink-0 shadow-sm cursor-pointer"
                >
                  <SkipForward className="w-3.5 h-3.5 text-amber-400" />
                  <span>診断結果と処方箋を見る</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Content Scroll Area */}
        <div
          ref={scrollContainerRef}
          className="p-5 sm:p-7 overflow-y-auto flex-1 space-y-6 scroll-smooth"
        >
          {showResultAnimation ? (
            <div className="py-12 text-center space-y-4 animate-bounce-short">
              <div className="w-20 h-20 mx-auto rounded-full bg-amber-500/20 border-2 border-amber-400 flex items-center justify-center text-amber-300 shadow-xl shadow-amber-500/10">
                <Trophy className="w-10 h-10 animate-pulse" />
              </div>
              <h4 className="text-2xl sm:text-3xl font-extrabold bg-gradient-to-r from-amber-200 to-amber-400 bg-clip-text text-transparent">
                体質＆五行診断完了！
              </h4>
              <p className="text-sm sm:text-base text-stone-200 font-medium">
                あなた専用の東洋養生プランを生成中...
              </p>
            </div>
          ) : showBirthdateStep ? (
            /* Final Direct Step: View Diagnosis Results & Oriental Prescription */
            <div className="py-6 space-y-6 text-center animate-fade-in">
              <div className="w-16 h-16 mx-auto rounded-full bg-amber-500/20 border-2 border-amber-400 flex items-center justify-center text-amber-300 shadow-xl shadow-amber-500/10">
                <Sparkles className="w-9 h-9" />
              </div>

              <div className="space-y-2">
                <span className="text-xs font-black text-amber-400 bg-amber-950 border border-amber-800 px-3.5 py-1 rounded-full inline-block">
                  体質診断アンケート完了
                </span>
                <h4 className="text-2xl sm:text-3xl font-extrabold text-stone-100">
                  回答お疲れ様でした！
                </h4>
                <p className="text-xs sm:text-sm text-stone-300 max-w-md mx-auto leading-relaxed">
                  集計された回答に基づき、あなた専用の【傷寒論 体質処方箋】と【無薬食養生アドバイス】が準備できました。
                </p>
              </div>

              <button
                onClick={() => calculateResults(answers.length > 0 ? answers : [0])}
                className="w-full max-w-lg mx-auto p-4 rounded-2xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-stone-950 font-black text-base sm:text-lg shadow-xl shadow-amber-500/20 transition flex items-center justify-center gap-2 active:scale-95 border border-amber-200 cursor-pointer"
              >
                <Sparkles className="w-5 h-5 text-stone-950" />
                <span>診断結果と東洋処方箋を見る</span>
                <ArrowRight className="w-5 h-5 text-stone-950" />
              </button>
            </div>
          ) : showCheckpoint ? (
            /* Checkpoint Intermediary Screen */
            <div className="py-4 space-y-6 animate-fade-in text-center">
              <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 border-2 border-emerald-400 flex items-center justify-center text-emerald-300 shadow-xl">
                <CheckCircle className="w-9 h-9" />
              </div>

              <div className="space-y-2">
                <span className="text-xs font-black text-emerald-300 bg-emerald-950/90 border border-emerald-700 px-3.5 py-1 rounded-full inline-block">
                  第 {currentStep} 問 チェックポイント到達！
                </span>
                <h4 className="text-xl sm:text-2xl font-black text-stone-100">
                  体質診断が進みました！
                </h4>
                <p className="text-xs sm:text-sm text-stone-300 max-w-lg mx-auto leading-relaxed pt-1">
                  ここまでの {currentStep} 問で、あなたの【五行バランス】と【傷寒論タイプ】の基礎データが集まりました。すぐに診断結果と処方箋を見ることも、追加の質問に答えて精度を高めることもできます！
                </p>
              </div>

              {/* Action Choices */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2 max-w-xl mx-auto">
                {/* Option A: Continue */}
                {maxAvailable > targetQuestionCount && (
                  <button
                    onClick={() => handleExtendQuestions(10)}
                    className="p-4 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-stone-950 font-bold border border-emerald-400/60 shadow-xl transition-all duration-200 flex flex-col items-center justify-center gap-2 group active:scale-95"
                  >
                    <div className="flex items-center gap-2 text-stone-950 font-black text-sm sm:text-base">
                      <PlusCircle className="w-5 h-5 text-emerald-950 group-hover:scale-110 transition-transform" />
                      <span>追加10問（全{Math.min(targetQuestionCount + 10, maxAvailable)}問）に進む</span>
                    </div>
                  </button>
                )}

                {/* Option B: View Results Now */}
                <button
                  onClick={() => setShowBirthdateStep(true)}
                  className="p-4 rounded-2xl bg-stone-800 hover:bg-stone-750 border border-amber-500/50 hover:border-amber-400 text-amber-200 font-bold shadow-lg transition-all duration-200 flex flex-col items-center justify-center gap-2 group active:scale-95"
                >
                  <div className="flex items-center gap-2 text-amber-300 font-black text-sm sm:text-base">
                    <BarChart2 className="w-5 h-5 text-amber-400 group-hover:scale-110 transition-transform" />
                    <span>診断結果と東洋処方箋を見る</span>
                  </div>
                  <span className="text-[11px] text-amber-300/80">
                    現在の回答で傷寒論体質＆処方箋を出力
                  </span>
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Question Box (Larger Typography & TTS Read Aloud Button) */}
              <div
                ref={questionBoxRef}
                className="bg-stone-850 border-2 border-amber-500/50 rounded-2xl p-5 sm:p-6 relative overflow-hidden shadow-xl space-y-3"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs sm:text-sm font-black text-amber-300 bg-amber-950 border border-amber-700/80 px-3 py-1 rounded-xl shadow-sm">
                    第 {currentQ.id} 問 / {totalQuestionsToDisplay}
                  </span>

                  {/* Manual Question TTS Button */}
                  <button
                    onClick={toggleSpeakQuestion}
                    className={`px-3 py-1.5 rounded-xl text-xs font-black transition flex items-center gap-1.5 border shadow-sm active:scale-95 ${
                      isSpeakingQuestion
                        ? 'bg-amber-500 text-stone-950 border-amber-300 animate-pulse'
                        : 'bg-stone-800 hover:bg-stone-750 text-amber-300 border-amber-500/40'
                    }`}
                  >
                    {isSpeakingQuestion ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-amber-400" />}
                    <span>{isSpeakingQuestion ? '音声停止' : ' 質問を音声で聴く'}</span>
                  </button>
                </div>

                {/* Enlarged Question Title */}
                <h4 className="text-xl sm:text-2xl md:text-3xl font-black text-stone-100 leading-relaxed tracking-wide">
                  {currentQ.question}
                </h4>

                <p className="text-sm sm:text-base text-amber-200/90 font-bold flex items-center gap-2 pt-1 border-t border-stone-800">
                  <span>{currentQ.subtitle}</span>
                </p>
              </div>

              {/* Options list without any 20XP badges for clear viewing */}
              <div className="space-y-3.5">
                {currentQ.options.map((opt, idx) => {
                  const isSelected = answers[currentStep] === idx;
                  const letterBadge = OPTION_LETTERS[idx] || `${idx + 1}`;

                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectOption(idx)}
                      className={`w-full text-left p-4 sm:p-5 rounded-2xl border-2 transition-all duration-200 flex items-center justify-between gap-3 sm:gap-4 group active:scale-[0.99] ${
                        isSelected
                          ? 'bg-amber-950/90 border-amber-400 shadow-xl text-amber-100 scale-[1.01]'
                          : 'bg-stone-800/90 hover:bg-stone-750 border-stone-700/80 hover:border-amber-500/60 text-stone-200'
                      }`}
                    >
                      {/* Left Side: Large Alphabet Badge + Option Text */}
                      <div className="flex items-center gap-3.5 sm:gap-4 flex-1 min-w-0">
                        {/* Option Letter Box A, B, C, D */}
                        <div
                          className={`w-11 h-11 sm:w-13 sm:h-13 rounded-2xl flex items-center justify-center font-black text-xl sm:text-2xl shrink-0 border-2 shadow-md transition-all ${
                            isSelected
                              ? 'bg-amber-400 text-stone-950 border-amber-200 scale-105'
                              : 'bg-stone-950 text-amber-400 border-amber-500/40 group-hover:bg-amber-500 group-hover:text-stone-950 group-hover:border-amber-400'
                          }`}
                        >
                          {letterBadge}
                        </div>

                        <div className="flex-1 space-y-1 min-w-0">
                          {opt.badgeText && (
                            <span className="text-xs font-black text-amber-300 bg-amber-950/90 border border-amber-700/60 px-2.5 py-0.5 rounded-md inline-block">
                              {opt.badgeText}
                            </span>
                          )}
                          <p className="text-base sm:text-lg md:text-xl font-extrabold text-stone-100 leading-relaxed">
                            {opt.text}
                          </p>
                        </div>
                      </div>

                      {/* Right Side: Arrow Icon */}
                      <div className="flex items-center gap-2 shrink-0">
                        <ArrowRight className="w-5 h-5 text-stone-500 group-hover:text-amber-400 transition-transform group-hover:translate-x-1" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Footer Navigation Bar */}
        <div className="px-5 py-3 bg-stone-950 border-t border-stone-800 flex items-center justify-between text-xs text-stone-400 shrink-0">
          <div className="flex items-center gap-2">
            {(currentStep > 0 || showCheckpoint || showBirthdateStep) && !showResultAnimation && (
              <button
                onClick={handlePrevStep}
                className="flex items-center gap-1.5 bg-stone-800 hover:bg-stone-700 text-stone-200 px-3.5 py-1.5 rounded-xl border border-stone-700 transition font-bold text-xs"
              >
                <ArrowLeft className="w-4 h-4 text-amber-400" />
                <span>前へ戻る</span>
              </button>
            )}
          </div>

          {(currentStep > 0 || showBirthdateStep) && !showResultAnimation && (
            <button
              onClick={resetQuiz}
              className="flex items-center gap-1 text-stone-400 hover:text-stone-200 transition text-xs font-medium"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>最初からやり直す</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};



// ==========================================
// File: src/components/RelaxBGMPlayer.tsx
// ==========================================
import React, { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Music, Play, Pause, Sliders } from 'lucide-react';

type BGMPreset = 'cheerful' | 'breeze' | 'serene';

export const RelaxBGMPlayer: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.22);
  const [preset, setPreset] = useState<BGMPreset>('cheerful');
  const [showSettings, setShowSettings] = useState(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const masterGainRef = useRef<GainNode | null>(null);
  const timerRef = useRef<number | null>(null);

  // Stop background music synthesis
  const stopBGM = () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
      try {
        audioCtxRef.current.close();
      } catch (e) {
        console.error('AudioContext close error', e);
      }
      audioCtxRef.current = null;
    }
    setIsPlaying(false);
  };

  // Start cheerful & gentle background music synthesizer using Web Audio API
  const startBGM = () => {
    stopBGM();

    try {
      const AudioCtx =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const ctx = new AudioCtx();

      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      audioCtxRef.current = ctx;

      const masterGain = ctx.createGain();
      masterGain.gain.setValueAtTime(volume, ctx.currentTime);

      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1100, ctx.currentTime);

      filter.connect(masterGain);
      masterGain.connect(ctx.destination);
      masterGainRef.current = masterGain;

      // Gentle & Joyful Pentatonic Melody Notes (C4, D4, E4, G4, A4, C5, D5, E5, G5) in Hz
      const joyfulScale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25, 783.99];

      // Soft ambient warm drone undertone
      const droneOsc = ctx.createOscillator();
      const droneGain = ctx.createGain();
      droneOsc.type = 'sine';
      droneOsc.frequency.setValueAtTime(130.81, ctx.currentTime);
      droneGain.gain.setValueAtTime(0.02, ctx.currentTime);
      droneOsc.connect(droneGain);
      droneGain.connect(filter);
      droneOsc.start();

      if (preset === 'cheerful') {
        // Soft joyful marimba & bell arpeggio sequence
        let step = 0;
        const melodyPattern = [0, 2, 3, 5, 4, 2, 3, 7, 5, 3, 2, 4, 3, 5, 7, 8, 5, 3];

        timerRef.current = window.setInterval(() => {
          if (!audioCtxRef.current) return;
          const noteIndex = melodyPattern[step % melodyPattern.length];
          const freq = joyfulScale[noteIndex];

          const osc = ctx.createOscillator();
          const gain = ctx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, ctx.currentTime);

          const now = ctx.currentTime;
          gain.gain.setValueAtTime(0.001, now);
          gain.gain.linearRampToValueAtTime(0.09, now + 0.04);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.8);

          osc.connect(gain);
          gain.connect(filter);
          osc.start(now);
          osc.stop(now + 1.9);

          step++;
        }, 440); // Upbeat gentle relaxing tempo
      } else if (preset === 'breeze') {
        // Soothing nature breeze + gentle chord chimes
        let step = 0;
        const chimeNotes = [523.25, 659.25, 783.99, 880.0];

        timerRef.current = window.setInterval(() => {
          if (!audioCtxRef.current) return;
          const note = chimeNotes[step % chimeNotes.length];
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(note, ctx.currentTime);

          const now = ctx.currentTime;
          gain.gain.setValueAtTime(0, now);
          gain.gain.linearRampToValueAtTime(0.08, now + 0.4);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 3.0);

          osc.connect(gain);
          gain.connect(filter);
          osc.start(now);
          osc.stop(now + 3.2);

          step++;
        }, 1600);
      } else if (preset === 'serene') {
        // Serene warm ambient pad
        const baseFreqs = [130.81, 196.0, 261.63, 329.63];
        baseFreqs.forEach((freq) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, ctx.currentTime);

          gain.gain.setValueAtTime(0.04, ctx.currentTime);
          osc.connect(gain);
          gain.connect(filter);
          osc.start();
        });
      }

      setIsPlaying(true);
    } catch (err) {
      console.error('Audio BGM start error:', err);
    }
  };

  const togglePlay = () => {
    if (isPlaying) {
      stopBGM();
    } else {
      startBGM();
    }
  };

  // Adjust volume dynamically
  useEffect(() => {
    if (masterGainRef.current && audioCtxRef.current) {
      masterGainRef.current.gain.setValueAtTime(volume, audioCtxRef.current.currentTime);
    }
  }, [volume]);

  // Restart when preset changes
  useEffect(() => {
    if (isPlaying) {
      startBGM();
    }
  }, [preset]);

  // Auto-play from start on initial mount or first click anywhere
  useEffect(() => {
    const handleInitialUserGesture = () => {
      if (!isPlaying && !audioCtxRef.current) {
        startBGM();
      }
    };

    // Try auto start
    startBGM();

    window.addEventListener('click', handleInitialUserGesture, { once: true });
    window.addEventListener('keydown', handleInitialUserGesture, { once: true });

    return () => {
      window.removeEventListener('click', handleInitialUserGesture);
      window.removeEventListener('keydown', handleInitialUserGesture);
      stopBGM();
    };
  }, []);

  return (
    <div className="relative inline-block">
      <div className="flex items-center gap-1.5 bg-stone-950/90 border border-amber-500/40 rounded-xl px-2.5 py-1.5 shadow-md">
        <button
          onClick={togglePlay}
          className={`flex items-center gap-1.5 text-xs font-bold px-2 py-1 rounded-lg transition active:scale-95 ${
            isPlaying
              ? 'bg-amber-500 text-stone-950 shadow-sm animate-pulse'
              : 'bg-stone-800 hover:bg-stone-700 text-amber-300'
          }`}
          title={isPlaying ? 'BGMを停止' : '優しく楽しい和合BGMを再生'}
        >
          <Music className="w-3.5 h-3.5" />
          <span>{isPlaying ? 'BGM再生中' : 'BGMオン'}</span>
          {isPlaying ? <Pause className="w-3 h-3 ml-0.5" /> : <Play className="w-3 h-3 ml-0.5" />}
        </button>

        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-1 rounded-lg text-stone-400 hover:text-amber-300 hover:bg-stone-800 transition"
          title="BGM音量・曲種設定"
        >
          <Sliders className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Popover Settings Without Emojis */}
      {showSettings && (
        <div className="absolute right-0 mt-2 w-60 bg-stone-900 border border-amber-500/40 rounded-2xl p-3.5 shadow-2xl z-50 text-stone-100 space-y-3 animate-fade-in">
          <div className="flex items-center justify-between border-b border-stone-800 pb-2">
            <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
              <Music className="w-3.5 h-3.5" />
              <span>養生リラックスBGM設定</span>
            </span>
            <button
              onClick={() => setShowSettings(false)}
              className="text-stone-400 hover:text-stone-200 text-xs font-bold px-1"
            >
              ✕
            </button>
          </div>

          {/* Sound Presets without emojis */}
          <div className="space-y-1.5">
            <span className="text-[11px] text-stone-400 font-bold block">音色モード選択:</span>
            <div className="grid grid-cols-1 gap-1">
              <button
                onClick={() => setPreset('cheerful')}
                className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                  preset === 'cheerful'
                    ? 'bg-amber-950 text-amber-300 border border-amber-700 font-bold'
                    : 'bg-stone-800 hover:bg-stone-750 text-stone-300'
                }`}
              >
                優しく明るい和合メロディ
              </button>
              <button
                onClick={() => setPreset('breeze')}
                className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                  preset === 'breeze'
                    ? 'bg-amber-950 text-amber-300 border border-amber-700 font-bold'
                    : 'bg-stone-800 hover:bg-stone-750 text-stone-300'
                }`}
              >
                清流と風鈴の気功ソウヒ
              </button>
              <button
                onClick={() => setPreset('serene')}
                className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                  preset === 'serene'
                    ? 'bg-amber-950 text-amber-300 border border-amber-700 font-bold'
                    : 'bg-stone-800 hover:bg-stone-750 text-stone-300'
                }`}
              >
                深遠な瞑想ドローン音
              </button>
            </div>
          </div>

          {/* Volume Control */}
          <div className="space-y-1 pt-1 border-t border-stone-800">
            <div className="flex items-center justify-between text-[11px] text-stone-400">
              <span className="flex items-center gap-1">
                {volume === 0 ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                <span>音量調整</span>
              </span>
              <span>{Math.round(volume * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
              className="w-full accent-amber-500 bg-stone-800 h-1.5 rounded-lg cursor-pointer"
            />
          </div>
        </div>
      )}
    </div>
  );
};



// ==========================================
// File: src/components/ShanghanProfile.tsx
// ==========================================
import React, { useState, useEffect } from 'react';
import { ShanghanType } from '../types';
import { SHANGHAN_PROFILES } from '../data/orientalData';
import { BookOpen, ShieldAlert, HeartPulse, Utensils, Activity, Sparkles, MapPin, Volume2, VolumeX, Heart, MessageCircle } from 'lucide-react';

interface ShanghanProfileCardProps {
 userShanghanType: ShanghanType;
}

export const ShanghanProfileCard: React.FC<ShanghanProfileCardProps> = ({
 userShanghanType,
}) => {
 const [activeTabType, setActiveTabType] = useState<ShanghanType>(userShanghanType);
 const [isSpeaking, setIsSpeaking] = useState(false);

 useEffect(() => {
    setActiveTabType(userShanghanType);
  }, [userShanghanType]);

  const activeProfile = SHANGHAN_PROFILES[activeTabType] || SHANGHAN_PROFILES.taiyin;
 const isUserType = activeTabType === userShanghanType;

 const allTypes: ShanghanType[] = ['taiyang', 'shaoyang', 'yangming', 'taiyin', 'shaoyin', 'jueyin'];

 // Speech synthesis read aloud for the full diagnosis result & encouragement
 const handleToggleSpeakResult = () => {
 if (!('speechSynthesis' in window)) {
 alert('お使いのブラウザは音声読み上げに対応していません。');
 return;
 }

 if (isSpeaking) {
 window.speechSynthesis.cancel();
 setIsSpeaking(false);
 return;
 }

 window.speechSynthesis.cancel();

 const textToSpeak = `
 ${activeProfile.name}。 ${activeProfile.tagline}。
 解説。 ${activeProfile.description}。
 食養生のアドバイス。 ${activeProfile.dietAdvice.join('。 ')}。
 運動と経絡ケア。 ${activeProfile.exerciseAdvice.join('。 ')}。
 養生からのメッセージ。 ${activeProfile.encouragement || ''}
 `;

 const utterance = new SpeechSynthesisUtterance(textToSpeak);
 utterance.lang = 'ja-JP';
 utterance.rate = 0.95;
 utterance.pitch = 1.0;

 utterance.onend = () => setIsSpeaking(false);
 utterance.onerror = () => setIsSpeaking(false);

 setIsSpeaking(true);
 window.speechSynthesis.speak(utterance);
 };

 return (
 <div className="bg-stone-900/90 border border-stone-800 rounded-3xl p-5 sm:p-7 text-stone-100 shadow-xl space-y-6">
 {/* Title & Speech Aloud Header */}
 <div className="flex items-center justify-between flex-wrap gap-3">
 <div className="flex items-center gap-3">
 <div className="w-12 h-12 rounded-2xl bg-amber-950 border border-amber-500/40 flex items-center justify-center text-amber-400 text-xl font-serif shadow-md">
 傷
 </div>
 <div>
 <h3 className="font-extrabold text-lg sm:text-xl text-stone-100 flex items-center gap-2">
 「傷寒論」体質診断 ＆ 養生処方箋
 </h3>
 <p className="text-xs sm:text-sm text-stone-400">
 中国古代医典『傷寒論』に基づく個別の食養生・経絡運動レシピ
 </p>
 </div>
 </div>

 <div className="flex items-center gap-2 flex-wrap">
 {/* TTS Read Aloud Button */}
 <button
 onClick={handleToggleSpeakResult}
 className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm font-extrabold transition flex items-center gap-2 shadow-md active:scale-95 ${
 isSpeaking
 ? 'bg-amber-500 text-stone-950 animate-pulse'
 : 'bg-stone-800 hover:bg-stone-750 text-amber-300 border border-amber-500/40'
 }`}
 >
 {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-amber-400" />}
 <span>{isSpeaking ? '音声停止' : ' 結果・アドバイスを音声で聴く'}</span>
 </button>

 <span className="text-xs bg-amber-950/80 border border-amber-800/60 text-amber-300 font-bold px-3 py-1.5 rounded-xl">
 薬不使用宣言 (無薬食養生)
 </span>
 </div>
 </div>

 {/* Six Meridian Type Tabs */}
 <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-stone-800">
 {allTypes.map((sType) => {
 const prof = SHANGHAN_PROFILES[sType];
 const isSelected = activeTabType === sType;
 const isMy = sType === userShanghanType;

 return (
 <button
 key={sType}
 onClick={() => setActiveTabType(sType)}
 className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 ${
 isSelected
 ? 'bg-gradient-to-r from-amber-600 to-amber-500 text-stone-950 shadow-md scale-105'
 : 'bg-stone-800/80 hover:bg-stone-750 text-stone-300 border border-stone-700/60'
 }`}
 >
 <span>{prof.kanjiName}</span>
 {isMy && (
 <span className="text-[10px] bg-stone-950 text-amber-300 px-1.5 py-0.2 rounded font-normal">
 あなた
 </span>
 )}
 </button>
 );
 })}
 </div>

 {/* Profile Detail Content */}
 <div className="space-y-6">
 {/* Header Hero Banner for Constitution */}
 <div className="bg-gradient-to-r from-amber-950/40 via-stone-800/60 to-stone-900 border border-amber-500/30 rounded-2xl p-5 relative overflow-hidden">
 <div className="flex items-start justify-between flex-wrap gap-3">
 <div className="space-y-1">
 <div className="flex items-center gap-2">
 <span className="text-xs font-bold text-amber-400 bg-amber-950 px-2.5 py-0.5 rounded-full border border-amber-700/50">
 {activeProfile.kanjiName}
 </span>
 <span className="text-xs text-stone-400 font-medium">
 パターン: {activeProfile.yinYangType}
 </span>
 </div>
 <h4 className="text-lg sm:text-xl font-bold text-stone-100 mt-1">
 {activeProfile.name}
 </h4>
 <p className="text-xs sm:text-sm text-amber-200/90 font-medium pt-1">
 “{activeProfile.tagline}”
 </p>
 </div>

 {isUserType && (
 <div className="bg-amber-500/20 border border-amber-400/40 rounded-xl px-3 py-1.5 flex items-center gap-1.5 text-xs text-amber-300 font-bold shrink-0">
 <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
 <span>診断結果適用中</span>
 </div>
 )}
 </div>

 <p className="text-sm sm:text-base text-stone-200 leading-relaxed mt-4 pt-3 border-t border-stone-700/50 font-medium">
 {activeProfile.description}
 </p>
 </div>

 {/* Encouragement Card (励ましの言葉) */}
 {activeProfile.encouragement && (
 <div className="bg-gradient-to-r from-rose-950/40 via-amber-950/30 to-stone-900 border border-rose-500/40 rounded-2xl p-4.5 sm:p-5 relative overflow-hidden shadow-lg space-y-2">
 <div className="flex items-center gap-2 text-rose-300 font-extrabold text-sm sm:text-base">
 <Heart className="w-5 h-5 text-rose-400 fill-rose-400/20 animate-pulse" />
 <span>養生からの温かい励ましのメッセージ</span>
 </div>
 <p className="text-sm sm:text-base text-stone-100 font-medium leading-relaxed bg-stone-950/50 p-3.5 rounded-xl border border-stone-800">
 “{activeProfile.encouragement}”
 </p>
 </div>
 )}

 {/* Symptoms Grid */}
 <div className="space-y-2">
 <h5 className="text-xs font-bold text-stone-300 flex items-center gap-1.5">
 <HeartPulse className="w-4 h-4 text-red-400" />
 <span>この体質で見られやすいSOSサイン</span>
 </h5>
 <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
 {activeProfile.keySymptoms.map((sym, idx) => (
 <div
 key={idx}
 className="bg-stone-800/50 border border-stone-700/50 rounded-xl p-2.5 text-xs text-stone-200 flex items-center gap-2"
 >
 <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
 <span>{sym}</span>
 </div>
 ))}
 </div>
 </div>

 {/* Diet & Exercise Action Plans */}
 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
 {/* Diet Plan */}
 <div className="bg-stone-800/60 border border-emerald-900/50 rounded-2xl p-4 space-y-3">
 <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
 <Utensils className="w-4 h-4" />
 <span>食養生アドバイス（薬に頼らない）</span>
 </div>
 <ul className="space-y-2 text-xs text-stone-300">
 {activeProfile.dietAdvice.map((adv, idx) => (
 <li key={idx} className="flex items-start gap-2 bg-stone-900/60 p-2.5 rounded-xl border border-stone-800">
 <span className="text-emerald-400 font-bold"></span>
 <span className="leading-relaxed">{adv}</span>
 </li>
 ))}
 </ul>

 {/* Recommended Ingredients */}
 <div className="pt-2">
 <span className="text-[11px] text-stone-400 font-bold block mb-1.5">
 おすすめ養生食材・スープの具材:
 </span>
 <div className="flex flex-wrap gap-1.5">
 {activeProfile.recommendedIngredients.map((ing, idx) => (
 <span
 key={idx}
 className="text-xs bg-emerald-950/80 text-emerald-200 border border-emerald-800/60 px-2.5 py-1 rounded-lg font-bold flex items-center gap-1"
 >
 <span></span>
 <span>{ing}</span>
 </span>
 ))}
 </div>
 </div>
 </div>

 {/* Exercise & Stretch Plan */}
 <div className="bg-stone-800/60 border border-teal-900/50 rounded-2xl p-4 space-y-3">
 <div className="flex items-center gap-2 text-teal-400 font-bold text-sm">
 <Activity className="w-4 h-4" />
 <span>運動方式＆経絡ケア（八段錦・気功・体操）</span>
 </div>
 <ul className="space-y-2 text-xs text-stone-300">
 {activeProfile.exerciseAdvice.map((adv, idx) => (
 <li key={idx} className="flex items-start gap-2 bg-stone-900/60 p-2.5 rounded-xl border border-stone-800">
 <span className="text-teal-400 font-bold"></span>
 <span className="leading-relaxed">{adv}</span>
 </li>
 ))}
 </ul>

 {/* Recommended Stretch */}
 <div className="pt-2">
 <span className="text-[11px] text-stone-400 font-bold block mb-1.5">
 おすすめ経絡ストレッチ＆気功:
 </span>
 <div className="flex flex-wrap gap-1.5">
 {activeProfile.recommendedStretch.map((st, idx) => (
 <span
 key={idx}
 className="text-xs bg-teal-950/80 text-teal-200 border border-teal-800/60 px-2.5 py-1 rounded-lg font-bold flex items-center gap-1"
 >
 <span>️</span>
 <span>{st}</span>
 </span>
 ))}
 </div>
 </div>
 </div>
 </div>

 {/* Acupoints Cards */}
 <div className="space-y-3">
 <h5 className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
 <MapPin className="w-4 h-4 text-amber-400" />
 <span>【特選】セルフケアツボ押しマップ</span>
 </h5>
 <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
 {activeProfile.acupoints.map((acu, idx) => (
 <div
 key={idx}
 className="bg-stone-800/80 border border-stone-700/60 rounded-xl p-3.5 space-y-1 text-xs"
 >
 <div className="flex items-center justify-between">
 <span className="font-bold text-amber-300 text-sm">
 {acu.name}
 </span>
 <span className="text-[10px] text-stone-400 bg-stone-900 px-2 py-0.5 rounded-md">
 ツボ
 </span>
 </div>
 <p className="text-stone-300 font-medium">
 場所: {acu.location}
 </p>
 <p className="text-stone-400">
 効能: {acu.effect}
 </p>
 </div>
 ))}
 </div>
 </div>
 </div>
 </div>
 );
};



// ==========================================
// File: src/components/TcmGlossaryModal.tsx
// ==========================================
import React from 'react';
import { BookOpen, HelpCircle, Sparkles, X, Lightbulb } from 'lucide-react';

export interface GlossaryTerm {
  term: string;
  reading: string;
  summary: string;
  explanation: string;
  advice: string;
  category: 'shanghan' | 'five_elements' | 'lifestyle' | 'anatomy';
}

export const TCM_GLOSSARY: Record<string, GlossaryTerm> = {
  傷寒論: {
    term: '傷寒論 (しょうかんろん)',
    reading: 'しょうかんろん',
    summary: '約1800年前に編纂された東洋医学最古の臨床・体質医学の聖典',
    explanation:
      '寒気や冷え（外邪）が体内に侵入した際、体がどのように反応し、病が深まっていくかを『六経（ろっけい）』という6段階の体質・病態パターン（太陽・少陽・陽明・太陰・少陰・厥陰）に分類して解説した臨床書です。',
    advice: '西洋医学が「病気そのもの」を攻撃するのに対し、『傷寒論』は「本人の冷え・胃腸・自律神経の抵抗力」を整えて自然治癒力を引き出します。',
    category: 'shanghan',
  },
  無薬食養生: {
    term: '無薬食養生 (むやくしょくようじょう)',
    reading: 'むやくしょくようじょう',
    summary: '薬に頼らず、毎日の食材・温活・ツボ刺激で不調を根本から整える方法',
    explanation:
      '「医食同源」の思想に基づき、身近な季節の野菜や薬味（生姜、葱、シナモン、大根等）とツボ押し運動を組み合わせて体のアンバランスを補う手法です。副作用がなく、日々の予防医療に最適です。',
    advice: '冷えを感じたら葛湯や生姜湯を飲むなど、薬を飲む前の「初期アプローチ」として生涯役に立ちます。',
    category: 'lifestyle',
  },
  陰虚: {
    term: '陰虚 (いんきょ)',
    reading: 'いんきょ',
    summary: '体内の「うるおい（体液・血）」が不足して、から咳や手足のほてりが起きる状態',
    explanation:
      '車で例えると「冷却水（クーラー液）」が不足した状態です。エンジンが熱を持ちやすくなり、夕方になると顔が火照ったり、喉が乾いたり、ドライアイや不眠になりやすくなります。',
    advice: 'クコの実、豆腐、山芋、はとむぎなどの「陰（うるおい）」を補う食材を摂り、夜更かしを控えましょう。',
    category: 'five_elements',
  },
  陽虚: {
    term: '陽虚 (ようきょ)',
    reading: 'ようきょ',
    summary: '体内の「温めるエネルギー（ヒーター）」が不足して、強い冷えを感じる状態',
    explanation:
      'ボイラーの火が弱まり、手足やお腹が常に冷えて、温かい食べ物や飲み物を欲する状態です。下痢をしやすく、おしっこの回数が増える特徴があります。',
    advice: '生姜、ニラ、シナモン、黒糖などの温熱食材を選び、お腹や足首を絶対に冷やさないようにしましょう。',
    category: 'five_elements',
  },
  気滞: {
    term: '気滞 (きたい)',
    reading: 'きたい',
    summary: 'ストレスや緊張によって「気（エネルギー）」の巡りが滞っている状態',
    explanation:
      '自律神経が緊張し、気（エネルギー）の交通渋滞が起きている状態です。お腹や肋骨あたりが張ったり、ため息が増えたり、イライラや気分の落ち込みが交互に現れます。',
    advice: 'シトラス・柑橘類の香り（レモン、ゆず）や三つ葉、セロリなど「香りの良い食材」で気の滞りをスッと通しましょう。',
    category: 'five_elements',
  },
  水毒: {
    term: '水毒・水滞 (すいどく・すいたい)',
    reading: 'すいどく・すいたい',
    summary: '冷えや冷たい飲み物の摂りすぎで、胃腸や組織に不要な水分が溜まった状態',
    explanation:
      '冷たい飲み物やビール、氷水を日常的に摂ることで胃腸の熱が奪われ、水分代謝が低下。頭重感、むくみ、ぽちゃぽちゃとした胃の音がするのが特徴です。',
    advice: '冷たい水分のガブ飲みを控え、常温や温かいお茶を選び、足三里のツボ押しで胃腸を温めましょう。',
    category: 'lifestyle',
  },
  頭寒足熱: {
    term: '頭寒足熱 (ずかんそくねつ)',
    reading: 'ずかんそくねつ',
    summary: '頭を涼やかに保ち、足元やお腹を温める健康の黄金バランス',
    explanation:
      '東洋医学では、温かい気は上に昇りやすく、冷たい気は下に沈みやすいとされます。足元が冷えると頭に熱が上り（のぼせ・イライラ）、上下の循環が壊れます。',
    advice: '足湯やレッグウォーマーで足元を温め、頭部は涼しい状態に保つことで自律神経が深く安定します。',
    category: 'anatomy',
  },
  八段錦: {
    term: '八段錦 (はちだんきん)',
    reading: 'はちだんきん',
    summary: '中国で800年以上親しまれている、8つの動作からなる気功・健康ストレッチ',
    explanation:
      '激しい運動ではなく、呼吸とゆったりした動作を合わせて全身の経絡（気の通り道）を伸長・刺激する気功エクササイズです。誰でも無理なく自律神経を整えられます。',
    advice: '朝起きた時や夜のリラックスタイムに、両手を上に伸ばして胸を開くだけでも内臓の働きが活発化します。',
    category: 'lifestyle',
  },
  経絡: {
    term: '経絡 (けいらく)',
    reading: 'けいらく',
    summary: '全身の臓器と体表を結ぶ「気・血・水」が流れるエネルギーのネットワーク',
    explanation:
      '線路のように全身を巡る14本の主要なルートです。経絡の上に存在する重要な「駅」が『ツボ（経穴）』であり、ツボを刺激することで対応する臓器の働きが活性化します。',
    advice: 'ツボを押すと心地よい響きを感じるのは、経絡を通じて遠くの臓器に刺激が届いている証拠です。',
    category: 'anatomy',
  },
  衛気: {
    term: '衛気 (えき)',
    reading: 'えき',
    summary: '皮膚や粘膜の表面を守る、免疫とバリアの防衛エネルギー',
    explanation:
      '体のバリアシールドのような存在です。衛気が強いとウイルスや冷気（風邪の邪気）を跳ね返せますが、疲労やストレスで衰えると肌荒れや寒気を感じやすくなります。',
    advice: '乾布摩擦やしっかりした呼吸法、温かいスープで肺と脾胃を補うことが衛気の強化につながります。',
    category: 'shanghan',
  },
};

interface TcmTermProps {
  termKey: string;
  children?: React.ReactNode;
}

export const TcmTerm: React.FC<TcmTermProps> = ({ termKey, children }) => {
  const [showModal, setShowModal] = React.useState(false);
  const glossaryItem = TCM_GLOSSARY[termKey];

  if (!glossaryItem) {
    return <span>{children || termKey}</span>;
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setShowModal(true)}
        className="inline-flex items-center gap-0.5 text-amber-300 hover:text-amber-200 border-b border-dashed border-amber-400 font-bold px-0.5 py-0 rounded hover:bg-amber-950/60 transition cursor-pointer"
        title={`『${glossaryItem.term}』の簡単解説を見る`}
      >
        <span>{children || termKey}</span>
        <HelpCircle className="w-3 h-3 text-amber-400 inline shrink-0" />
      </button>

      {showModal && (
        <div className="fixed inset-[#0] z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-stone-900 border-2 border-amber-500/60 rounded-3xl max-w-lg w-full p-5 sm:p-6 text-stone-100 shadow-2xl space-y-4 relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 p-2 rounded-full bg-stone-800 text-stone-400 hover:text-stone-100 hover:bg-stone-700 transition"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2.5 text-amber-400">
              <BookOpen className="w-6 h-6" />
              <span className="text-xs font-bold bg-amber-950 border border-amber-700 px-2.5 py-1 rounded-lg">
                東洋医学・かんたん用語辞典
              </span>
            </div>

            <div className="space-y-1">
              <h3 className="text-xl font-black text-amber-300">{glossaryItem.term}</h3>
              <p className="text-xs text-amber-200/80 font-bold flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" />
                <span>{glossaryItem.summary}</span>
              </p>
            </div>

            <div className="bg-stone-950/90 border border-stone-800 rounded-2xl p-4 text-sm text-stone-200 leading-relaxed space-y-2">
              <p className="font-medium">{glossaryItem.explanation}</p>
            </div>

            <div className="bg-amber-950/40 border border-amber-600/40 rounded-2xl p-4 text-xs sm:text-sm text-amber-100 space-y-1">
              <span className="font-black text-amber-300 flex items-center gap-1">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                <span>養生ワンポイントアドバイス</span>
              </span>
              <p className="leading-relaxed font-medium">{glossaryItem.advice}</p>
            </div>

            <div className="pt-2 text-center">
              <button
                onClick={() => setShowModal(false)}
                className="w-full bg-amber-500 hover:bg-amber-400 text-stone-950 font-black py-2.5 rounded-xl transition text-sm shadow-md"
              >
                理解しました（閉じる）
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};



// ==========================================
// File: src/components/YouTubeVideoSection.tsx
// ==========================================
import React, { useState } from 'react';
import { YouTubeVideo, ElementType } from '../types';
import { YOUTUBE_VIDEOS, FIVE_ELEMENT_INFO } from '../data/orientalData';
import { Play, Film, X, Search, Filter, Sparkles, Clock, Tag } from 'lucide-react';

export const YouTubeVideoSection: React.FC = () => {
 const [selectedCategory, setSelectedCategory] = useState<string>('all');
 const [selectedElement, setSelectedElement] = useState<string>('all');
 const [activeVideoModal, setActiveVideoModal] = useState<YouTubeVideo | null>(null);
 const [searchQuery, setSearchQuery] = useState('');

 const filteredVideos = YOUTUBE_VIDEOS.filter((video) => {
 const matchCat = selectedCategory === 'all' || video.category === selectedCategory;
 const matchEl = selectedElement === 'all' || video.targetElement === selectedElement;
 const matchSearch =
 searchQuery === '' ||
 video.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
 video.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
 video.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));

 return matchCat && matchEl && matchSearch;
 });

 return (
 <div className="bg-stone-900/90 border border-stone-800 rounded-3xl p-5 sm:p-6 text-stone-100 shadow-xl space-y-6">
 {/* Title */}
 <div className="flex items-center justify-between flex-wrap gap-2">
 <div className="flex items-center gap-2.5">
 <div className="w-10 h-10 rounded-2xl bg-rose-950 border border-rose-500/40 flex items-center justify-center text-rose-400 text-lg">
 ▶
 </div>
 <div>
 <h3 className="font-bold text-base sm:text-lg text-stone-100 flex items-center gap-2">
 YouTube 養生動画＆運動・薬膳レシピガイド
 </h3>
 <p className="text-xs text-stone-400">
 毎日飽きずに続けられる八段錦・経絡ストレッチ・ツボ押し＆温活スープ料理動画
 </p>
 </div>
 </div>

 <span className="text-xs bg-stone-800 text-amber-300 border border-amber-500/30 font-medium px-3 py-1 rounded-xl">
 動画視聴で +50 XP 習慣
 </span>
 </div>

 {/* Filter & Search Bar */}
 <div className="space-y-3">
 <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
 {/* Search Input */}
 <div className="relative flex-1">
 <Search className="w-4 h-4 text-stone-400 absolute left-3 top-1/2 -translate-y-1/2" />
 <input
 type="text"
 placeholder="動画タイトルやキーワード（例：生姜, ツボ, 八段錦）で検索..."
 value={searchQuery}
 onChange={(e) => setSearchQuery(e.target.value)}
 className="w-full bg-stone-800/80 border border-stone-700 rounded-xl pl-9 pr-4 py-2 text-xs text-stone-100 placeholder-stone-500 focus:outline-none focus:border-amber-500"
 />
 </div>

 {/* Category Tabs */}
 <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
 {[
 { id: 'all', label: 'すべて' },
 { id: 'qigong', label: ' 八段錦・気功' },
 { id: 'exercise', label: '️ 経絡ストレッチ' },
 { id: 'acupoint', label: ' ツボ押し' },
 { id: 'recipe', label: ' 薬膳食養生' },
 ].map((cat) => (
 <button
 key={cat.id}
 onClick={() => setSelectedCategory(cat.id)}
 className={`px-3 py-1.5 rounded-xl text-xs font-bold transition shrink-0 ${
 selectedCategory === cat.id
 ? 'bg-amber-500 text-stone-950 shadow'
 : 'bg-stone-800 hover:bg-stone-750 text-stone-300 border border-stone-700'
 }`}
 >
 {cat.label}
 </button>
 ))}
 </div>
 </div>

 {/* Five Elements Filter Row */}
 <div className="flex items-center gap-2 overflow-x-auto text-xs">
 <span className="text-stone-400 font-bold text-[11px] shrink-0">五行で絞り込み:</span>
 <button
 onClick={() => setSelectedElement('all')}
 className={`px-2.5 py-1 rounded-lg transition shrink-0 ${
 selectedElement === 'all'
 ? 'bg-stone-200 text-stone-900 font-bold'
 : 'bg-stone-800 text-stone-400 hover:text-stone-200'
 }`}
 >
 全属性
 </button>
 {(['wood', 'fire', 'earth', 'metal', 'water'] as ElementType[]).map((el) => {
 const info = FIVE_ELEMENT_INFO[el];
 const isSel = selectedElement === el;
 return (
 <button
 key={el}
 onClick={() => setSelectedElement(el)}
 className={`px-2.5 py-1 rounded-lg border font-bold transition shrink-0 flex items-center gap-1 ${
 isSel ? 'bg-amber-500 text-stone-950 border-amber-400' : 'bg-stone-800/80 text-stone-300 border-stone-700'
 }`}
 >
 <span className="w-2 h-2 rounded-full" style={{ backgroundColor: info.color }} />
 <span>{info.kanji} ({info.organ})</span>
 </button>
 );
 })}
 </div>
 </div>

 {/* Video Cards Grid */}
 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
 {filteredVideos.map((video) => {
 const elInfo = FIVE_ELEMENT_INFO[video.targetElement];

 return (
 <div
 key={video.id}
 className="bg-stone-800/60 border border-stone-700/60 rounded-2xl overflow-hidden hover:border-amber-500/50 transition duration-200 group flex flex-col"
 >
 {/* Thumbnail Container */}
 <div
 onClick={() => setActiveVideoModal(video)}
 className="relative aspect-video bg-stone-950 cursor-pointer overflow-hidden group-hover:opacity-90 transition"
 >
 <img
 src={video.thumbnailUrl}
 alt={video.title}
 className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
 />
 <div className="absolute inset-0 bg-black/30 group-hover:bg-black/10 transition flex items-center justify-center">
 <div className="w-12 h-12 rounded-full bg-amber-500/90 text-stone-950 flex items-center justify-center shadow-lg group-hover:scale-110 transition">
 <Play className="w-5 h-5 fill-stone-950 ml-0.5" />
 </div>
 </div>

 <span className="absolute bottom-2 right-2 bg-black/80 backdrop-blur-sm text-stone-200 text-[10px] font-mono px-2 py-0.5 rounded-md flex items-center gap-1">
 <Clock className="w-3 h-3" /> {video.duration}
 </span>

 <span
 className="absolute top-2 left-2 text-[10px] font-bold px-2 py-0.5 rounded-md border text-stone-950"
 style={{ backgroundColor: elInfo.color, borderColor: elInfo.color }}
 >
 {elInfo.kanji}（{elInfo.organ}）
 </span>
 </div>

 {/* Card Body */}
 <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
 <div className="space-y-1.5">
 <h4
 onClick={() => setActiveVideoModal(video)}
 className="font-bold text-sm text-stone-100 hover:text-amber-300 cursor-pointer line-clamp-2 leading-snug"
 >
 {video.title}
 </h4>
 <p className="text-xs text-stone-400 line-clamp-2 leading-relaxed">
 {video.description}
 </p>
 </div>

 {/* Tags & Action */}
 <div className="pt-2 border-t border-stone-700/40 flex items-center justify-between gap-2">
 <div className="flex flex-wrap gap-1">
 {video.tags.slice(0, 2).map((tag, idx) => (
 <span key={idx} className="text-[10px] bg-stone-900 text-stone-400 px-2 py-0.5 rounded">
 #{tag}
 </span>
 ))}
 </div>

 <button
 onClick={() => setActiveVideoModal(video)}
 className="text-xs text-amber-400 font-bold hover:underline flex items-center gap-1 shrink-0"
 >
 再生する
 </button>
 </div>
 </div>
 </div>
 );
 })}
 </div>

 {filteredVideos.length === 0 && (
 <div className="p-12 text-center text-stone-400 bg-stone-800/40 rounded-2xl border border-stone-700/40">
 <Film className="w-8 h-8 mx-auto mb-2 text-stone-500" />
 <p className="text-sm font-bold">該当する養生動画が見つかりませんでした</p>
 <p className="text-xs text-stone-500 mt-1">検索キーワードを変更するか全属性タブでお試しください。</p>
 </div>
 )}

 {/* YouTube Embedded Player Modal */}
 {activeVideoModal && (
 <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
 <div className="relative w-full max-w-3xl bg-stone-900 border border-amber-500/30 rounded-3xl overflow-hidden shadow-2xl flex flex-col">
 {/* Modal Header */}
 <div className="px-5 py-3 bg-stone-950 border-b border-stone-800 flex items-center justify-between">
 <div className="flex items-center gap-2">
 <Play className="w-4 h-4 text-amber-400 fill-amber-400" />
 <h4 className="font-bold text-amber-300 text-xs sm:text-sm line-clamp-1">
 {activeVideoModal.title}
 </h4>
 </div>
 <button
 onClick={() => setActiveVideoModal(null)}
 className="p-1.5 rounded-xl bg-stone-800 hover:bg-stone-700 text-stone-400 hover:text-stone-200 transition"
 >
 <X className="w-5 h-5" />
 </button>
 </div>

 {/* Video Iframe Container */}
 <div className="relative aspect-video bg-black">
 <iframe
 src={`https://www.youtube.com/embed/${activeVideoModal.youtubeId}?autoplay=1`}
 title={activeVideoModal.title}
 className="w-full h-full border-0"
 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
 allowFullScreen
 />
 </div>

 {/* Modal Footer Info */}
 <div className="p-5 space-y-2 bg-stone-950/80">
 <p className="text-xs text-stone-300 leading-relaxed">
 {activeVideoModal.description}
 </p>
 <div className="flex flex-wrap gap-1.5 pt-1">
 {activeVideoModal.tags.map((tag, idx) => (
 <span
 key={idx}
 className="text-[10px] bg-stone-800 text-amber-300/80 px-2 py-0.5 rounded-md border border-stone-700"
 >
 #{tag}
 </span>
 ))}
 </div>
 </div>
 </div>
 </div>
 )}
 </div>
 );
};



// ==========================================
// File: src/data/orientalData.ts
// ==========================================
import {
 QuizQuestion,
 ShanghanProfile,
 ShanghanType,
 YouTubeVideo,
 DailyQuest,
 Badge,
 OrganClockSlot,
 ElementType,
} from '../types';

export const FIVE_ELEMENT_INFO: Record<
 ElementType,
 {
 kanji: string;
 name: string;
 organ: string;
 viscera: string;
 season: string;
 color: string;
 bgGradient: string;
 textColor: string;
 borderColor: string;
 flavor: string;
 emotion: string;
 sense: string;
 desc: string;
 goodFoods: string[];
 goodExercises: string[];
 }
> = {
 wood: {
 kanji: '木',
 name: '木 (もく)',
 organ: '肝・胆',
 viscera: '自律神経・目・筋',
 season: '春 (芽吹き)',
 color: '#10B981', // Emerald
 bgGradient: 'from-emerald-500/20 to-teal-500/10',
 textColor: 'text-emerald-700 dark:text-emerald-300',
 borderColor: 'border-emerald-500',
 flavor: '酸味 (すっぱい)',
 emotion: '怒り・伸びやかさ',
 sense: '目',
 desc: '「肝は将軍の官」。気を巡らせ、自律神経と感情を伸びやかに保つエネルギー。春に芽吹く木のように滞りを嫌います。',
 goodFoods: ['シトラス・柑橘類', '緑黄色野菜', '酢の物', '緑茶', 'しそ・香草'],
 goodExercises: ['脇腹の横曲げストレッチ', '深呼吸・気功散歩', '太衝（たいしょう）のツボ押し', '目もとの温熱ケア'],
 },
 fire: {
 kanji: '火',
 name: '火 (か)',
 organ: '心・小腸',
 viscera: '循環器・精神・舌',
 season: '夏 (盛夏)',
 color: '#EF4444', // Red
 bgGradient: 'from-red-500/20 to-rose-500/10',
 textColor: 'text-red-700 dark:text-red-300',
 borderColor: 'border-red-500',
 flavor: '苦味 (にがい)',
 emotion: '喜び・昂ぶり',
 sense: '舌',
 desc: '「心は君主の官」。全身に血を巡らせ、神（こころ）を宿す情熱の火。巡りが過剰になると不眠やのぼせが起こります。',
 goodFoods: ['ゴーヤ・苦瓜', 'ジャスミン茶', 'トマト', '小豆', 'はとむぎ'],
 goodExercises: ['胸を開くストレッチ', '神門（しんもん）のツbo押し', 'ゆったりした太極拳', '瞑想・マインドフルネス'],
 },
 earth: {
 kanji: '土',
 name: '土 (ど)',
 organ: '脾・胃',
 viscera: '消化吸収・筋肉・口',
 season: '土用 (季節の変わり目)',
 color: '#F59E0B', // Amber
 bgGradient: 'from-amber-500/20 to-yellow-500/10',
 textColor: 'text-amber-700 dark:text-amber-300',
 borderColor: 'border-amber-500',
 flavor: '甘味 (ほのかな甘み)',
 emotion: '思い煩い・安心感',
 sense: '口・くちびる',
 desc: '「脾は後天の本」。食べたものから『気・血』を生み出す中央ボイラー。冷えや冷たい飲み物でボイラーの火が弱まります。',
 goodFoods: ['かぼちゃ・さつまいも', '大豆・豆腐', '温かいお粥', 'みそ汁', 'なつめ・山芋'],
 goodExercises: ['足三里（あしさんり）のツボ押し', 'お腹を温める手当てマッサージ', '食後の軽やかなウォーキング'],
 },
 metal: {
 kanji: '金',
 name: '金 (ごん)',
 organ: '肺・大腸',
 viscera: '呼吸・皮膚・鼻・免疫',
 season: '秋 (実りと乾燥)',
 color: '#6B7280', // Slate / Silver
 bgGradient: 'from-slate-400/20 to-zinc-500/10',
 textColor: 'text-slate-700 dark:text-slate-300',
 borderColor: 'border-slate-400',
 flavor: '辛味 (からい・ピリッ)',
 emotion: '悲しみ・清廉さ',
 sense: '鼻・バリア皮膚',
 desc: '「肺は相傅の官」。呼吸によって天の気を巡らし、皮膚の防衛バリア（衛気）を作る金属の盾。乾燥を何より嫌います。',
 goodFoods: ['白きくらげ', '大根・レンコン', '梨（ナシ）', '豆腐・白い胡麻', '生姜湯'],
 goodExercises: ['胸郭を広げる呼吸エクササイズ', '合谷（ごうこく）のツボ押し', '背中の乾布摩擦・軽い体操'],
 },
 water: {
 kanji: '水',
 name: '水 (すい)',
 organ: '腎・膀胱',
 viscera: '生命力・骨・耳・エイジング',
 season: '冬 (静寂と蓄え)',
 color: '#3B82F6', // Blue
 bgGradient: 'from-blue-500/20 to-indigo-500/10',
 textColor: 'text-blue-700 dark:text-blue-300',
 borderColor: 'border-blue-500',
 flavor: '鹹味 (塩け・海のエキス)',
 emotion: '恐れ・意志の力',
 sense: '耳・髪・骨',
 desc: '「腎は先天の本」。生まれ持った生命エネルギー（精）を蓄える静かな水。冷えは腎の精を消耗させる最大の敵です。',
 goodFoods: ['黒胡麻・黒豆', 'ひじき・海藻', 'くるみ', '山芋・クコの実', '出汁スープ'],
 goodExercises: ['湧泉（ゆうせん）のツボ押し・青竹踏み', '腰まわりを温める股関節ストレッチ', '足首まわし'],
 },
};

export const SHANGHAN_PROFILES: Record<ShanghanType, ShanghanProfile> = {
 taiyang: {
 id: 'taiyang',
 name: '太陽病タイプ (風寒・表寒型)',
 kanjiName: '太陽病型',
 tagline: '風や冷気に敏感！バリア機能を高めて寒気を跳ね返すアクティブタイプ',
 description:
 '『傷寒論』において病が一番外側（表）にある状態。肌のバリアがデリケートで、クーラーや冬の風で首筋や肩がこわばりやすい特徴があります。早めの温活と汗をかきすぎない適度な発散がカギです。',
 coldHeatBalance: 'mild-cold',
 yinYangType: '気虚',
 keySymptoms: ['寒気を感じやすい', '首や肩がこりやすい', '汗をかきにくい、または冷や汗をかく', '季節の変わり目に風邪っぽい'],
 dietAdvice: [
 '体を温めて発散させる「生姜（ショウガ）」や「長ネギの白い部分」を味噌汁に投入！',
 '冷たいジュースや生野菜は避け、温かいスープ中心に切り替えましょう。',
 'シナモンスパイス（桂皮）を入れた温かい紅茶や薬膳茶が効果的。',
 ],
 exerciseAdvice: [
 '肩甲骨まわりをほぐす「風池・風府」ゾーンの温熱ストレッチ。',
 'ラジオ体操や軽い八段錦で、じんわり体に温かさを行き渡らせる。',
 '首の後ろ（風門のツボ）に温かいシャワーや蒸しタオルを当てる。',
 ],
 recommendedIngredients: ['生姜', '長ネギ', 'シナモン', '紫蘇（シソ）', '葛湯（くずゆ）'],
 recommendedStretch: ['肩甲骨はがしストレッチ', '風池（ふうち）のツボ押圧', '八段錦・第1勢'],
 encouragement:
 'あなたは周囲に気を配り、季節の変化にもとても敏感に反応できる優しい感性の持ち主です。寒気や肩こりを感じたら決して無理をせず、温かいスープやお茶でご自身を優しく温めてあげてくださいね。あなたの元気は皆の希望です！',
 acupoints: [
 { name: '合谷 (ごうこく)', location: '親指と人差し指の骨が交わるへこみ', effect: '全身の気の巡りを良くし、寒気を追い払う' },
 { name: '風池 (ふうち)', location: '首の後ろ、髪の生え際のくぼみ', effect: '首肩のこりをほぐし、風の邪気を防御' },
 ],
 },
 shaoyang: {
 id: 'shaoyang',
 name: '少陽病タイプ (寒熱往来・気滞型)',
 kanjiName: '少陽病型',
 tagline: 'ストレスで口が苦い？気の高ぶりと落ち込みが交互に来るセンシティブタイプ',
 description:
 '『傷寒論』で寒気と熱っぽさが交互に来る（寒熱往来）状態。自律神経が過敏になり、イライラしたりため息が増えたり、めまいや脇腹の張りを覚えやすいタイプです。肝の気をほぐすのが最優先！',
 coldHeatBalance: 'neutral',
 yinYangType: '気滞',
 keySymptoms: ['口の中に苦みを感じる', '胸や脇腹が張る', 'イライラと落ち込みの波がある', '朝起きたときにスッキリしない'],
 dietAdvice: [
 '柑橘系（ゆず・レモン・シークヮーサー）で滞った気を爽やかに巡らせましょう。',
 'ミントティーやジャスミン茶など、香り高いハーブティーが最高の薬膳に。',
 '油っこい食事や激辛料理は控え、消化に優しいグリーン野菜をチョイス。',
 ],
 exerciseAdvice: [
 '体を左右にひねる脇腹ストレッチで、胆経（体の側面）の通りを良くする。',
 'ゆったり深呼吸をしながら歩く「マインドフル散歩」。',
 '足の甲にあるツボ「太衝」を痛気持ちいい強さでじっくり押す。',
 ],
 recommendedIngredients: ['三つ葉', '柑橘類', 'ハーブティー', 'セロリ', '春菊'],
 recommendedStretch: ['脇腹の横曲げストレッチ', '太衝（たいしょう）の押し揉み', '八段錦・第3勢'],
 encouragement:
 '日々忙しい中で、心と体が頑張りすぎて揺れることがありますね。完璧を目指さなくて大丈夫。深呼吸と爽やかな柑橘の香りでリセットし、ご自身のペースを愛おしく守っていきましょう！',
 acupoints: [
 { name: '太衝 (たいしょう)', location: '足の親指と人差し指の骨の間', effect: 'ストレスによる肝のたかぶりを鎮め自律神経を安定させる' },
 { name: '陽陵泉 (ようりょうせん)', location: '膝の外側下にある骨のへこみ', effect: '筋肉のつっぱりや脇腹の張りを解消' },
 ],
 },
 yangming: {
 id: 'yangming',
 name: '陽明病タイプ (裏熱・胃腸熱型)',
 kanjiName: '陽明病型',
 tagline: '体内のボイラー超高熱！パワフルで暑がり、冷たい水を求めやすいタイプ',
 description:
 '『傷寒論』で体内に強い熱がこもる状態。食欲旺盛ですが、顔が赤くなりやすく、便秘がちだったり、目が冴えて不眠になったりします。適度に熱を冷まし、うるおい（津液）を補うことが大切です。',
 coldHeatBalance: 'heat',
 yinYangType: '湿熱',
 keySymptoms: ['体熱感が強く暑がり', '冷たい飲み物を好む', '便秘やすっきりしないお通じ', '顔が火照りやすい'],
 dietAdvice: [
 'トマト・きゅうり・豆腐・はとむぎなど、余分な熱をクールダウンする食材を。',
 '氷水の飲みすぎは胃を壊すので、常温の緑茶やドクダミ茶がおすすめ。',
 '肉類の食べすぎを控え、繊維質の豊富な大根やゴボウを取り入れましょう。',
 ],
 exerciseAdvice: [
 '汗をじんわり流すスクワットやウォーキングで熱を発散。',
 '股関節と太もも前側（胃経）を伸ばすストレッチ。',
 '手のツボ「曲池」を押して体内の余分な熱をクリアに。',
 ],
 recommendedIngredients: ['トマト', 'きゅうり', 'はとむぎ', '緑茶', '豆腐', '大根'],
 recommendedStretch: ['太もも前側（胃経）のストレッチ', '曲池（きょくち）のツボ押圧', 'スクワット運動'],
 encouragement:
 'パワフルで前向き、パッションあふれるあなたの情熱はとても素晴らしい魅力です！ただエンジンが過熱した時は優しい野菜スープでひと休み。心を穏やかに保つことで、あなたの本当の良さがさらに広がります。',
 acupoints: [
 { name: '曲池 (きょくち)', location: '肘を曲げた時にできる横じわの外端', effect: '体内のこもった熱を和らげ、肌トラブルを整える' },
 { name: '内庭 (ないてい)', location: '足の第2指と第3指の間の付け根', effect: '胃熱を鎮め、過剰な食欲や歯茎の火照りをケア' },
 ],
 },
 taiyin: {
 id: 'taiyin',
 name: '太陰病タイプ (裏寒湿・脾胃虚弱型)',
 kanjiName: '太陰病型',
 tagline: '胃腸がぽんぽこ冷え冷え！水分が溜まりやすく重だるいお腹ケアタイプ',
 description:
 '『傷寒論』で胃腸（脾）のエネルギーが冷えて低下した状態。お腹が冷えると下痢や膨満感が起きやすく、雨の日や湿度が高い日に体が重だるくなります。温かいお粥とお腹の保温が救世主です！',
 coldHeatBalance: 'cold',
 yinYangType: '水滞',
 keySymptoms: ['食後に眠くなる・胃が重い', '手足や腹部が冷える', 'むくみやすく雨の日に体調を崩す', '便が柔らかくなりやすい'],
 dietAdvice: [
 '朝食には生姜入りの温かいお粥やお味噌汁を習慣に！',
 'かぼちゃ、山芋、さつまいもなど自然な甘みの温性野菜がお腹を元気にします。',
 '冷たいジュース・生もの・白砂糖たっぷりのスイーツは控えめに。',
 ],
 exerciseAdvice: [
 '名ツボ「足三里」を毎日30秒マッサージして消化力をアップ。',
 'お腹に手を当てて円を描くように温める「腹部時計回りマッサージ」。',
 '背筋を伸ばしてお腹に空気を入れる腹式呼吸法。',
 ],
 recommendedIngredients: ['山芋', 'かぼちゃ', '生姜', '黒糖', 'みそ', 'なつめ'],
 recommendedStretch: ['足三里（あしさんり）マッサージ', 'お腹温めマッサージ', 'ひざ抱えストレッチ'],
 encouragement:
 '身体やお腹の冷えを感じる時は、カラダが「少し休んでぬくもりが欲しいよ」とメッセージをくれている証拠です。焦らず温かいお粥を食べ、お腹を温めてあげましょう。自分をいたわる時間が最高の栄養になります。',
 acupoints: [
 { name: '足三里 (あしさんり)', location: '膝のお皿のすぐ下、外側の凹みから指幅4本分下', effect: '東洋医学最高の胃腸強化・疲労回復ツボ' },
 { name: '中脘 (ちゅうかん)', location: 'みぞおちとおへそのちょうど真ん中', effect: '胃の働きを高め消化不良や吐き気を予防' },
 ],
 },
 shaoyin: {
 id: 'shaoyin',
 name: '少陰病タイプ (深部虚寒・陽気減退型)',
 kanjiName: '少陰病型',
 tagline: '芯から冷えてパワーダウン…！じっくり寝てエネルギーを充電するタイプ',
 description:
 '『傷寒論』で全身の生命エネルギー（陽気・腎）が深部から冷え切った状態。手足が氷のように冷たく、横になりたいほどの強い倦怠感や根気不足を感じます。とにかく温めて無理をしない休養が大切。',
 coldHeatBalance: 'cold',
 yinYangType: '陽虚',
 keySymptoms: ['手足の末端が極度に冷たい', '一日中布団に入っていたいほどの倦怠感', '腰やお尻まわりが冷える', '夜間頻尿がある'],
 dietAdvice: [
 '黒ごま、黒豆、ひじき、くるみなど「黒い食材」で腎のパワーを蓄積！',
 'シナモン、ニラ、羊肉や鶏肉、出汁スープで体の奥底から温める。',
 '生野菜は絶対NG。すべて火を通したポトフや煮込み料理を徹底。',
 ],
 exerciseAdvice: [
 '足裏の「湧泉」を青竹踏みやゴルフボールでじんわり刺激。',
 '腰まわり（命門・腎兪）にカイロを貼ったり、腰を前後にゆっくりほぐす。',
 '夜23時までの就寝を厳守（黄帝内経の「冬の養生」の実践）。',
 ],
 recommendedIngredients: ['黒胡麻', '黒豆', 'くるみ', 'シナモン', 'ニラ', '出汁スープ'],
 recommendedStretch: ['湧泉（ゆうせん）ツボ押し', '腰まわり猫のポーズストレッチ', '温足浴（足湯）'],
 encouragement:
 '今日まで本当によく頑張ってこられましたね。お疲れの時は無理に動こうとせず、心置きなく横になって深呼吸してください。命の根っこ（腎）は休むことで必ず蘇ります。焦らず、あたたかい時間を過ごしましょう。',
 acupoints: [
 { name: '湧泉 (ゆうせん)', location: '足裏の指を曲げた時に一番凹む中央部', effect: '湧き出る泉のように生命力をチャージする万能ツボ' },
 { name: '太谿 (たいけい)', location: '内くるぶしとアキレス腱の間のへこみ', effect: '腎の原気を補い冷えと老化・疲労をケア' },
 ],
 },
 jueyin: {
 id: 'jueyin',
 name: '厥陰病タイプ (上熱下寒・錯雑型)',
 kanjiName: '厥陰病型',
 tagline: '頭はのぼせて足は氷？上熱下寒のアンバランスをリセットする繊細タイプ',
 description:
 '『傷寒論』の最も奥深い段階。上半身や顔はカーッと熱くなるのに、足元は冷たく、冷えのぼせや緊張・緊張性頭痛が起きやすい状態です。頭の熱を下げ、足元を温めて上下の巡りを回復させましょう。',
 coldHeatBalance: 'mild-cold',
 yinYangType: '陰虚',
 keySymptoms: ['顔や頭は火照るのに足先は冷える', '突然のイライラや緊張', '動悸や頭痛が起きやすい', '夢を多く見て浅い睡眠'],
 dietAdvice: [
 '足元を温める生姜と、上の熱を静めるミントや菊花を組みあわせたハーブティー。',
 'クコの実、松の実、ナツメで血（津液）を補い精神を安定。',
 '極端に辛い料理や大量のアルコールは頭の火照りを悪化させるので注意。',
 ],
 exerciseAdvice: [
 '「頭寒足熱」を実現する頭マッサージと足湯のハイブリッドケア。',
 '手のツボ「内関」で胸のつかえや動悸をリラックス。',
 '深呼吸をしながら足をゆっくり踏みしめる太極拳の足踏み。',
 ],
 recommendedIngredients: ['クコの実', '菊花', 'ナツメ', '松の実', '麦茶', 'ハトムギ'],
 recommendedStretch: ['首筋ストレッチ', '内関（ないかん）ツボ押し', '足浴＆頭部軽擦'],
 encouragement:
 '上半身の火照りと足元の冷えで、身体のコントロールに繊細なエネルギーを使われていますね。頭寒足熱の足湯やツボ押しで、上下の巡りを優しく結び直しましょう。あなたは本来、しなやかで強い回復力を持っています。',
 acupoints: [
 { name: '内関 (ないかん)', location: '手首の横じわから指幅3本分肘寄りの中央', effect: '自律神経を整え、胸のつかえや冷えのぼせを抑える' },
 { name: '百会 (ひゃくえ)', location: '両耳を結んだ線と頭の正中線が交わる頂点', effect: '頭部に上がった過剰な気を穏やかに引き下げる' },
 ],
 },
};

export const QUIZ_QUESTIONS: QuizQuestion[] = [
 {
 id: 1,
 question: 'Q1. あなたの年代（年齢層）を教えてください',
 subtitle: '年齢による五行生命力（腎気）の変化を考慮します',
 options: [

 { text: '20代未満（元気溢れる若年期）', badgeText: '木気旺盛', elements: { wood: 25 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: '20代〜30代（仕事・家事で代謝活発）', badgeText: '火木充実', elements: { wood: 20, fire: 20 }, shanghanPoints: { taiyang: 1, shaoyang: 1 }, xp: 20 },
 { text: '40代〜50代（身体の曲がり角・冷え注意期）', badgeText: '土金陰陽転換', elements: { earth: 25, metal: 20 }, shanghanPoints: { taiyin: 2, shaoyin: 1 }, xp: 20 },
 { text: '60代以上（腎精を優しく育む温活期）', badgeText: '水腎ケア期', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 2,
 question: 'Q2. あなたの性別を教えてください',
 subtitle: '男性は『気』、女性は『血』を中心とする体質傾向',
 options: [
 { text: '女性（月経・冷え・血の滞り『瘀血』を配慮）', badgeText: '血陰重視', elements: { wood: 20, water: 20 }, shanghanPoints: { shaoyang: 2, jueyin: 2 }, xp: 20 },
 { text: '男性（内熱・胃熱・仕事のストレス『気鬱』を配慮）', badgeText: '気陽重視', elements: { fire: 20, wood: 20 }, shanghanPoints: { yangming: 2, shaoyang: 2 }, xp: 20 },
 { text: 'その他・回答しない', badgeText: '陰陽和合', elements: { earth: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
 ],
 },
 {
 id: 3,
 question: 'Q3. 普段のお酒（飲酒）の頻度と量はどれくらいですか？',
 subtitle: 'アルコールは熱と湿気（湿熱）を生む重要ファクターです',
 options: [

 { text: '毎日飲む（晩酌が日常・習慣）', badgeText: '湿熱ため込み注意', elements: { fire: 30, earth: 25 }, shanghanPoints: { yangming: 3 }, xp: 20 },
 { text: '週に2〜3回程度（たしなむ程度）', badgeText: '適度な巡り', elements: { wood: 20 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
 { text: '月に数回・機会飲酒のみ', badgeText: 'マイルド体質', elements: { earth: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
 { text: '全く飲まない・お酒に弱い', badgeText: '湿熱ゼロ', elements: { metal: 20, earth: 20 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 4,
 question: 'Q4. お酒を飲む際、好んで飲む『酒類の種類』は？',
 subtitle: '冷えたビールは胃腸を冷やし、熱燗やワインは身体を温めます',
 options: [

 { text: 'キンキンに冷えた生ビール・缶サワー・ハイボール', badgeText: '胃寒・水毒原因', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '温かい日本酒（熱燗）・お湯割り焼酎', badgeText: '温中散寒', elements: { fire: 20, metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
 { text: '赤ワイン・常温の洋酒', badgeText: '気血めぐり', elements: { wood: 20, fire: 20 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
 { text: 'お酒は飲まない・お茶中心', badgeText: 'お茶派', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 5,
 question: 'Q5. 氷水や冷たいジュース・冷やしたお茶の日常習慣は？',
 subtitle: '東洋医学で最も忌避される『胃腸ボイラーの冷やし』チェック！',
 options: [

 { text: '毎日氷入りの水やキンキンに冷えた飲料を飲む', badgeText: '脾胃ボイラー消火', elements: { earth: 35 }, shanghanPoints: { taiyin: 3, shaoyin: 2 }, xp: 20 },
 { text: '夏場や運動後だけ冷たいものを飲む', badgeText: '季節限定冷やし', elements: { earth: 20 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
 { text: '常温の水・白湯・あたたかいお茶を年中意識している', badgeText: '温活マスター', elements: { earth: 20, metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 6,
 question: 'Q6. 生野菜サラダやアイスクリーム・刺身などの冷菜習慣は？',
 subtitle: '生の冷たい食材は胃腸の消化の火（脾陽）を弱めます',
 options: [

 { text: '毎日生野菜サラダや冷たい料理・アイスを好んで食べる', badgeText: 'お腹冷湿たまり', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '加熱した温野菜・スープ・温かい料理を中心にして飲食している', badgeText: '火の消化サポート', elements: { earth: 25 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 7,
 question: 'Q7. 朝起きた時の身体の目覚め具合は？',
 subtitle: '朝一番の身体エンジンをチェック！',
 options: [

 { text: '首や肩がカチコチ！温かい上着を着たい', badgeText: '風寒ガード', elements: { wood: 10, metal: 20 }, shanghanPoints: { taiyang: 3 }, xp: 20 },
 { text: '起き抜けに口が苦く、頭がボーッとする', badgeText: '自律神経モヤモヤ', elements: { wood: 25 }, shanghanPoints: { shaoyang: 3 }, xp: 20 },
 { text: '朝から体が熱くて、冷たい水が飲みたい', badgeText: 'ボイラー高熱', elements: { fire: 25 }, shanghanPoints: { yangming: 3 }, xp: 20 },
 { text: '胃が重くて、布団から出たくない', badgeText: '胃腸お疲れ', elements: { earth: 25 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '手足が氷のように冷たくて動けない', badgeText: '深部ひえひえ', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 8,
 question: 'Q8. ストレスがピークに達した時、身体はどうなる？',
 subtitle: 'ココロと身体のSOSシグナル！',
 options: [

 { text: 'イライラ爆発！ 脇腹が張って怒りっぽくなる', badgeText: '肝気高ぶり', elements: { wood: 30 }, shanghanPoints: { shaoyang: 3 }, xp: 20 },
 { text: '胸がドキドキ！ 夜中に目が冴えて眠れない', badgeText: '心火アップ', elements: { fire: 30 }, shanghanPoints: { jueyin: 2 }, xp: 20 },
 { text: '甘いものをドカ食いして胃がもたれる', badgeText: 'ドカ食いストレス', elements: { earth: 30 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
 { text: 'ため息が止まらず、肌荒れや咳が出る', badgeText: 'バリア低下', elements: { metal: 30 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: '急に怖くなったり、気力が底をつく', badgeText: 'バッテリーゼロ', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 9,
 question: 'Q9. 夜の睡眠と布団に入った時の感覚は？',
 subtitle: '夜の陰気と睡眠の質を診断！',
 options: [

 { text: '布団に入っても足が冷たくて寝付けない', badgeText: '足先フリーズ', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
 { text: '夢をたくさん見て、浅い眠りになりやすい', badgeText: '安眠レス', elements: { fire: 25 }, shanghanPoints: { jueyin: 3 }, xp: 20 },
 { text: '足や手が熱くて布団から出してしまう', badgeText: '手足ほてり', elements: { fire: 25 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: '昼間もずっと眠くて倦怠感がある', badgeText: '気力ダウン', elements: { earth: 25 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 10,
 question: 'Q10. 雨の日や湿気が多い天気のコンディションは？',
 subtitle: '湿邪（湿気）への強さをチェック！',
 options: [

 { text: 'ナメクジのように体が重だるく、顔や足がむくむ', badgeText: '湿気たまり', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '気圧の変化で頭痛やめまいが起きやすい', badgeText: '気圧デリケート', elements: { wood: 25 }, shanghanPoints: { shaoyang: 2, jueyin: 2 }, xp: 20 },
 { text: '関節や腰がズキズキ痛む', badgeText: '寒湿の滞り', elements: { water: 25 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
 { text: '天気の影響はほとんど受けない！爽やか', badgeText: '元気バリア', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 11,
 question: 'Q11. あなたの毎日のお通じ（便）の状態は？',
 subtitle: '腸内環境と脾胃の熱・冷え状態をチェック！',
 options: [

 { text: '毎日コロコロ固くて便秘がち（便が硬い）', badgeText: '腸乾燥熱', elements: { fire: 25, metal: 20 }, shanghanPoints: { yangming: 3 }, xp: 20 },
 { text: '泥状・柔らかくてすっきりしないことが多い', badgeText: 'お腹冷え湿', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: 'ストレスで急にお腹が痛くなって下す', badgeText: '過敏お腹', elements: { wood: 25 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: '毎朝つるんとバナナ便で快調！', badgeText: '快腸マスター', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 12,
 question: 'Q12. 首筋や肩のこり方の特徴は？',
 subtitle: '気の滞りと邪気の入り口をチェック！',
 options: [

 { text: '風が当たると一瞬で肩と首がガチガチになる', badgeText: '風邪の入り口', elements: { metal: 25 }, shanghanPoints: { taiyang: 3 }, xp: 20 },
 { text: 'ストレスやパソコン作業で首筋が張る', badgeText: '肝気滞り', elements: { wood: 30 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: '重だるくて、揉んでもあまりすっきりしない', badgeText: '血行滞り', elements: { water: 20 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 13,
 question: 'Q13. 今日飲みたいスープの味付け・種類は？',
 subtitle: '五味（酸・苦・甘・辛・鹹）から身体の欲求をキャッチ！',
 options: [

 { text: 'レモン香るサンラータン・酢の物スープ（酸味）', badgeText: '肝を養う酸', elements: { wood: 30 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: 'ジャスミン茶やゴーヤのさっぱりスープ（苦味）', badgeText: '心を鎮める苦', elements: { fire: 30 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: 'かぼちゃとポテトの濃厚温かポタージュ（甘味）', badgeText: '脾を元気にする甘', elements: { earth: 30 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
 { text: '生姜と長ネギのピリ辛温活ポトフ（辛味）', badgeText: '肺を潤す辛', elements: { metal: 30 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: 'ひじきと黒豆の出汁旨味スープ（鹹味）', badgeText: '腎を育む塩味', elements: { water: 30 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 14,
 question: 'Q14. パソコンやスマホを見た後の目のコンディションは？',
 subtitle: '「肝は目に開竅する」視力と気の疲労度！',
 options: [

 { text: '目がシパシパ乾燥して、しょぼしょぼする', badgeText: '肝血不足', elements: { wood: 30 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: '目の奥がズキズキ痛んで赤くなりやすい', badgeText: '肝火のぼせ', elements: { wood: 20, fire: 15 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: 'まぶたが重くなってすぐ眠くなる', badgeText: '脾気低下', elements: { earth: 25 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 15,
 question: 'Q15. 自分の身体の「暑がり／寒がり」タイプはどれ？',
 subtitle: '傷寒論の「寒・熱」バランスの基本！',
 options: [

 { text: '超寒がり！ カイロと靴下が手放せない', badgeText: '寒症タイプ', elements: { water: 30 }, shanghanPoints: { shaoyin: 3, taiyin: 2 }, xp: 20 },
 { text: '超暑がり！ すぐ顔が赤くなって汗が出る', badgeText: '熱症タイプ', elements: { fire: 30 }, shanghanPoints: { yangming: 3 }, xp: 20 },
 { text: '頭は火照るのに、足元は氷のように冷たい', badgeText: '冷えのぼせ', elements: { wood: 20, water: 20 }, shanghanPoints: { jueyin: 3 }, xp: 20 },
 { text: 'ちょうど良くバランスが取れている', badgeText: '平人（理想）', elements: { earth: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 16,
 question: 'Q16. 普段飲みたくなるお茶の好みは？',
 subtitle: 'お茶の性味（温性・涼性）による好み診断！',
 options: [

 { text: '生姜紅茶や桂皮（シナモン）茶（温める）', badgeText: '温活チャージ', elements: { metal: 25 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: 'ジャスミン茶やほうじ茶（香りでリラックス）', badgeText: '理気巡り', elements: { wood: 25 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: 'ドクダミ茶や冷やし緑茶（クールダウン）', badgeText: '清熱解毒', elements: { fire: 25 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: 'はとむぎ茶や黒豆茶（むくみオフ＆補腎）', badgeText: '利水補腎', elements: { earth: 20, water: 20 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 17,
 question: 'Q17. 汗のかき方のクセは？',
 subtitle: '肌のバリア機能（衛気）と代謝状態！',
 options: [

 { text: '動いていなくてもダラダラ大量に汗をかく', badgeText: '衛気もれ', elements: { metal: 25 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: '暑くてもほとんど汗をかけず蒸れてしまう', badgeText: '毛穴ブロック', elements: { metal: 25 }, shanghanPoints: { taiyang: 3 }, xp: 20 },
 { text: '寝ている間にじんわり嫌な汗（寝汗）をかく', badgeText: '陰虚ほてり', elements: { fire: 20 }, shanghanPoints: { jueyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 18,
 question: 'Q18. お口の中や唇のコンディションは？',
 subtitle: '「脾は口に開竅する」消化器のシグナル！',
 options: [

 { text: '唇がすぐカサカサ乾いて皮がむける', badgeText: '津液不足', elements: { metal: 25 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: '口の中が粘つく感じがあり、舌に白い苔がつく', badgeText: '胃腸の湿気', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '口内炎ができやすく、口の中が苦い', badgeText: '少陽の苦み', elements: { wood: 25 }, shanghanPoints: { shaoyang: 3 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 19,
 question: 'Q19. 軽い運動（ウォーキングや体操）をした後の気分は？',
 subtitle: '運動による気の循環効果！',
 options: [

 { text: ' 身体が軽くなって気分すっきり！元気が湧く', badgeText: '気機すっきり', elements: { wood: 20, earth: 10 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
 { text: ' 途中でドッと疲れて動けなくなってしまう', badgeText: '気虚バッテリー少', elements: { earth: 30 }, shanghanPoints: { taiyin: 2, shaoyin: 2 }, xp: 20 },
 { text: ' 体がぽかぽか温まって冷えが吹き飛ぶ', badgeText: '陽気チャージ', elements: { water: 25 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 20,
 question: 'Q20. 普段好んで食べたい主食・穀物はどれ？',
 subtitle: '穀物の気で脾胃を養う！',
 options: [

 { text: ' 熱々で胃に優しい玄米お粥やお味噌汁', badgeText: '健脾スープ', elements: { earth: 30 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
 { text: ' ホクホクのさつまいもや熟したかぼちゃ', badgeText: '自然な甘み', elements: { earth: 25 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
 { text: ' パスタやパンなど小麦系が大好き', badgeText: '小麦ラブ', elements: { fire: 15 }, shanghanPoints: { yangming: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 21,
 question: 'Q21. ツボ押しをした時、どこが一番「痛気持ちいい」？',
 subtitle: '経絡の滞りポイントをチェック！',
 options: [

 { text: ' 膝の下「足三里（あしさんり）」が一番効く', badgeText: '胃腸疲労', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: ' 足の親指の甲「太衝（たいしょう）」が痛い', badgeText: 'ストレス肝滞', elements: { wood: 30 }, shanghanPoints: { shaoyang: 3 }, xp: 20 },
 { text: '️ 手の親指「合谷（ごうこく）」が響く', badgeText: '頭肩こり風寒', elements: { metal: 25 }, shanghanPoints: { taiyang: 3 }, xp: 20 },
 { text: ' 足裏中央「湧泉（ゆうせん）」がジンジンする', badgeText: '生命力チャージ', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 22,
 question: 'Q22. 酸っぱいもの（レモン・梅干し・お酢）に対する感覚は？',
 subtitle: '酸味（木）の収斂作用への反応！',
 options: [

 { text: ' 酸っぱいものが無性に食べたくなる！', badgeText: '肝が酸味を要求', elements: { wood: 30 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: ' 酸っぱいものは苦手、胃がキュッとしみる', badgeText: '胃が酸に弱い', elements: { earth: 25 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 23,
 question: 'Q23. 黒い食材（黒ごま、黒豆、ひじき、きくらげ）を食べる頻度は？',
 subtitle: '腎精（エイジングケア）の摂取度！',
 options: [

 { text: '頻繁に食べる！ 大好き', badgeText: '黒の補腎上手', elements: { water: 30 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
 { text: 'あまり意識して食べていないかも…', badgeText: '補腎チャンス', elements: { water: 10 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 24,
 question: 'Q24. ️ 寒風が吹いた時の首・鼻の反応は？',
 subtitle: '「肺は鼻に開竅する」表証チェック！',
 options: [

 { text: ' くしゃみや透明な鼻水がすぐ出る', badgeText: '水様鼻水', elements: { metal: 25 }, shanghanPoints: { taiyang: 3 }, xp: 20 },
 { text: '喉が乾燥してイライラ痛む', badgeText: '喉の乾燥', elements: { metal: 30 }, shanghanPoints: { yangming: 1 }, xp: 20 },
 { text: '平気！ 寒さにも負けない強いバリアがある', badgeText: '無敵バリア', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 25,
 question: 'Q25. 緊張する場面での胃腸の反応は？',
 subtitle: '木（肝）が土（脾）を攻撃する「木克土」チェック！',
 options: [

 { text: '緊張するとすぐお腹が痛くなる・キューッと縮こまる', badgeText: '木克土ストレス', elements: { wood: 20, earth: 20 }, shanghanPoints: { shaoyang: 2, taiyin: 2 }, xp: 20 },
 { text: '緊張しても食欲は落ちない！ ガツガツ食べられる', badgeText: '鋼の胃腸', elements: { earth: 20 }, shanghanPoints: { yangming: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 26,
 question: 'Q26. 夜23時までにベッドに入れていますか？',
 subtitle: '『黄帝内経』の「胆経タイム（23:00〜1:00）」遵守度！',
 options: [

 { text: 'はい！ 23時前にはぐっすり眠っている', badgeText: '黄帝内経優等生', elements: { wood: 25, water: 25 }, shanghanPoints: { shaoyang: 1, shaoyin: 1 }, xp: 20 },
 { text: 'ついつい夜更かしして深夜1〜2時になりがち', badgeText: '夜更かし細胞', elements: { wood: 10 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 27,
 question: 'Q27. 休みの日の理想の過ごし方は？',
 subtitle: '気・血・津液の充電スタイル！',
 options: [

 { text: 'とにかくベッドで横になって身体を休めたい', badgeText: 'じっくり充電', elements: { earth: 20, water: 20 }, shanghanPoints: { taiyin: 2, shaoyin: 2 }, xp: 20 },
 { text: '外に出て散歩やドライブで気をリフレッシュしたい！', badgeText: 'アクティブ発散', elements: { wood: 25 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 28,
 question: 'Q28. 生姜（ショウガ）やシソ（紫蘇）の料理は好き？',
 subtitle: '発散・温中食材の好み！',
 options: [

 { text: '大好き！ たっぷり薬味を入れて食べたい', badgeText: '薬味温活派', elements: { metal: 25 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: '辛くて少し苦手かも', badgeText: 'マイルド派', elements: { earth: 20 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 29,
 question: 'Q29. 耳鳴りやめまいを感じることはありますか？',
 subtitle: '「腎は耳に開竅する」耳のシグナル！',
 options: [

 { text: '疲れると耳鳴りやふわふわしためまいが起きやすい', badgeText: '腎精・肝気注意', elements: { water: 25, wood: 20 }, shanghanPoints: { shaoyin: 2, shaoyang: 2 }, xp: 20 },
 { text: 'めまいや耳鳴りは全くない', badgeText: '耳も元気', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 30,
 question: 'Q30. 普段緑黄色野菜やハーブ、柑橘類をよく食べますか？',
 subtitle: '肝（木）をのびのび育てる食材！',
 options: [

 { text: '毎日意識して食べている！', badgeText: '緑の巡り完璧', elements: { wood: 30 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
 { text: 'あまり野菜を食べれていないかも…', badgeText: '緑パワー不足', elements: { wood: 10 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 31,
 question: 'Q31. 足首やふくらはぎの「むくみ」具合は？',
 subtitle: '水（腎・膀胱）の水代謝チェック！',
 options: [

 { text: '夕方になると靴がきつくなるほどパンパンにむくむ', badgeText: '水分溜まり', elements: { earth: 25, water: 25 }, shanghanPoints: { taiyin: 2, shaoyin: 2 }, xp: 20 },
 { text: 'むくみはほとんど気にならない', badgeText: '水巡りスッキリ', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 32,
 question: 'Q32. 湯船に浸かった時の身体の変化は？',
 subtitle: '温浴効果と冷えの解消度！',
 options: [

 { text: '極楽！ 芯から温まって疲れが吹き飛ぶ', badgeText: '温浴チャージ', elements: { water: 25, fire: 15 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
 { text: '長湯するとすぐのぼせて気分が悪くなる', badgeText: 'のぼせ注意', elements: { wood: 20, fire: 20 }, shanghanPoints: { jueyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 33,
 question: 'Q33. 白湯（あたたかいお湯）を毎朝飲んでいますか？',
 subtitle: '無薬・食養生の一番簡単な第一歩！',
 options: [

 { text: '毎朝の習慣になっている！ お腹が落ち着く', badgeText: '白湯マスター', elements: { earth: 25 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
 { text: 'これから始めたいと思っている！', badgeText: '白湯ビギナー', elements: { earth: 15 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 34,
 question: 'Q34. 「気功（八段錦）」やラジオ体操をやってみたい？',
 subtitle: '経絡を意識した身体アプローチ！',
 options: [

 { text: 'ぜひ習慣にしたい！ 呼吸を深くしたい', badgeText: '八段錦チャレンジャー', elements: { metal: 25, wood: 20 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
 { text: 'まずは食事のアドバイスから実践したい', badgeText: '食養生先行派', elements: { earth: 20 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 35,
 question: 'Q35. のどの乾き（口渇）と冷水への欲求は？',
 subtitle: '津液（体液）の消耗と内部の熱状態',
 options: [

 { text: '口がカラカラに乾き、冷たい水をゴクゴク飲みたい', badgeText: '実熱・口渇', elements: { fire: 30 }, shanghanPoints: { yangming: 3 }, xp: 20 },
 { text: '口は乾くが、温かい飲み物を少し口に含むだけで十分', badgeText: '陰虚・温水欲', elements: { water: 25 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
 { text: 'のどはあまり渇かない', badgeText: '津液良好', elements: { earth: 20 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 36,
 question: 'Q36. 胸のつかえ・みぞおちの圧迫感・ため息はありますか？',
 subtitle: '「気」の流れの滞り（気鬱）を診断',
 options: [

 { text: 'みぞおちが詰まった感じがして、ため息がよく出る', badgeText: '気滞・気鬱', elements: { wood: 30 }, shanghanPoints: { shaoyang: 3 }, xp: 20 },
 { text: '胸のつかえや圧迫感は特にない', badgeText: '気機のびのび', elements: { wood: 20 }, shanghanPoints: { shaoyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 37,
 question: 'Q37. 手先や足先の温度感（末端冷え）はどれに近い？',
 subtitle: '陽気の巡りと末端への血流（末梢循環）',
 options: [

 { text: '年中手足がキンキンに冷えている', badgeText: '陽虚・末端冷え', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
 { text: '手足は温かいが、お腹だけが冷たい', badgeText: '腹部中寒', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '全身ぽかぽか温かい', badgeText: '陽気旺盛', elements: { fire: 20 }, shanghanPoints: { yangming: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 38,
 question: 'Q38. 甘い食べ物（お菓子・和菓子・パン）への強いほしさは？',
 subtitle: '脾気（消化器）が弱ると甘味を過剰に欲します',
 options: [

 { text: '食後に甘いものを食べないと落ち着かない', badgeText: '脾気低下・甘味欲', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '甘いものはたまに少量食べる程度で十分', badgeText: '脾胃安定', elements: { earth: 20 }, shanghanPoints: { taiyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 39,
 question: 'Q39. 朝起きた時の口の中の苦味や粘つきは？',
 subtitle: '少陽（肝胆）の熱、湿熱の停滞シグナル',
 options: [

 { text: '朝起きた時、口の中が苦い（口苦）', badgeText: '少陽胆熱', elements: { wood: 30 }, shanghanPoints: { shaoyang: 3 }, xp: 20 },
 { text: '朝起きた時、口の中がねばねば・ネバつく', badgeText: '脾胃湿熱', elements: { earth: 30 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
 { text: '口の中は朝からすっきり快適', badgeText: '清爽状態', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 40,
 question: 'Q40. 腰や膝の重だるさ、関節の力抜けはありますか？',
 subtitle: '「腎は骨を主どる」腎気の衰えをチェック',
 options: [

 { text: '長時間立つと腰や膝が抜けそうに重だるくなる', badgeText: '腎気疲労', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
 { text: '腰や膝はしっかり丈夫で力が入る', badgeText: '腎精充実', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 41,
 question: 'Q41. 季節の変わり目に風邪を引きやすいですか？',
 subtitle: '衛気（バリア免疫）の強さ',
 options: [

 { text: '季節の変わり目には必ず喉痛や風邪を引く', badgeText: '衛気バリア低下', elements: { metal: 30 }, shanghanPoints: { taiyang: 3 }, xp: 20 },
 { text: '風邪はほとんど引かない！ 体調が安定している', badgeText: 'バリア強固', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 42,
 question: 'Q42. 肌の乾燥や粉ふき・かゆみは気になりますか？',
 subtitle: '「肺は皮毛を主どる」津液とうるおい',
 options: [

 { text: '冬場やクーラーで肌が粉をふくほど乾燥する', badgeText: '肺陰・血虚', elements: { metal: 30 }, shanghanPoints: { yangming: 1 }, xp: 20 },
 { text: '肌のうるおいは保たれている', badgeText: '津液潤滑', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 43,
 question: 'Q43. ️ 長く喋ると声が小さくなったり、呼吸が浅くなりますか？',
 subtitle: '宗気・肺気のパワー測定',
 options: [

 { text: '人と話すとすぐ声が枯れ、呼吸が浅く疲れる', badgeText: '肺気虚', elements: { metal: 30 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: '大きなハッキリした声がしっかり出る', badgeText: '肺気パワフル', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 44,
 question: 'Q44. ️ 辛い料理（唐辛子・麻婆豆腐・スパイス）の好みは？',
 subtitle: '辛味による発散と胃熱のチェック',
 options: [

 { text: '激辛料理が大好きで日常的に食べる', badgeText: '辛味発散・胃熱', elements: { metal: 20, fire: 20 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: '辛いものは苦手・お腹を壊しやすい', badgeText: '脾胃デリケート', elements: { earth: 25 }, shanghanPoints: { taiyin: 2 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 45,
 question: 'Q45. 昼間のおしっこ（尿）の回数と色の傾向は？',
 subtitle: '水代謝と腎・膀胱の熱・冷え状態',
 options: [

 { text: '回数が多く（1日8回以上）、色が薄く透明', badgeText: '腎陽虚・水代謝低下', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
 { text: '回数が少なく、色が濃い黄色で少し臭う', badgeText: '膀胱湿熱', elements: { fire: 25 }, shanghanPoints: { yangming: 2 }, xp: 20 },
 { text: '適度な回数と自然な薄黄色', badgeText: '水代謝良好', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 46,
 question: 'Q46. 夜起きてトイレに行く（夜間尿）頻度は？',
 subtitle: '「腎は二陰（排泄）を司る」夜の腎気チェック',
 options: [

 { text: '毎夜1〜2回以上起きてトイレに行く', badgeText: '夜間腎気注意', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
 { text: '朝までぐっすり起きてトイレに行くことはない', badgeText: '朝までぐっすり', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 47,
 question: 'Q47. 揚げ物や肉料理・脂っこいものを食べた後の胃は？',
 subtitle: '消化酵素（脾の運化機能）の強さ',
 options: [

 { text: 'すぐ胃がもたれて吐き気や胃痛がする', badgeText: '消化力ダウン', elements: { earth: 30 }, shanghanPoints: { taiyin: 3 }, xp: 20 },
 { text: '胃もたれせずガッツリ消化できる！', badgeText: '強力胃袋', elements: { earth: 20 }, shanghanPoints: { yangming: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 48,
 question: 'Q48. 物忘れが増えたり、頭のすっきり感が落ちていませんか？',
 subtitle: '「脳は髄の海」腎精と血の栄養状態',
 options: [

 { text: '物忘れや頭のモヤモヤ（ブレインフォグ）が気になる', badgeText: '腎精補給期', elements: { water: 30, wood: 20 }, shanghanPoints: { shaoyin: 2 }, xp: 20 },
 { text: '頭脳明晰で集中力がしっかり続く', badgeText: '脳髄すっきり', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 49,
 question: 'Q49. 1年の中で一番「体調を崩しやすい季節」はいつですか？',
 subtitle: '四季の邪気（風・暑・湿・燥・寒）への感受性',
 options: [

 { text: ' 春（風邪・花粉症・自律神経ブレ）', badgeText: '春の風木に敏感', elements: { wood: 30 }, shanghanPoints: { shaoyang: 2 }, xp: 20 },
 { text: '️ 夏・梅雨（熱中症・湿気・夏バテ）', badgeText: '夏の暑湿に敏感', elements: { fire: 25, earth: 25 }, shanghanPoints: { yangming: 2, taiyin: 2 }, xp: 20 },
 { text: ' 秋（喉痛・乾燥・肺のトラブル）', badgeText: '秋の燥金に敏感', elements: { metal: 30 }, shanghanPoints: { taiyang: 2 }, xp: 20 },
 { text: '️ 冬（強い冷え・関節痛・インフルエンザ）', badgeText: '冬の寒水に敏感', elements: { water: 30 }, shanghanPoints: { shaoyin: 3 }, xp: 20 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
 {
 id: 50,
 question: 'Q50. ️ 最後に、自分の身体の自然治癒力を高める『無薬食養生』への思いは？',
 subtitle: 'これからの健康な心身に向けた養生の宣言！',
 options: [

 { text: ' 薬に頼らず、毎日の食材とツボ押しで最高の健康を手に入れたい！', badgeText: '養生マスター宣言', elements: { wood: 20, fire: 20, earth: 20, metal: 20, water: 20 }, shanghanPoints: { taiyang: 1 }, xp: 50 },
 { text: ' 無理なく自分のペースで温活と美味しい薬膳を楽しみたい', badgeText: 'のんびり温活宣言', elements: { earth: 30 }, shanghanPoints: { taiyin: 1 }, xp: 50 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },

  {
    id: 51,
    question: 'Q51. よく下痢をしたり、お腹が冷えて便がゆるくなりやすいですか？',
    subtitle: '「脾は運化を主どる」脾胃の冷え（脾胃虚寒）チェック',
    options: [

      { text: '冷えたり冷たいものを摂るとすぐ下痢・お腹が下る', badgeText: '脾胃虚寒', elements: { earth: 35 }, shanghanPoints: { taiyin: 3 }, xp: 0 },
      { text: 'お腹は丈夫で、あまり下痢することはない', badgeText: '胃腸良好', elements: { earth: 20 }, shanghanPoints: { yangming: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 52,
    question: 'Q52. よく頭痛（片頭痛・後頭部痛・重だるい痛み）が起こりますか？',
    subtitle: '「頭は諸陽の会」肝気の上昇・血虚・水湿の滞り',
    options: [

      { text: 'ストレスや天候でよく頭痛がし、頭が重重しく痛む', badgeText: '肝陽上亢・気滞頭痛', elements: { wood: 30, water: 20 }, shanghanPoints: { shaoyang: 3 }, xp: 0 },
      { text: '普段あまり頭痛を感じることはない', badgeText: '頭部清爽', elements: { wood: 20 }, shanghanPoints: { taiyang: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 53,
    question: 'Q53. つらい肩こり・首筋の凝り・背中の張りを感じますか？',
    subtitle: '血行不良（瘀血）と自律神経（肝気鬱結）の緊張',
    options: [

      { text: '日常的に肩や首がパンパンに凝り固まっている', badgeText: '気滞瘀血・肩こり', elements: { wood: 30, fire: 20 }, shanghanPoints: { taiyang: 2 }, xp: 0 },
      { text: '肩や首は柔らかく緊張しにくい', badgeText: '気血順調', elements: { wood: 20 }, shanghanPoints: { taiyang: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 54,
    question: 'Q54. 目の疲れ・乾き・かすみ・ピントが合いにくい症状はありますか？',
    subtitle: '「肝は目に開竅する」肝血の消耗度チェック',
    options: [

      { text: 'スマホやPCで目がすぐ疲れ、乾きや充血が気になる', badgeText: '肝血虚・目疲労', elements: { wood: 35 }, shanghanPoints: { shaoyang: 2 }, xp: 0 },
      { text: '視界はクリアで目はあまり疲れない', badgeText: '肝血充満', elements: { wood: 20 }, shanghanPoints: { taiyang: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 55,
    question: 'Q55. 疲れやすく、朝起きるのがつらかったり体がだるいですか？',
    subtitle: '「気虚」エネルギー不足と生命力の衰え（気虚・腎虚）',
    options: [

      { text: '慢性的に疲れやすく、横になりたくなる', badgeText: '気虚・疲労蓄積', elements: { earth: 30, water: 25 }, shanghanPoints: { taiyin: 3, shaoyin: 2 }, xp: 0 },
      { text: '朝から活力があり元気に動ける', badgeText: '気力充実', elements: { earth: 20 }, shanghanPoints: { yangming: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 56,
    question: 'Q56. ラーメンや漬物など、塩っぱいもの・濃い味付けをよく食べますか？',
    subtitle: '「鹹味は腎に入る」塩分過多と水代謝への影響',
    options: [

      { text: '濃い味・塩辛いものが好きでよく食べる（むくみや喉の渇きあり）', badgeText: '鹹味過多・腎負荷', elements: { water: 30 }, shanghanPoints: { shaoyin: 2 }, xp: 0 },
      { text: '薄味好みで塩分控えめを意識している', badgeText: '適塩・水代謝良好', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 57,
    question: 'Q57. ケーキ・和菓子・チョコなど、甘いものをよく食べますか？',
    subtitle: '「甘味は脾に入る」甘味過多と体内の湿気（湿濁）生成',
    options: [

      { text: '甘いものをほぼ毎日食べてしまい、体が重だるくなりやすい', badgeText: '甘味過多・湿重', elements: { earth: 35 }, shanghanPoints: { taiyin: 3 }, xp: 0 },
      { text: '甘いものはあまり食べない・たまに少量摂る程度', badgeText: '脾胃すっきり', elements: { earth: 20 }, shanghanPoints: { yangming: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 58,
    question: 'Q58. いつも満腹になるまで食べてしまったり、過食気味ですか？',
    subtitle: '「飲食に節なし」お腹の停滞（食滞・胃熱）チェック',
    options: [

      { text: '満腹になるまで食べないと満足できず腹膨満感がある', badgeText: '食滞・過食傾向', elements: { earth: 30, fire: 20 }, shanghanPoints: { yangming: 3 }, xp: 0 },
      { text: '腹八分目を心がけて美味しく腹八分でやめられる', badgeText: '腹八分目・胃腸健全', elements: { earth: 20 }, shanghanPoints: { yangming: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 59,
    question: 'Q59. キムチやスパイスなど、辛いものをよく食べる結果はどうですか？',
    subtitle: '「辛味は肺に入る」津液乾燥と熱のこもり',
    options: [

      { text: '辛いものを食べると汗が吹き出し、吹き出物や喉の乾燥が出やすい', badgeText: '辛味過多・津液乾燥', elements: { metal: 30, fire: 20 }, shanghanPoints: { yangming: 2 }, xp: 0 },
      { text: '辛いものは適量または控えめで肌や喉に影響はない', badgeText: '肺陰保護', elements: { metal: 20 }, shanghanPoints: { taiyang: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 60,
    question: 'Q60. 氷入りの冷たい飲み物や生ものをよく摂る生活習慣はありますか？',
    subtitle: '「冷えは万病の素」お腹のボイラー（胃腸陽気）の冷却度',
    options: [

      { text: '冷たい飲み物を一年中よく飲み、お腹が冷えやすい', badgeText: 'お腹ボイラー消火', elements: { earth: 35, water: 20 }, shanghanPoints: { taiyin: 3 }, xp: 0 },
      { text: '温かい飲み物や常温を意識して飲んでいる', badgeText: '温活良好', elements: { earth: 20 }, shanghanPoints: { yangming: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 61,
    question: 'Q61. 朝起きた時に口の中が苦かったり、ねばついたり、口臭が気になりますか？',
    subtitle: '「肝胆湿熱・胃熱」体内の熱と湿気の停滞',
    options: [

      { text: '朝口の中が苦い・ねばつく・胃熱を感じる', badgeText: '肝胆湿熱・胃熱', elements: { wood: 25, fire: 25 }, shanghanPoints: { shaoyang: 3 }, xp: 0 },
      { text: '朝の口の中はさわやかで苦みやねばつきはない', badgeText: '口中爽快', elements: { wood: 20 }, shanghanPoints: { taiyang: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
  {
    id: 62,
    question: 'Q62. 足腰の冷え・下半身のむくみ・夜間の尿意が気になりますか？',
    subtitle: '「腎は水を司る」生命エネルギーと下半身の冷え',
    options: [

      { text: '足先や腰が冷えてむくみやすく、夜トイレに起きることがある', badgeText: '腎陽虚・下半身冷え', elements: { water: 35 }, shanghanPoints: { shaoyin: 3 }, xp: 0 },
      { text: '足腰は温かくむくみや夜間尿も気にならない', badgeText: '腎気充実', elements: { water: 20 }, shanghanPoints: { shaoyin: 1 }, xp: 0 },
      { text: 'その他・どちらにも当てはまらない', badgeText: 'その他・平穏', elements: { earth: 15 }, shanghanPoints: { taiyang: 1 }, xp: 10 },
    ]
  },
];

export const ORGAN_CLOCK_SLOTS: OrganClockSlot[] = [
 {
 timeRange: '03:00 - 05:00',
 startHour: 3,
 endHour: 5,
 organKanji: '肺',
 organName: '肺経 (はいけい)',
 meridian: '手太陰肺経',
 element: 'metal',
 actionAdvice: '全身へ気を届ける時間。深い腹式呼吸でフレッシュな天の気を取り入れましょう。',
 avoidAdvice: '冷やしすぎやタバコの煙などの刺激は避けて。',
 emoji: '️',
 },
 {
 timeRange: '05:00 - 07:00',
 startHour: 5,
 endHour: 7,
 organKanji: '大腸',
 organName: '大腸経 (だいちょうけい)',
 meridian: '手陽明大腸経',
 element: 'metal',
 actionAdvice: 'デトックスタイム！朝起きたら温かい白湯を1杯飲んで腸を優しく刺激しましょう。',
 avoidAdvice: '二度寝をしすぎず、排便のタイミングを逃さないこと。',
 emoji: '',
 },
 {
 timeRange: '07:00 - 09:00',
 startHour: 7,
 endHour: 9,
 organKanji: '胃',
 organName: '胃経 (いけい)',
 meridian: '足陽明胃経',
 element: 'earth',
 actionAdvice: '消化ボイラー絶好調！一番しっかり栄養を吸収できる時間。温かい朝食を召し上がれ。',
 avoidAdvice: '朝食抜きや冷たいスムージー単体は消化の火を消します。',
 emoji: '',
 },
 {
 timeRange: '09:00 - 11:00',
 startHour: 9,
 endHour: 11,
 organKanji: '脾',
 organName: '脾経 (ひけい)',
 meridian: '足太陰脾経',
 element: 'earth',
 actionAdvice: '食べたものを『気・血』に変換中！頭脳労働や集中した作業に最も適したゴールデンタイム。',
 avoidAdvice: '間食のダラダラ食いは脾を疲れさせます。',
 emoji: '',
 },
 {
 timeRange: '11:00 - 13:00',
 startHour: 11,
 endHour: 13,
 organKanji: '心',
 organName: '心経 (しんけい)',
 meridian: '手少陰心経',
 element: 'fire',
 actionAdvice: '血流とメンタルの中枢。昼食後は15分ほどの「目を閉じるプチ休息」で心を労わろう。',
 avoidAdvice: '激しい運動や怒りの感情は心の火を暴走させます。',
 emoji: '️',
 },
 {
 timeRange: '13:00 - 15:00',
 startHour: 13,
 endHour: 15,
 organKanji: '小腸',
 organName: '小腸経 (しょうちょうけい)',
 meridian: '手太陽小腸経',
 element: 'fire',
 actionAdvice: '清濁の分別（必要な栄養と不要なものを仕分ける）。こまめな水分補給が吉。',
 avoidAdvice: '冷たい飲み物の一気飲みはNG。',
 emoji: '',
 },
 {
 timeRange: '15:00 - 17:00',
 startHour: 15,
 endHour: 17,
 organKanji: '膀胱',
 organName: '膀胱経 (ぼうこうけい)',
 meridian: '足太陽膀胱経',
 element: 'water',
 actionAdvice: '代謝が高まる夕方のピーク！軽い経絡ストレッチやウォーキング、ツボ押しに最適。',
 avoidAdvice: '長時間の座りっぱなしで背中を固めないように注意。',
 emoji: '',
 },
 {
 timeRange: '17:00 - 19:00',
 startHour: 17,
 endHour: 19,
 organKanji: '腎',
 organName: '腎経 (じんけい)',
 meridian: '足少陰腎経',
 element: 'water',
 actionAdvice: '生命力を蓄える時間。温かい夕食と出汁スープで1日の疲労をリセット。足湯も効果的！',
 avoidAdvice: '過度な残業や体を冷やす環境は腎精を削ります。',
 emoji: '',
 },
 {
 timeRange: '19:00 - 21:00',
 startHour: 19,
 endHour: 21,
 organKanji: '心包',
 organName: '心包経 (しんぽうけい)',
 meridian: '手厥陰心包経',
 element: 'fire',
 actionAdvice: '心を包んで守る時間。家族や大切な人との会話、音楽や読書でリラックスモードへ。',
 avoidAdvice: '激しい議論やネガティブなニュースの長見は避けましょう。',
 emoji: '',
 },
 {
 timeRange: '21:00 - 23:00',
 startHour: 21,
 endHour: 23,
 organKanji: '三焦',
 organName: '三焦経 (さんしょうけい)',
 meridian: '手少陽三焦経',
 element: 'fire',
 actionAdvice: '全身の水と熱の通路を整える。ぬるめのお風呂で湯船に浸かり、スマホを置いておやすみ準備。',
 avoidAdvice: '深夜の夜食や強いブルーライト照射は避けて。',
 emoji: '',
 },
 {
 timeRange: '23:00 - 01:00',
 startHour: 23,
 endHour: 1,
 organKanji: '胆',
 organName: '胆経 (たんけい)',
 meridian: '足少陽胆経',
 element: 'wood',
 actionAdvice: '陰から陽への切り替えポイント！黄帝内経では『23時までの就寝』が健康の絶対条件。',
 avoidAdvice: '夜更かし！胆の細胞修復チャンスを奪ってしまいます。',
 emoji: '',
 },
 {
 timeRange: '01:00 - 03:00',
 startHour: 1,
 endHour: 3,
 organKanji: '肝',
 organName: '肝経 (かんけい)',
 meridian: '足厥陰肝経',
 element: 'wood',
 actionAdvice: '血液の解毒と浄化中。熟睡することで、翌朝の澄んだ目と軽い身体が作られます。',
 avoidAdvice: 'この時間帯の起きてアルコール摂取や作業は厳禁。',
 emoji: '',
 },
];

export const YOUTUBE_VIDEOS: YouTubeVideo[] = [
 {
 id: 'yt-qigong-1',
 youtubeId: 'sJ9XThB5uJ4', // Embedded sample working YouTube video ID for Baduanjin Qigong
 title: '【毎朝3分】初心者向け 八段錦（気功）で自律神経と五行を調える',
 category: 'qigong',
 targetElement: 'wood',
 duration: '03:45',
 description: '中国古代から伝わる伝統気功「八段錦」。胸を開き、脇腹を伸ばして肝と自律神経の気を健やかに巡らせます。',
 thumbnailUrl: 'https://img.youtube.com/vi/sJ9XThB5uJ4/hqdefault.jpg',
 tags: ['気功', '八段錦', '自律神経', '朝の習慣'],
 },
 {
 id: 'yt-stretch-1',
 youtubeId: '1z80v7zN0fA',
 title: '【経絡ストレッチ】12経絡を伸ばして冷え・むくみを劇的改善',
 category: 'exercise',
 targetElement: 'water',
 duration: '06:20',
 description: '腎経と膀胱経を中心に、体の背面と足をじっくり伸ばす東洋医学ストレッチ。冷え症や腰のだるさに最適です。',
 thumbnailUrl: 'https://img.youtube.com/vi/1z80v7zN0fA/hqdefault.jpg',
 tags: ['経絡ストレッチ', '腎経', '冷え性改善', '夜のケア'],
 },
 {
 id: 'yt-acupoint-1',
 youtubeId: 'S-7m1a4m_R8',
 title: '【万能のツボ】足三里＆太衝押しで胃腸活性化＆ストレス撃退',
 category: 'acupoint',
 targetElement: 'earth',
 duration: '04:15',
 description: '黄帝内経でも称賛される足三里（脾胃）と太衝（肝気）のセルフツボ押し。手軽にオフィスやベッドの上で実践できます。',
 thumbnailUrl: 'https://img.youtube.com/vi/S-7m1a4m_R8/hqdefault.jpg',
 tags: ['ツボ押し', '足三里', '太衝', '胃腸ケア'],
 },
 {
 id: 'yt-recipe-1',
 youtubeId: 'R9V2U2Ym3eY',
 title: '【薬なし食養生】生姜と長ネギの温活ポカポカ味噌スープ',
 category: 'recipe',
 targetElement: 'metal',
 duration: '05:30',
 description: '身近な食材だけで作る無薬膳スープ。生姜の温性と長ネギの発散パワーで肌バリアと肺の気を強化します。',
 thumbnailUrl: 'https://img.youtube.com/vi/R9V2U2Ym3eY/hqdefault.jpg',
 tags: ['薬膳レシピ', '温活', '生姜', '肺バリア'],
 },
 {
 id: 'yt-recipe-2',
 youtubeId: 'w29pC2E8sDg',
 title: '【黒の滋養】黒胡麻と山芋のほっこり美肌お粥（腎精補給）',
 category: 'recipe',
 targetElement: 'water',
 duration: '04:50',
 description: '黒胡麻、黒豆、山芋を使った腎（生命力）を養う伝統のお粥。疲れた胃腸を休め、身体の深部を温めます。',
 thumbnailUrl: 'https://img.youtube.com/vi/w29pC2E8sDg/hqdefault.jpg',
 tags: ['黒い食材', 'お粥', '補腎', 'エイジングケア'],
 },
 {
 id: 'yt-recipe-3',
 youtubeId: 'V9P08kQ9dCw',
 title: '【理気・すっきり】クコの実とナツメの自家製リラックスハーブティー',
 category: 'recipe',
 targetElement: 'fire',
 duration: '03:10',
 description: 'クコの実とナツメ、菊花を入れたカフェインフリーの養生茶。心火を落ち着かせ、目の疲労と安眠をサポート。',
 thumbnailUrl: 'https://img.youtube.com/vi/V9P08kQ9dCw/hqdefault.jpg',
 tags: ['養生茶', 'クコの実', 'ナツメ', '安眠'],
 },
];

export const INITIAL_DAILY_QUESTS: DailyQuest[] = [
 {
 id: 'quest-1',
 title: '朝一番の白湯（あたたかいお水）を一杯飲む',
 description: '胃腸のボイラー（脾胃）を温めて1日の代謝をスムーズにスタート！',
 xpReward: 30,
 completed: false,
 category: 'diet',
 iconName: 'Coffee',
 },
 {
 id: 'quest-2',
 title: 'ツボ「足三里」または「太衝」を30秒間マッサージ',
 description: '痛気持ちいい強さでじっくり刺激し、気・血の巡りを整える。',
 xpReward: 30,
 completed: false,
 category: 'exercise',
 iconName: 'Sparkles',
 },
 {
 id: 'quest-3',
 title: '経絡ストレッチまたは気功（八段錦）動画を1本実践',
 description: '動画を見ながら伸びやかに全身の経絡をほぐす。',
 xpReward: 50,
 completed: false,
 category: 'exercise',
 iconName: 'Activity',
 },
 {
 id: 'quest-4',
 title: '夜23時までにベッドに入りデジタルデトックス',
 description: '黄帝内経の黄金律！「23時からの胆経タイム」で細胞修復と明日への充電。',
 xpReward: 40,
 completed: false,
 category: 'sleep',
 iconName: 'Moon',
 },
];

export const INITIAL_BADGES: Badge[] = [
 {
 id: 'badge-1',
 name: '養生見習い',
 description: '東洋養生ナビの第一歩を踏み出した証！',
 icon: '',
 unlocked: true,
 requiredLevel: 1,
 },
 {
 id: 'badge-2',
 name: '白湯マスター',
 description: '朝の白湯習慣でお腹のボイラーを温めた証！',
 icon: '',
 unlocked: false,
 requiredLevel: 2,
 },
 {
 id: 'badge-3',
 name: '五行の調律師',
 description: '木火土金水のバランスチェックをマスターした証！',
 icon: '️',
 unlocked: false,
 requiredLevel: 3,
 },
 {
 id: 'badge-4',
 name: '傷寒論の智者',
 description: '自身の傷寒論体質を知り適切な食養生を実践した証！',
 icon: '',
 unlocked: false,
 requiredLevel: 4,
 },
 {
 id: 'badge-5',
 name: '黄帝内経の達人',
 description: '子午流注の24時間リズムを制した現代の神農氏！',
 icon: '',
 unlocked: false,
 requiredLevel: 5,
 },
];

export const FORTUNES: Omit<import('../types').FortuneResult, 'rarity'>[] = [
 {
 title: '『黄帝内経・素問』上古天真論より',
 neijingQuote: '「食飲に節あり、起居に常あり、妄りに作労せず」',
 quoteTranslation: '「暴飲暴食を避け、決まったリズムで暮らし、無理な徹夜や過労を控えることが健康の極意である」',
 luckyFood: '温かいお味噌汁 ＆ 生姜',
 luckyTime: '07:00 - 09:00 (胃経タイム)',
 luckyAcupoint: '足三里 (あしさんり)',
 xpBonus: 100,
 },
 {
 title: '『黄帝内経・素問』四気調神大論より',
 neijingQuote: '「聖人は未病を治し、已病を治さず」',
 quoteTranslation: '「名医は病気になってから治すのではなく、病気になる前の『未病』の段階で養生し防ぐ」',
 luckyFood: '黒胡麻または黒豆スープ',
 luckyTime: '17:00 - 19:00 (腎経タイム)',
 luckyAcupoint: '湧泉 (ゆうせん)',
 xpBonus: 80,
 },
 {
 title: '『傷寒論』辨太陽病脈証並治より',
 neijingQuote: '「桂枝湯、温覆して時間を置き、微かに汗出でむとす」',
 quoteTranslation: '「体を温めてほんのり汗ばむ程度に発散させることで、邪気を追い払い元気を回復させる」',
 luckyFood: '長ネギとクコの実の薬膳スープ',
 luckyTime: '05:00 - 07:00 (大腸デトックス)',
 luckyAcupoint: '合谷 (ごうこく)',
 xpBonus: 90,
 },
 {
 title: '『黄帝内経・素問』陰陽応象大論より',
 neijingQuote: '「春養肝、夏養心、秋養肺、冬養腎」',
 quoteTranslation: '「季節の移り変わりに合わせて五臓（肝・心・脾・肺・腎）を愛しむことこそ天人合一の道」',
 luckyFood: '三つ葉と柑橘香る和え物',
 luckyTime: '11:00 - 13:00 (心経リラックス)',
 luckyAcupoint: '太衝 (たいしょう)',
 xpBonus: 100,
 },
];



// ==========================================
// File: src/index.css
// ==========================================
@import "tailwindcss";



// ==========================================
// File: src/main.tsx
// ==========================================
import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

