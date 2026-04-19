# PCat - Citrus Hack 2026
CitrusPet is an AI-powered desktop companion designed to combat the isolation of long study and coding sessions by providing a constant, supportive presence right on your taskbar. By blending personality with technology, this interactive buddy serves as a mental health advocate, offering real-time words of encouragement and positive affirmations to keep you motivated and reduce burnout. The pet feels truly alive by utilizing Google Gemini for intelligent, context-aware dialogue and ElevenLabs for realistic vocalization, all while moving naturally across your screen. It is more than just a desktop overlay; it is a dedicated online buddy that monitors your activity to ensure you never feel alone during your most intensive tasks

### Tech Stack:

* Language: Python 3.12
*  AI & Logic: Google Gemini (google-genai) for intelligent responses
*  Speech & Audio: ElevenLabs API for voice and Pygame for audio playback
  
*  GUI: PyQt6 for transparent, always-on-top window management
  
*  System Integration: pynput for activity sensing and win32gui for UI hooks
  
*  Environment: python-dotenv for API security and Scoop for dependency management

### Installation

To get CitrusPet running locally, follow these steps:
  1. Clone the Repository:

    git clone https://github.com/yourusername/CitrusPet.git
    cd CitrusPet

  2. Install Dependencies:

        Note: We recommend Python 3.12 for compatibility with Pygame wheels.

    pip install PyQt6 google-genai python-dotenv elevenlabs pygame pywin32 pynput

  3. Set Up Environment Variables:
     
    Create a .env file in the root directory and add your keys:
    GEMINI_API_KEY=your_key_here
    ELEVENLABS_API_KEY=your_key_here

  4. Run the App:

    python main.py

  
Sprites used: https://last-tick.itch.io/animated-pixel-kittens-cats-32x32 

Made with love by Andrew Li, Yilin Liu, and Jeffrey Xia
