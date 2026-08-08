'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence, type MotionProps, motion } from 'motion/react';
import {
  useAgent,
  useSessionContext,
  useSessionMessages,
} from '@livekit/components-react';

import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';

import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';

import { Shimmer } from '@/components/ai-elements/shimmer';
import { cn } from '@/lib/shadcn/utils';
import { TileLayout } from './tile-view';

const MotionMessage = motion.create(Shimmer);

const BOTTOM_VIEW_MOTION_PROPS: MotionProps = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

const CHAT_MOTION_PROPS: MotionProps = {
  variants: {
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeOut',
        duration: 0.3,
      },
    },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.2,
        ease: 'easeOut',
        duration: 0.3,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

const SHIMMER_MOTION_PROPS: MotionProps = {
  variants: {
    visible: {
      opacity: 1,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0.8,
      },
    },
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

export interface AgentSessionView_01Props {
  /**
   * Message shown above the controls before the first chat message is sent.
   *
   * @default 'Agent is listening, ask it a question'
   */
  preConnectMessage?: string;
  /**
   * Enables or disables the chat toggle and transcript input controls.
   *
   * @default true
   */
  supportsChatInput?: boolean;
  /**
   * Enables or disables camera controls in the bottom control bar.
   *
   * @default true
   */
  supportsVideoInput?: boolean;
  /**
   * Enables or disables screen sharing controls in the bottom control bar.
   *
   * @default true
   */
  supportsScreenShare?: boolean;
  /**
   * Shows a pre-connect buffer state with a shimmer message before messages appear.
   *
   * @default true
   */
  isPreConnectBufferEnabled?: boolean;

  /** Selects the visualizer style rendered in the main tile area. */
  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  /** Primary hex color used by supported audio visualizer variants. */
  audioVisualizerColor?: `#${string}`;
  /** Hue shift intensity used by certain visualizers. */
  audioVisualizerColorShift?: number;
  /** Number of bars to render when `audioVisualizerType` is `bar`. */
  audioVisualizerBarCount?: number;
  /** Number of rows in the visualizer when `audioVisualizerType` is `grid`. */
  audioVisualizerGridRowCount?: number;
  /** Number of columns in the visualizer when `audioVisualizerType` is `grid`. */
  audioVisualizerGridColumnCount?: number;
  /** Number of radial bars when `audioVisualizerType` is `radial`. */
  audioVisualizerRadialBarCount?: number;
  /** Base radius of the radial visualizer when `audioVisualizerType` is `radial`. */
  audioVisualizerRadialRadius?: number;
  /** Stroke width of the wave path when `audioVisualizerType` is `wave`. */
  audioVisualizerWaveLineWidth?: number;
  /** Optional class name merged onto the outer `<section>` container. */
  className?: string;
}

export function AgentSessionView_01({
  preConnectMessage = '🌾 Connecting to Krishi Mitra... Please allow microphone access and start speaking.',
  supportsChatInput = true,
  supportsVideoInput = true,
  supportsScreenShare = true,
  isPreConnectBufferEnabled = true,

  audioVisualizerType,
  audioVisualizerColor,
  audioVisualizerColorShift,
  audioVisualizerBarCount,
  audioVisualizerGridRowCount,
  audioVisualizerGridColumnCount,
  audioVisualizerRadialBarCount,
  audioVisualizerRadialRadius,
  audioVisualizerWaveLineWidth,
  ref,
  className,
  ...props
}: React.ComponentProps<'section'> & AgentSessionView_01Props) {
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { state: agentState } = useAgent();

  const [callEnded, setCallEnded] = useState(false);
  const [micDenied, setMicDenied] = useState(false);
  const [connectionState, setConnectionState] = useState<  'ready' | 'connecting' | 'connected'>('ready');

  const getStatus = () => {
  if (callEnded)
    return {
      text: '🔴 Call Ended',
      color: 'bg-red-500',
    };

  if (connectionState === 'ready')
    return {
      text: '⚪ Ready',
      color: 'bg-gray-500',
    };

  if (connectionState === 'connecting')
    return {
      text: '🟡 Connecting...',
      color: 'bg-yellow-500',
    };

  const state = String(agentState).toLowerCase();

  if (state.includes('listen'))
    return {
      text: '🎤 Listening',
      color: 'bg-green-600',
    };

  if (state.includes('think'))
    return {
      text: '🤔 Thinking',
      color: 'bg-blue-600',
    };

  if (state.includes('speak'))
    return {
      text: '🗣️ Speaking',
      color: 'bg-orange-500',
    };

  return {
    text: '🟢 Connected',
    color: 'bg-green-700',
  };
};

const restartCall = () => {
  setCallEnded(false);
  setConnectionState('connecting');
  session.start();
};

  const controls: AgentControlBarControls = {
    leave: true,
    microphone: true,
    chat: supportsChatInput,
    camera: supportsVideoInput,
    screenShare: supportsScreenShare,
  };

  useEffect(() => {
  const lastMessage = messages.at(-1);
  const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

  if (scrollAreaRef.current && lastMessageIsLocal) {
    scrollAreaRef.current.scrollTop =
      scrollAreaRef.current.scrollHeight;
  }

  if (session.isConnected) {
    setConnectionState('connected');
    setCallEnded(false);
  }
}, [messages, session.isConnected]);

useEffect(() => {
  if (!session.isConnected && connectionState === 'connected') {
    setCallEnded(true);
  }
}, [session.isConnected]);


useEffect(() => {
  navigator.mediaDevices
    ?.getUserMedia({ audio: true })
    .then((stream) => {
      stream.getTracks().forEach((t) => t.stop());
      setMicDenied(false);
    })
    .catch(() => {
      setMicDenied(true);
    });
}, []);

  return (
    <section
  ref={ref}
  className={cn(
    'bg-background relative z-10 h-full w-full overflow-hidden',
    className
  )}
  {...props}
>

  {/* Agent Status */}
  <div className="absolute top-24 left-1/2 z-999 -translate-x-1/2">
    <div
      className={cn(
        "rounded-full px-6 py-2 text-white font-semibold shadow-lg",
        getStatus().color
      )}
    >
      {getStatus().text}
    </div>
  </div>

  {/* Microphone Permission */}
  {micDenied && (
    <div className="absolute top-24 left-1/2 z-50 w-[90%] max-w-xl -translate-x-1/2 rounded-xl border border-red-300 bg-red-50 p-4 text-center shadow-lg">

      <h3 className="font-bold text-red-700">
        🎤 Microphone Permission Required
      </h3>

      <p className="mt-2 text-sm text-red-600">
        Please allow microphone access and refresh the page.
      </p>

    </div>
  )}

  <Fade top className="absolute inset-x-4 top-0 z-10 h-40" />

  {/* transcript */}

      <div className="absolute top-0 bottom-[135px] flex w-full flex-col md:bottom-[170px]">
        <AnimatePresence>
          {chatOpen && (
            <motion.div
              {...CHAT_MOTION_PROPS}
              className="flex h-full w-full flex-col gap-4 space-y-3 transition-opacity duration-300 ease-out"
            >
              <AgentChatTranscript
                agentState={agentState}
                messages={messages}
                className="mx-auto w-full max-w-2xl [&_.is-user>div]:rounded-[22px] [&>div>div]:px-4 [&>div>div]:pt-40 md:[&>div>div]:px-6"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      {/* Tile layout */}
      <TileLayout
        chatOpen={chatOpen}
        audioVisualizerType={audioVisualizerType}
        audioVisualizerColor={audioVisualizerColor}
        audioVisualizerColorShift={audioVisualizerColorShift}
        audioVisualizerBarCount={audioVisualizerBarCount}
        audioVisualizerRadialBarCount={audioVisualizerRadialBarCount}
        audioVisualizerRadialRadius={audioVisualizerRadialRadius}
        audioVisualizerGridRowCount={audioVisualizerGridRowCount}
        audioVisualizerGridColumnCount={audioVisualizerGridColumnCount}
        audioVisualizerWaveLineWidth={audioVisualizerWaveLineWidth}
      />

      {callEnded && (
  <div className="absolute inset-0 z-40 flex flex-col items-center justify-center bg-white/90 backdrop-blur">

    <div className="text-6xl">📞</div>

    <h2 className="mt-4 text-3xl font-bold text-red-600">
      Call Ended
    </h2>

    <p className="mt-2 text-gray-600">
      Thank you for using Krishi Mitra.
    </p>

    <button
      onClick={restartCall}
      className="mt-6 rounded-xl bg-green-600 px-8 py-3 text-white hover:bg-green-700"
    >
      Start Again
    </button>

  </div>
)}
      {/* Bottom */}
      <motion.div
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="absolute inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {/* Pre-connect message */}
        {isPreConnectBufferEnabled && (
          <AnimatePresence>
            {messages.length === 0 && (
              <MotionMessage
                key="pre-connect-message"
                duration={2}
                aria-hidden={messages.length > 0}
                {...SHIMMER_MOTION_PROPS}
               className="pointer-events-none mx-auto block rounded-xl bg-green-50 px-6 py-4 text-center text-base font-semibold text-green-700 shadow-lg"
              >
                {preConnectMessage}
              </MotionMessage>
            )}
          </AnimatePresence>
        )}
        <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar
            variant="livekit"
            controls={controls}
            isChatOpen={chatOpen}
            isConnected={session.isConnected}
            onDisconnect={() => {  session.end();
            setCallEnded(true);
              }}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </motion.div>
    </section>
  );
}
