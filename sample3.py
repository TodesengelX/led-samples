import asyncio
import threading
import tkinter as tk
from tkinter import ttk
import pyaudio
import queue
import sys
from google import genai

# --- Configuration ---
# REPLACE THIS WITH YOUR ACTUAL API KEY
API_KEY = "YOUR_GEMINI_API_KEY" 

# The experimental model that supports the Live API
MODEL_ID = "gemini-2.0-flash-exp"

# Audio settings (Gemini Live expects 16kHz input, 24kHz output)
INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHANNELS = 1
CHUNK_SIZE = 512

class AudioHandler:
    """
    Handles microphone input and speaker output using PyAudio.
    """
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.input_queue = asyncio.Queue()
        self.output_queue = queue.Queue()
        self.is_recording = False
        self.loop = None # Will be set by the async client

    def start_audio_streams(self):
        # Input Stream (Microphone)
        self.input_stream = self.p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=INPUT_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
            stream_callback=self._input_callback
        )
        
        # Output Stream (Speakers)
        self.output_stream = self.p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=OUTPUT_RATE,
            output=True,
            frames_per_buffer=CHUNK_SIZE
        )
        self.is_recording = True
        
        # Start a dedicated thread for non-blocking audio playback
        threading.Thread(target=self._play_output_loop, daemon=True).start()

    def _input_callback(self, in_data, frame_count, time_info, status):
        """
        Callback from PyAudio when new audio data is available from the mic.
        """
        if self.is_recording and self.loop:
            # Transfer data from the PyAudio thread to the asyncio loop safely
            try:
                self.loop.call_soon_threadsafe(self.input_queue.put_nowait, in_data)
            except Exception:
                pass # Event loop might be closing
        return (None, pyaudio.paContinue)

    def _play_output_loop(self):
        """
        Reads audio chunks from the output queue and writes them to the speaker stream.
        """
        while self.is_recording:
            try:
                # Get data with a short timeout to allow checking is_recording
                data = self.output_queue.get(timeout=0.1)
                self.output_stream.write(data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio playback error: {e}")

    def stop_streams(self):
        self.is_recording = False
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()

class GeminiLiveClient:
    """
    Manages the connection to the Gemini Live API.
    """
    def __init__(self, audio_handler, update_status_callback):
        self.client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1alpha'})
        self.audio = audio_handler
        self.update_status = update_status_callback
        self.stop_event = asyncio.Event()

    async def run(self):
        # Capture the running event loop so the audio callback can use it
        self.audio.loop = asyncio.get_running_loop()
        
        # Start Mic and Speaker
        self.audio.start_audio_streams()
        self.update_status("Connected", "green")
        
        # Configure the session for Audio capabilities
        config = {"response_modalities": ["AUDIO"]}
        
        try:
            async with self.client.aio.live.connect(model=MODEL_ID, config=config) as session:
                self.update_status("Listening...", "blue")
                
                # Run send and receive loops concurrently
                send_task = asyncio.create_task(self.send_audio(session))
                receive_task = asyncio.create_task(self.receive_audio(session))
                
                # Wait here until the stop button is pressed
                await self.stop_event.wait()
                
                # Cleanup tasks
                send_task.cancel()
                receive_task.cancel()

        except Exception as e:
            print(f"Connection error: {e}")
            self.update_status(f"Error: {str(e)[:30]}...", "red")
        finally:
            self.audio.stop_streams()

    async def send_audio(self, session):
        """
        Reads from input queue (mic) and sends to Gemini.
        """
        while not self.stop_event.is_set():
            try:
                audio_data = await self.audio.input_queue.get()
                await session.send(input={"data": audio_data, "mime_type": "audio/pcm"}, end_of_turn=False)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Send error: {e}")
                break

    async def receive_audio(self, session):
        """
        Receives audio chunks from Gemini and puts them in output queue (speaker).
        """
        while not self.stop_event.is_set():
            try:
                async for response in session.receive():
                    if response.server_content is not None:
                        model_turn = response.server_content.model_turn
                        if model_turn is not None:
                            for part in model_turn.parts:
                                if part.inline_data is not None:
                                    self.audio.output_queue.put(part.inline_data.data)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Receive error: {e}")
                break

class ChatApp:
    """
    Main Tkinter GUI Application.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Live Voice Chat")
        self.root.geometry("400x350")
        
        # --- UI Layout ---
        
        # Status Circle
        self.status_indicator = tk.Canvas(root, width=30, height=30, highlightthickness=0)
        self.status_indicator_circle = self.status_indicator.create_oval(5, 5, 25, 25, fill="gray")
        self.status_indicator.pack(pady=(30, 10))
        
        # Status Text
        self.status_label = ttk.Label(root, text="Ready to Connect", font=("Segoe UI", 12))
        self.status_label.pack(pady=5)

        # Instructions
        self.info_label = ttk.Label(root, text="Press Start to begin voice conversation", font=("Segoe UI", 9), foreground="gray")
        self.info_label.pack(pady=5)
        
        # Buttons Frame
        self.btn_frame = ttk.Frame(root)
        self.btn_frame.pack(pady=30)
        
        self.start_btn = ttk.Button(self.btn_frame, text="Start Chat", command=self.start_chat)
        self.start_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)
        
        self.stop_btn = ttk.Button(self.btn_frame, text="End Chat", command=self.stop_chat, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)

        # Asyncio Thread Handling
        self.loop = None
        self.thread = None
        self.client = None

        # Clean shutdown on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_status(self, text, color):
        """Updates the GUI from a background thread."""
        self.root.after(0, lambda: self._update_ui(text, color))

    def _update_ui(self, text, color):
        self.status_label.config(text=text)
        self.status_indicator.itemconfig(self.status_indicator_circle, fill=color)

    def start_chat(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.update_status("Connecting...", "orange")
        
        # Run asyncio in a separate thread so GUI doesn't freeze
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

    def stop_chat(self):
        if self.client:
            # Signal the async loop to stop
            self.loop.call_soon_threadsafe(self.client.stop_event.set)
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("Disconnected", "gray")

    def _run_async_loop(self):
        """Target function for the background thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        audio_handler = AudioHandler()
        self.client = GeminiLiveClient(audio_handler, self.update_status)
        
        self.loop.run_until_complete(self.client.run())
        self.loop.close()

    def on_close(self):
        self.stop_chat()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    # Simple style configuration
    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 10))
    
    app = ChatApp(root)
    root.mainloop()