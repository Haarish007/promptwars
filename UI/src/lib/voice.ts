/**
 * Anchor — Voice STT/TTS Wrapper (Web Speech API).
 *
 * Provides a simple, unified interface for voice-first crisis & check-in paths.
 * Gracefully falls back if Web Speech API is not supported in browser.
 */

export interface SpeechToTextOptions {
  onResult: (transcript: string) => void;
  onError?: (err: any) => void;
  onEnd?: () => void;
}

export class VoiceController {
  private recognition: any = null;
  private synth: SpeechSynthesis | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
      }
      if ('speechSynthesis' in window) {
        this.synth = window.speechSynthesis;
      }
    }
  }

  isSTTSupported(): boolean {
    return !!this.recognition;
  }

  isTTSSupported(): boolean {
    return !!this.synth;
  }

  startListening(options: SpeechToTextOptions): void {
    if (!this.recognition) {
      options.onError?.('STT not supported');
      return;
    }

    this.recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      options.onResult(transcript);
    };

    this.recognition.onerror = (err: any) => {
      options.onError?.(err);
    };

    this.recognition.onend = () => {
      options.onEnd?.();
    };

    this.recognition.start();
  }

  stopListening(): void {
    if (this.recognition) {
      this.recognition.stop();
    }
  }

  speak(text: string, onEnd?: () => void): void {
    if (!this.synth) return;

    this.synth.cancel(); // Stop any active speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; // Slightly slower, calm pace
    utterance.pitch = 1.0;
    if (onEnd) {
      utterance.onend = onEnd;
    }
    this.synth.speak(utterance);
  }

  stopSpeaking(): void {
    if (this.synth) {
      this.synth.cancel();
    }
  }
}

export const voice = new VoiceController();
