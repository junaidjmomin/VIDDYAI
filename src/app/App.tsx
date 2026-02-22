import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { StarBackground } from './components/StarBackground';
import { ViddyAvatar } from './components/ViddyAvatar';
import { ThemeToggle } from './components/ThemeToggle';
import { GlassCard, Button, Input, cn } from './components/UIComponents';
import {
  Rocket,
  BookOpen,
  Calculator,
  FlaskConical,
  Languages,
  Globe,
  Star,
  ChevronRight,
  Upload,
  Send,
  ArrowLeft,
  CheckCircle2,
  Brain,
  Search,
  Settings,
  ShieldCheck,
  ThumbsUp,
  ThumbsDown,
  Layout,
  Download,
  PlayCircle,
  Mic,
  MicOff,
  Volume2,
  VolumeX
} from 'lucide-react';
import { Toaster, toast } from 'sonner';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';
import { ImageWithFallback } from './components/figma/ImageWithFallback';
import { useAppStore, type Subject } from '../store/useAppStore';
import api from '../api/client';

// --- Types ---
type Screen = 'welcome' | 'game' | 'upload' | 'chat';

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: string;
  thoughtExpanded?: boolean;
  agentSteps?: { agent: string; action: string }[];
  safety_verified?: boolean;
}

const SUBJECTS: { id: Subject; name: string; icon: any; color: string; gradient: string }[] = [
  { id: 'Math', name: 'Math', icon: Calculator, color: '#8B5CF6', gradient: 'from-[#1E1040] to-[#2D1B69]' },
  { id: 'Science', name: 'Science/EVS', icon: FlaskConical, color: '#06B6D4', gradient: 'from-[#0C1E2E] to-[#0E4A5C]' },
  { id: 'English', name: 'English', icon: BookOpen, color: '#F59E0B', gradient: 'from-[#2D1B10] to-[#4A2D0E]' },
  { id: 'Hindi', name: 'Hindi', icon: Languages, color: '#F43F5E', gradient: 'from-[#2D101E] to-[#4A0E1E]' },
  { id: 'GK', name: 'General Knowledge', icon: Globe, color: '#10B981', gradient: 'from-[#102D1E] to-[#0E4A2E]' },
];

const MOCK_CHART_DATA = [
  { name: 'Mon', score: 65 },
  { name: 'Tue', score: 72 },
  { name: 'Wed', score: 68 },
  { name: 'Thu', score: 85 },
  { name: 'Fri', score: 82 },
  { name: 'Sat', score: 92 },
];



// --- Main App Component ---
export default function App() {
  const {
    student,
    currentScreen,
    setCurrentScreen,
    theme
  } = useAppStore();

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [showConfetti, setShowConfetti] = useState(false);

  // Real Data State
  const [videoData, setVideoData] = useState<any>(null); // To store YouTube result
  const [visuals, setVisuals] = useState<any[]>([]); // To store PPT download links

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Derived subject
  const subject = student?.subject || 'Science';

  const fetchRelatedMedia = async (topic: string) => {
    try {
      // 1. Search Video
      const video = await api.searchVideos(
  topic,
  student?.grade || 3,
  subject,
  student?.iq_scores?.[subject] || 50,
student?.eq_scores?.[subject] || 50
);
      if (video.success) {
        setVideoData(video);
      } else {
        setVideoData(null);
      }

      // 2. Setup placeholders for PPTs
      setVisuals([
        { id: 1, title: `${topic} Basics`, ready: false },
        { id: 2, title: `${topic} Advanced`, ready: false }
      ]);
    } catch (e) {
      console.error("Media fetch failed", e);
    }
  };

const handleGeneratePPT = async (visualIndex: number) => {
  if (!student) return;

  const topic = visuals[visualIndex].title;

  const toastId = toast.loading("Generating your presentation...");

  try {
    const response = await api.generatePPT(
      topic,
      student.grade,
      subject,
      [
        `Introduction to ${topic}`,
        `Key concepts of ${topic}`,
        `Examples of ${topic}`,
        `Summary of ${topic}`
      ]
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText);
    }

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${topic.replace(/\s+/g, "_")}.pptx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    toast.success("Presentation downloaded successfully! 🚀", { id: toastId });

  } catch (error) {
    console.error("PPT generation failed:", error);
    toast.error("Generation failed. Please try again.", { id: toastId });
  }
};
  // Fetch relevant media when subject changes or on load
  useEffect(() => {
    if (currentScreen === 'chat' && subject) {
      fetchRelatedMedia(subject);
    }
  }, [currentScreen, subject]);

  const [userName, setUserName] = useState('');
  const [selectedGrade, setSelectedGrade] = useState(3);
  const [selectedSubject, setSelectedSubject] = useState<Subject>('Math');

  // Initialize theme on mount
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.classList.toggle('light', theme === 'light');
  }, [theme]);

  return (
    <StarBackground>
      <ThemeToggle />
      <Toaster position="top-center" />
      <AnimatePresence mode="wait">
        {currentScreen === 'welcome' && (
          <WelcomeScreen
            key="welcome"
            userName={userName}
            setUserName={setUserName}
            selectedGrade={selectedGrade}
            setSelectedGrade={setSelectedGrade}
            selectedSubject={selectedSubject}
            setSelectedSubject={setSelectedSubject}
            onStart={() => setCurrentScreen('game')}
          />
        )}
        {currentScreen === 'game' && (
          <GameScreen
            key="game"
            subject={selectedSubject}
            onComplete={() => setCurrentScreen('upload')}
            onBack={() => setCurrentScreen('welcome')}
          />
        )}
        {currentScreen === 'upload' && (
          <UploadScreen
            key="upload"
            subject={selectedSubject}
            onComplete={() => setCurrentScreen('chat')}
            onBack={() => setCurrentScreen('game')}
          />
        )}
        {currentScreen === 'chat' && (
          <ChatScreen
            key="chat"
            userName={userName}
            subject={selectedSubject}
            visuals={visuals}
            videoData={videoData}
            onGeneratePPT={handleGeneratePPT}
            onFetchMedia={fetchRelatedMedia}
            onBack={() => setCurrentScreen('upload')}
          />
        )}
      </AnimatePresence>
    </StarBackground>
  );
}

