from gtts import gTTS
import os
import uuid


LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn"
}


MESSAGES = {

    "SELL NOW": {
        "English": "Current market prices are favorable. It is a good time to sell your crop.",
        "Hindi": "वर्तमान बाजार मूल्य अच्छे हैं। अपनी फसल बेचने का यह अच्छा समय है।",
        "Kannada": "ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಉತ್ತಮವಾಗಿದೆ. ನಿಮ್ಮ ಬೆಳೆ ಮಾರಾಟ ಮಾಡಲು ಇದು ಒಳ್ಳೆಯ ಸಮಯ."
    },

    "HOLD STOCK": {
        "English": "Current market prices are low. Please hold your stock and wait for better prices.",
        "Hindi": "वर्तमान बाजार मूल्य कम हैं। कृपया अपनी फसल रोककर रखें और बेहतर कीमत का इंतजार करें।",
        "Kannada": "ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಕಡಿಮೆಯಾಗಿದೆ. ದಯವಿಟ್ಟು ಉತ್ತಮ ಬೆಲೆಗೆ ಕಾಯಿರಿ."
    },

    "WATCH MARKET": {
        "English": "Market prices are stable. Continue monitoring before selling.",
        "Hindi": "बाज़ार मूल्य स्थिर हैं। बेचने से पहले कुछ समय प्रतीक्षा करें।",
        "Kannada": "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಸ್ಥಿರವಾಗಿದೆ. ಮಾರಾಟ ಮಾಡುವ ಮೊದಲು ಸ್ವಲ್ಪ ಸಮಯ ಕಾಯಿರಿ."
    }

}


def generate_voice(recommendation, language):

    os.makedirs("audio", exist_ok=True)

    message = MESSAGES.get(
        recommendation,
        MESSAGES["HOLD STOCK"]
    )[language]

    lang = LANGUAGE_CODES[language]

    filename = f"audio/{uuid.uuid4()}.mp3"

    speech = gTTS(
        text=message,
        lang=lang,
        slow=False
    )

    speech.save(filename)

    return filename