// --- Screens ---

function WelcomeScreen({ userName, setUserName, selectedGrade, setSelectedGrade, selectedSubject, setSelectedSubject, onStart }: any) {
  const { student, setStudent, setIsLoading, setCurrentScreen } = useAppStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleStart = async () => {
    if (!userName.trim()) {
      toast.error('Please enter your name!');
      return;
    }

    setIsSubmitting(true);
    setIsLoading(true);

    try {
      const response = await api.login({
        name: userName,
        grade: selectedGrade,
        subject: selectedSubject
      });

      if (response.success) {
        setStudent(response.profile);
        toast.success(`Welcome aboard, ${userName}! 🚀`);
        onStart();
      }
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Failed to start. Please try again!');
    } finally {
      setIsSubmitting(false);
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex min-h-screen items-center justify-center p-6"
    >
      <GlassCard className="w-full max-w-[520px] p-8 md:p-12 text-center">
        <div className="flex justify-center mb-6">
          <ViddyAvatar size={96} />
        </div>

        <h1 className="font-nunito text-4xl font-bold text-foreground mb-2 tracking-tight">
          VIDYASETU AI
        </h1>
        <p className="text-muted-foreground text-lg mb-8 font-inter">
          Your Cosmic Learning Companion
        </p>

        <div className="w-full h-px bg-border mb-8" />

        <div className="space-y-6">
          <Input
            icon={Rocket}
            placeholder="What's your name, Explorer?"
            value={userName}
            onChange={(e: any) => setUserName(e.target.value)}
          />

          <div className="space-y-4">
            <p className="text-primary font-inter font-medium text-sm tracking-widest uppercase">
              Choose your Grade
            </p>
            <div className="flex justify-center gap-4">
              {[1, 2, 3, 4, 5].map((grade) => (
                <button
                  key={grade}
                  onClick={() => setSelectedGrade(grade)}
                  className={`w-14 h-14 rounded-full font-nunito font-bold text-xl transition-all duration-300 ${selectedGrade === grade
                    ? "bg-primary text-primary-foreground scale-110 shadow-[0_0_20px_var(--primary)] ring-2 ring-primary/50"
                    : "bg-muted text-muted-foreground hover:bg-accent"
                    }`}
                >
                  {grade}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex flex-wrap justify-center gap-3">
              {SUBJECTS.map((sub) => {
                const Icon = sub.icon;
                return (
                  <button
                    key={sub.id}
                    onClick={() => setSelectedSubject(sub.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full font-inter text-sm font-medium transition-all ${selectedSubject === sub.id
                      ? `bg-primary text-primary-foreground shadow-[0_0_15px_var(--primary)]`
                      : "bg-muted text-muted-foreground hover:bg-accent"
                      }`}
                  >
                    <Icon size={16} />
                    {sub.name}
                  </button>
                );
              })}
            </div>
          </div>

          <Button
            className="w-full mt-4 flex items-center justify-center gap-2"
            onClick={handleStart}
            disabled={!userName || isSubmitting}
          >
            {isSubmitting ? 'Starting...' : 'Begin Your Journey!'} <Star size={18} className="text-yellow-300" />
          </Button>

          {student && (
            <button
              onClick={() => setCurrentScreen('chat')}
              className="mt-4 text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Already logged in? Go to Chat →
            </button>
          )}
        </div>

        <div className="mt-8 flex items-center justify-center gap-2 text-xs text-muted-foreground">
          <ShieldCheck size={14} />
          Trusted by CBSE schools across India
        </div>
      </GlassCard>
    </motion.div>
  );
}

function GameScreen({ subject, onComplete, onBack }: any) {
  const { student, addXp } = useAppStore();
  const currentSubject = SUBJECTS.find(s => s.id === subject) || SUBJECTS[0];


  const [currentChallenge, setCurrentChallenge] = useState<any>(null);
  const [challengeCount, setChallengeCount] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [feedback, setFeedback] = useState<'correct' | 'wrong' | null>(null);
  const [startTime, setStartTime] = useState(Date.now());

  const fetchNewChallenge = async () => {
    if (!student) return;
    setIsGenerating(true);
    try {
      const types: ('iq' | 'eq' | 'concept')[] = ['iq', 'eq', 'concept'];
      const type = types[challengeCount % 3];
      const response = await api.generateDynamicChallenge(student.student_id, subject, student.grade, type);
      if (response.success) {
        setCurrentChallenge(response.challenge);
        setStartTime(Date.now());
      }
    } catch (error) {
      console.error('Failed to generate challenge:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    fetchNewChallenge();
  }, [challengeCount]);

  const handleAnswer = async (selectedOption: string) => {
    if (!currentChallenge || feedback) return;

    const isCorrect = selectedOption === currentChallenge.correct;

    if (isCorrect) {
      setFeedback('correct');
      const timeTaken = (Date.now() - startTime) / 1000;

      // Submit game result to backend
      if (student) {
        try {
          const response = await api.submitGameResult({
            student_id: student.student_id,
            game_type: currentChallenge.trait || 'dynamic',
            score: 100,
            time_taken: timeTaken,
            is_dynamic: true
          });

          addXp(response.xp_earned || 15);
          toast.success(`+${response.xp_earned || 15} XP Earned! ⭐`);
        } catch (error) {
          console.error('Failed to submit game result:', error);
          addXp(15);
          toast.success(`+15 XP Earned! ⭐`);
        }
      }

      setTimeout(() => {
        setFeedback(null);
        if (challengeCount < 2) { // 3 rounds total
          setChallengeCount((prev: number) => prev + 1);
        } else {
          onComplete();
        }
      }, 1500);
    } else {
      setFeedback('wrong');
      setTimeout(() => setFeedback(null), 1000);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col min-h-screen p-8"
    >
      <header className="flex items-center justify-between mb-12">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 -ml-2 text-muted-foreground hover:text-foreground transition-all duration-200 hover:scale-110 active:scale-90 flex items-center justify-center rounded-full hover:bg-white/5"
            title="Go Back"
          >
            <ArrowLeft size={28} />
          </button>
          <h2 className="font-nunito text-2xl font-bold">Adventure Zone</h2>
        </div>

        <div className="flex items-center gap-8">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-green-500 shadow-[0_0_15px_rgba(34,197,94,0.4)] flex items-center justify-center">
              <CheckCircle2 size={20} className="text-card-foreground" />
            </div>
            <div className="w-8 h-px bg-border" />
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-12 h-12 rounded-full ring-4 ring-primary/20 flex items-center justify-center"
              style={{ backgroundColor: currentSubject.color }}
            >
              {currentSubject.icon && <currentSubject.icon size={24} className="text-card-foreground" />}
            </motion.div>
            <div className="w-8 h-px bg-border" />
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
              <Star size={20} className="text-muted-foreground" />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <button
              onClick={onComplete}
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center gap-1"
            >
              Skip to Upload <ChevronRight size={16} />
            </button>

            <div className="flex items-center gap-2 bg-yellow-500/10 px-4 py-2 rounded-full border border-yellow-500/20">
              <Star size={18} className="text-yellow-500" fill="#EAB308" />
              <span className="font-nunito font-bold text-yellow-500 text-xl">{student?.xp || 1240}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex flex-col items-center justify-center">
        <div className="w-full max-w-[640px]">
          <motion.div
            className="bg-card rounded-[28px] overflow-hidden shadow-2xl"
            animate={feedback === 'wrong' ? { x: [-10, 10, -10, 10, 0] } : {}}
          >
            <div className={`h-20 bg-linear-to-r ${currentSubject.gradient} flex items-center px-8`}>
              <h3 className="font-nunito text-2xl font-bold text-card-foreground flex items-center gap-3">
                <currentSubject.icon size={28} />
                {currentSubject.name} Game
              </h3>
            </div>

            <div className="p-12 text-center min-h-[400px] flex flex-col justify-center">
              {isGenerating || !currentChallenge ? (
                <div className="space-y-6">
                  <motion.div
                    animate={{ scale: [1, 1.1, 1], rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-24 h-24 rounded-full border-4 border-primary/20 border-t-primary mx-auto"
                  />
                  <p className="font-nunito text-xl font-bold text-muted-foreground animate-pulse">Viddy is thinking of a challenge...</p>
                </div>
              ) : (
                <>
                  <h4 className="font-nunito text-2xl font-bold mb-12 text-card-foreground">
                    {currentChallenge.question}
                  </h4>

                  <div className="flex justify-center items-center gap-8 mb-12">
                    <motion.div
                      animate={{ rotate: [0, 5, -5, 0], scale: [1, 1.05, 1] }}
                      transition={{ duration: 4, repeat: Infinity }}
                      className={`w-32 h-32 rounded-3xl bg-linear-to-br ${currentSubject.gradient} flex items-center justify-center border-2 border-white/20 shadow-2xl relative group`}
                    >
                      <div className="absolute inset-0 bg-white/10 blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                      <Star size={64} className="text-card-foreground" />
                    </motion.div>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    {currentChallenge.options?.map((option: string, i: number) => (
                      <button
                        key={i}
                        onClick={() => handleAnswer(option)}
                        disabled={!!feedback}
                        className={cn(
                          "h-24 rounded-2xl bg-card border-2 border-border flex items-center justify-center transition-all hover:border-ring/40 hover:bg-popover/5 active:scale-95 group relative px-6",
                          feedback === 'correct' && option === currentChallenge.correct && "border-green-500 bg-green-500/10",
                          feedback === 'wrong' && option !== currentChallenge.correct && "border-red-500 bg-red-500/10"
                        )}
                      >
                        <span className="font-nunito font-bold text-xl text-foreground">{option}</span>

                        {feedback === 'correct' && option === currentChallenge.correct && (
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="absolute inset-0 flex items-center justify-center bg-green-500/20 rounded-2xl"
                          >
                            <CheckCircle2 size={48} className="text-green-500" />
                          </motion.div>
                        )}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </motion.div>

          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 text-center"
            >
              <p className="font-nunito font-bold text-2xl text-[#F59E0B]">
                Excellent Explorer! 🚀
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </motion.div >
  );
}

function UploadScreen({ subject, onComplete, onBack }: any) {
  const { student, isUploading, setIsUploading, uploadProgress, setUploadProgress } = useAppStore();
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [chunksIndexed, setChunksIndexed] = useState(0);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const currentSubject = SUBJECTS.find(s => s.id === subject) || SUBJECTS[0];

  const handleFileUpload = async (file: File) => {
    if (!student) {
      toast.error('Student profile not found!');
      return;
    }

    if (file.type !== 'application/pdf') {
      toast.error('Please upload a PDF file');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev: number) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 5;
        });
      }, 200);

      const response = await api.uploadTextbook(file, student.student_id, subject, student.grade);

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadComplete(true);
      setChunksIndexed(response.chunks_indexed);

      toast.success(`${response.chunks_indexed} knowledge chunks indexed successfully! 📚`);

      setTimeout(() => {
        onComplete();
      }, 2000);
    } catch (error: any) {
      console.error('Upload failed:', error);
      toast.error(error.message || 'Upload failed. Please try again!');
      setUploadProgress(0);
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex min-h-screen items-center justify-center p-12"
    >
      <div className="grid md:grid-cols-2 gap-16 max-w-6xl w-full">
        <div className="space-y-8">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 -ml-2 rounded-full hover:bg-white/5 text-muted-foreground transition-all duration-200 hover:scale-110 active:scale-90 flex items-center justify-center"
              title="Go Back"
            >
              <ArrowLeft size={28} />
            </button>
            <div>
              <h2 className="font-nunito text-4xl font-bold text-foreground mb-2">Upload Your Textbook</h2>
              <p className="text-muted-foreground text-xl">Viddy will read every page for you 📚</p>
            </div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />

          <div
            onClick={() => !isUploading && fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            className={cn(
              "h-[400px] border-2 border-dashed rounded-[32px] flex flex-col items-center justify-center p-8 transition-all",
              isUploading ? "border-primary bg-primary/10 cursor-default" : "border-primary/40 bg-primary/5 hover:bg-primary/10 hover:border-primary cursor-pointer",
              isDragOver && "border-primary bg-primary/20"
            )}
          >
            {isUploading ? (
              <div className="w-full text-center space-y-8">
                <motion.div
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="mx-auto w-24 h-24 rounded-full border-4 border-primary/20 border-t-primary flex items-center justify-center"
                />
                <div className="space-y-4">
                  <p className="font-nunito font-bold text-2xl text-foreground">Reading your book...</p>
                  <p className="text-muted-foreground">Page {Math.floor(uploadProgress * 2)} of 200</p>
                  <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-primary to-primary/70"
                      initial={{ width: 0 }}
                      animate={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : uploadComplete ? (
              <div className="text-center space-y-6">
                <CheckCircle2 size={80} className="text-green-500 mx-auto" />
                <h3 className="font-nunito text-3xl font-bold text-green-500">Your book is ready!</h3>
                <p className="text-muted-foreground">{chunksIndexed || 247} knowledge stars indexed</p>
              </div>
            ) : (
              <div className="text-center space-y-6">
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 10 }}
                  className="mx-auto"
                >
                  <Upload size={80} className="text-primary" />
                </motion.div>
                <div className="space-y-2">
                  <h3 className="font-nunito text-2xl font-bold text-foreground">Drop your PDF here</h3>
                  <p className="text-muted-foreground font-inter">or click to browse</p>
                </div>
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">
                  Supports CBSE textbooks up to 50MB
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col items-center justify-center space-y-8">
          <motion.div
            animate={{ y: [0, -20, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className={`w-[240px] h-[240px] rounded-full bg-linear-to-br ${currentSubject.gradient} shadow-[0_0_60px_rgba(0,0,0,0.5)] flex items-center justify-center relative group`}
          >
            <div className="absolute inset-0 rounded-full bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity blur-xl" />
            <currentSubject.icon size={100} className="text-card-foreground" />
            <div className="absolute -bottom-4 right-0 bg-[#FCD34D] text-[#0A0E1A] font-nunito font-black px-6 py-2 rounded-full shadow-lg transform rotate-12">
              Grade {3}
            </div>
          </motion.div>

          <div className="text-center space-y-4">
            <h3 className="font-nunito text-4xl font-bold text-foreground">{currentSubject.name} Planet</h3>
            <div className="space-y-3">
              {['Smart Concept Summaries', 'Visual Star Maps', 'AI Practice Quizzes'].map((point, i) => (
                <div key={i} className="flex items-center gap-3 text-[#94A3B8] text-lg">
                  <Star size={16} className="text-[#FCD34D]" fill="#FCD34D" />
                  {point}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div >
  );
}

function ChatScreen({ userName, subject, visuals, videoData, onGeneratePPT, onFetchMedia, onBack }: any) {
  const { student, messages, addMessage, toggleThought, setCurrentScreen } = useAppStore();
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const recognitionRef = React.useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  // Add initial welcome message
  useEffect(() => {
    if (messages.length === 0) {
      addMessage({
        id: Date.now().toString(),
        role: 'ai',
        content: `Hello ${userName}! I've finished scanning your textbook. I'm ready to help you explore the galaxy of ${subject}. What mission should we start today?`,
        timestamp: new Date().toISOString(),
        thoughtExpanded: false,
        safety_verified: true
      });
    }
  }, []);

  const handleFeedback = async (messageId: string, feedbackType: 'thumbs_up' | 'thumbs_down') => {
    if (!student) return;

    try {
      await api.logFeedback({
        student_id: student.student_id,
        message_id: messageId,
        feedback_type: feedbackType,
        timestamp: new Date().toISOString()
      });

      toast.success(feedbackType === 'thumbs_up' ? 'Thanks for the feedback! 👍' : 'Feedback recorded. I\'ll improve!');
    } catch (error) {
      console.error('Failed to log feedback:', error);
    }
  };

  const audioRef = React.useRef<HTMLAudioElement | null>(null);

  const handleSpeak = async (messageId: string, text: string) => {
    // If already speaking this message → stop
    if (speakingMessageId === messageId && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setSpeakingMessageId(null);
      return;
    }

    // Stop any previous speech
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    setSpeakingMessageId(messageId);

    try {
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiBase}/api/tts/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error(`TTS failed: ${res.status}`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setSpeakingMessageId(null);
        audioRef.current = null;
        URL.revokeObjectURL(url);
      };

      audio.onerror = () => {
        toast.error('Failed to play audio.');
        setSpeakingMessageId(null);
        audioRef.current = null;
      };

      await audio.play();
    } catch (error: any) {
      console.error('TTS Error:', error);
      toast.error('Text-to-speech failed.');
      setSpeakingMessageId(null);
    }
  };

  const handleMicClick = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      toast.error('Microphone not supported in this browser.');
      return;
    }

    // If already recording → stop
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      toast.error('Microphone permission denied. Please allow mic access.');
      return;
    }

    const chunks: BlobPart[] = [];
    const mediaRecorder = new MediaRecorder(stream);
    recognitionRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstart = () => setIsListening(true);

    mediaRecorder.onstop = async () => {
      setIsListening(false);
      stream.getTracks().forEach((t) => t.stop());

      const audioBlob = new Blob(chunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const toastId = toast.loading('Transcribing…');
      try {
        const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiBase}/api/stt/transcribe`, {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Server error ${res.status}`);
        }

        const { transcript } = await res.json();
        if (transcript) {
          setInputValue((prev) => (prev ? prev + ' ' + transcript : transcript));
          toast.success('Done!', { id: toastId });
        } else {
          toast.warning('No speech detected. Please try again.', { id: toastId });
        }
      } catch (err: any) {
        toast.error(err.message || 'Transcription failed.', { id: toastId });
      }
    };

    // Auto-stop after 30 seconds to prevent runaway recordings
    mediaRecorder.start();
    setTimeout(() => {
      if (mediaRecorder.state === 'recording') mediaRecorder.stop();
    }, 30_000);
  };

  const handleSend = async () => {
    if (!inputValue.trim() || !student || isStreaming) return;

    const query = inputValue.trim();
    setInputValue('');

    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user' as const,
      content: query,
      timestamp: new Date().toISOString()
    };
    addMessage(userMessage);

    // Start streaming AI response
    setIsStreaming(true);
    setCurrentStreamingMessage('');

    try {
      const eventSource = api.createChatStream(query, student.student_id);

      let fullResponse = '';
      let messageId = '';
      let agentSteps: any[] = [];

      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          eventSource.close();
          setIsStreaming(false);
          return;
        }

        try {
          const data = JSON.parse(event.data);

          if (data.agent) {
            // Agent step update (e.g. status: "thinking" or "done")
            const agentName = data.agent.charAt(0).toUpperCase() + data.agent.slice(1);

            // If it's the result of an agent, we show its interim output
            if (data.status === 'done' && data.text) {
              fullResponse = data.text;
              setCurrentStreamingMessage(fullResponse);
            }

            agentSteps.push({
              agent: agentName + ' Agent',
              action: data.text || (data.status === 'thinking' ? `Thinking...` : 'Finished step')
            });
          } else if (data.final) {
            // Final complete message from council (data.final, data.query_id)
            fullResponse = data.final;
            const finalQueryId = data.query_id || `q_${Date.now()}`;

            addMessage({
              id: finalQueryId,
              role: 'ai',
              content: fullResponse,
              timestamp: new Date().toISOString(),
              thoughtExpanded: false,
              agentSteps: [...agentSteps],
              safety_verified: data.safety_verified
            });

            setCurrentStreamingMessage('');
            setIsStreaming(false);
            eventSource.close();

            // Trigger media fetch based on the answer topic (simple extraction for now)
            // Ideally, the backend would return "related_topics" in the final payload
            if (messages.length > 0) {
              // Just refresh media for the current subject context to keep it relevant
              onFetchMedia(subject);
            }
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        toast.error('Connection lost. Please try again.');
        setIsStreaming(false);
        setCurrentStreamingMessage('');
        eventSource.close();
      };

    } catch (error) {
      console.error('Failed to start chat stream:', error);
      toast.error('Failed to send message. Please try again!');
      setIsStreaming(false);
      setCurrentStreamingMessage('');
    }
  };

  return (
    <div className="flex flex-1 w-full overflow-hidden">
      {/* Sidebar Left */}
      <div className="w-[300px] border-r border-border bg-card flex flex-col p-6 space-y-8">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-primary flex items-center justify-center font-nunito font-bold text-2xl text-primary-foreground">
            {userName[0] || 'A'}
          </div>
          <div>
            <h3 className="font-nunito font-bold text-lg leading-tight text-foreground">{userName || 'Explorer'}</h3>
            <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Grade {student?.grade || 3} Explorer</p>
          </div>
        </div>

        <div className="space-y-4 p-4 rounded-2xl bg-accent/50 border border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Star size={18} className="text-yellow-500" fill="#EAB308" />
              <span className="font-nunito font-bold text-yellow-600 text-lg">{student?.xp || 1240} XP</span>
            </div>
            <span className="text-[10px] text-muted-foreground uppercase font-bold">Level 12</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div className="h-full w-[65%] bg-gradient-to-r from-yellow-500 to-yellow-600 shadow-[0_0_10px_rgba(234,179,8,0.3)]" />
          </div>
          <p className="text-center text-xs text-muted-foreground">Next rank: <span className="text-foreground">Star Navigator</span></p>
        </div>

        <div className="flex-1 space-y-6 overflow-y-auto">
          <div>
            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest mb-4">Current Mission</p>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-accent/50">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                <Globe size={20} className="text-cyan-400" />
              </div>
              <div>
                <p className="text-sm font-bold text-foreground">Exploring {subject}</p>
                <p className="text-[10px] text-muted-foreground">Interactive Learning</p>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-border space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-accent text-sm text-muted-foreground transition-colors">
            <Settings size={18} /> Settings
          </button>
          <button
            onClick={() => setCurrentScreen('welcome')}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-accent text-sm text-muted-foreground transition-colors"
          >
            <ArrowLeft size={18} /> Logout / Home
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative bg-background">
        <header className="h-20 border-b border-border flex items-center justify-between px-8 bg-card/50 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <div className="relative">
              <ViddyAvatar size={40} />
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-card rounded-full" />
            </div>
            <div>
              <h2 className="font-nunito font-bold text-lg text-foreground">Viddy AI 🦉</h2>
              <p className="text-xs text-green-500">● Online</p>
            </div>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-accent border border-border">
            {SUBJECTS.find(s => s.id === subject)?.icon && React.createElement(SUBJECTS.find(s => s.id === subject)!.icon, { size: 16, className: 'text-primary' })}
            <span className="text-sm font-bold text-foreground">{subject} Planet</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-8 scroll-smooth">
          {messages.map((msg, i) => (
            <div key={msg.id} className={cn("flex w-full", msg.role === 'user' ? "justify-end" : "justify-start")}>
              <div className={cn("flex gap-4 max-w-[70%]", msg.role === 'user' && "flex-row-reverse")}>
                {msg.role === 'ai' && (
                  <div className="flex-shrink-0">
                    <ViddyAvatar size={32} />
                  </div>
                )}

                <div className="space-y-3">
                  <div className={cn(
                    "p-6 rounded-3xl text-lg font-inter leading-relaxed shadow-xl",
                    msg.role === 'user'
                      ? "bg-gradient-to-br from-primary to-primary/80 text-primary-foreground rounded-tr-none"
                      : "bg-card text-foreground border border-border rounded-tl-none"
                  )}>
                    {msg.content}
                  </div>

                  {msg.role === 'ai' && (
                    <div className="space-y-2">
                      <div className="flex gap-2 flex-wrap items-center">
                        <button
                          onClick={() => handleFeedback(msg.id, 'thumbs_up')}
                          className="px-3 py-1.5 rounded-full bg-accent hover:bg-accent/80 text-xs flex items-center gap-2 text-muted-foreground transition-colors"
                        >
                          <ThumbsUp size={14} /> Helpful
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, 'thumbs_down')}
                          className="px-3 py-1.5 rounded-full bg-accent hover:bg-accent/80 text-xs flex items-center gap-2 text-muted-foreground transition-colors"
                        >
                          <ThumbsDown size={14} /> Not quite
                        </button>
                        {/* TTS speaker button */}
                        <button
                          onClick={() => handleSpeak(msg.id, msg.content)}
                          title={speakingMessageId === msg.id ? 'Stop reading' : 'Read aloud'}
                          className={cn(
                            'p-1.5 rounded-full transition-all',
                            speakingMessageId === msg.id
                              ? 'bg-primary/20 text-primary animate-pulse'
                              : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                          )}
                        >
                          {speakingMessageId === msg.id
                            ? <VolumeX size={14} />
                            : <Volume2 size={14} />}
                        </button>
                        {msg.safety_verified && (
                          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-500/10 text-[10px] font-bold text-green-500 uppercase">
                            <ShieldCheck size={12} /> Safe
                          </div>
                        )}
                      </div>

                      {msg.agentSteps && msg.agentSteps.length > 0 && (
                        <div className="rounded-2xl border border-border overflow-hidden">
                          <button
                            className="w-full px-4 py-2 bg-accent hover:bg-accent/80 flex items-center justify-between text-xs text-muted-foreground transition-colors"
                            onClick={() => toggleThought(msg.id)}
                          >
                            <span className="flex items-center gap-2">
                              <Brain size={14} className="text-purple-500" /> 🔮 See how Viddy thought
                            </span>
                            <ChevronRight size={14} className={cn("transition-transform", msg.thoughtExpanded && "rotate-90")} />
                          </button>

                          <AnimatePresence>
                            {msg.thoughtExpanded && (
                              <motion.div
                                initial={{ height: 0 }}
                                animate={{ height: 'auto' }}
                                exit={{ height: 0 }}
                                className="overflow-hidden bg-background"
                              >
                                <div className="p-4 space-y-3">
                                  {msg.agentSteps.map((step, idx) => (
                                    <div key={idx} className="pl-3 border-l-2 border-purple-500">
                                      <p className="text-[10px] font-bold text-purple-500 uppercase">{step.agent}</p>
                                      <p className="text-xs text-muted-foreground">{step.action}</p>
                                    </div>
                                  ))}
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="flex-shrink-0 pt-2">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center font-nunito font-bold text-xs text-primary-foreground">
                      {userName[0] || 'A'}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Streaming Message */}
          {isStreaming && currentStreamingMessage && (
            <div className="flex w-full justify-start">
              <div className="flex gap-4 max-w-[70%]">
                <div className="flex-shrink-0">
                  <ViddyAvatar size={32} />
                </div>
                <div className="p-6 rounded-3xl text-lg font-inter leading-relaxed shadow-xl bg-card text-foreground border border-border rounded-tl-none">
                  {currentStreamingMessage}
                  <motion.span
                    animate={{ opacity: [1, 0, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                    className="inline-block ml-1"
                  >
                    ▋
                  </motion.span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="p-8 bg-gradient-to-t from-background via-background to-transparent">
          <div className="relative max-w-4xl mx-auto">
            <Input
              placeholder={`Ask Viddy anything about your ${subject} textbook...`}
              className="pr-36 pl-8 h-16 text-lg bg-card border-border"
              value={inputValue}
              onChange={(e: any) => setInputValue(e.target.value)}
              onKeyDown={(e: any) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              disabled={isStreaming}
            />
            {/* Microphone button */}
            <button
              onClick={handleMicClick}
              disabled={isStreaming}
              title={isListening ? 'Stop listening' : 'Speak your question'}
              className={cn(
                'absolute right-[72px] top-1/2 -translate-y-1/2 w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all active:scale-95 disabled:cursor-not-allowed',
                isListening
                  ? 'bg-red-500 text-white shadow-[0_0_16px_rgba(239,68,68,0.6)] animate-pulse'
                  : 'bg-accent hover:bg-accent/70 text-muted-foreground hover:text-foreground disabled:opacity-50'
              )}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={isStreaming || !inputValue.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-primary-foreground shadow-lg active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar Right */}
      <div className="w-[300px] border-l border-border bg-card flex flex-col p-6 space-y-8">
        <div>
          <h3 className="font-nunito font-bold text-lg mb-4 flex items-center gap-2">
            <Star size={20} className="text-[#FCD34D]" fill="#FCD34D" /> Knowledge Cosmos
          </h3>
          <div className="space-y-3">
            {[
              { name: 'Evaporation', color: '#06B6D4' },
              { name: 'Condensation', color: '#8B5CF6' },
              { name: 'Precipitation', color: '#10B981' }
            ].map((concept, i) => (
              <div key={i} className="group p-3 rounded-xl bg-popover/5 border border-border hover:border-border/80 transition-all cursor-pointer">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-card-foreground"
                    style={{ background: concept.color }}
                  >
                    <Globe size={18} />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground group-hover:text-cyan-400 transition-colors">{concept.name}</p>
                    <p className="text-[10px] text-muted-foreground">Chapter 4 reference</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 space-y-4">
          <p className="text-[10px] text-[#475569] uppercase font-bold tracking-widest">Generated Visuals</p>
          <div className="grid grid-cols-2 gap-3">
            {visuals.length > 0 ? visuals.map((vis, i) => (
              <div
                key={i}
                onClick={() => onGeneratePPT(i)}
                className="aspect-video rounded-lg bg-white/5 border border-white/10 p-2 flex flex-col justify-end relative group overflow-hidden cursor-pointer hover:border-primary/50 transition-colors"
              >
                <div className="absolute inset-0 bg-linear-to-t from-black/60 to-transparent" />
                <div className="relative z-10 flex items-center justify-between">
                  <span className="text-[10px] text-muted-foreground/80 truncate max-w-[80%]">{vis.title}</span>
                  <Download size={12} className="text-muted-foreground/80" />
                </div>
                <div className="absolute inset-0 bg-[--color-primary]/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
                  <span className="text-[10px] font-bold text-white">Generate</span>
                </div>
              </div>
            )) : (
              <p className="text-xs text-muted-foreground col-span-2">Ask a question to unlock visuals!</p>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <p className="text-[10px] text-[#475569] uppercase font-bold tracking-widest">Video Explanation</p>
          <div className="aspect-video rounded-xl overflow-hidden relative group bg-black/40 border border-white/10">
            {videoData ? (
              <iframe
                src={videoData.embed_url}
                title={videoData.title}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground gap-2">
                <PlayCircle size={24} />
                <span className="text-xs">Video loading...</span>
              </div>
            )}
          </div>
          {videoData && (
            <p className="text-xs text-muted-foreground leading-tight line-clamp-2">{videoData.title}</p>
          )}
        </div>
      </div>
    </div>
  );
}
