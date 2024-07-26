import azure.cognitiveservices.speech as speechsdk
from config import Config

speech_config = speechsdk.SpeechConfig(subscription=Config.SPEECH_KEY, region=Config.SPEECH_REGION)

def get_voice_input(audio_stream):
    import logging
    logging.basicConfig(filename='voice_memory.log', level=logging.DEBUG)
    
    logging.info("Starting voice input processing for audio stream")
    try:
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "es-ES", "fr-FR", "de-DE"])
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config
        )

        logging.info("Initiating speech recognition")
        result = speech_recognizer.recognize_once_async().get()
        logging.info(f"Speech recognition result reason: {result.reason}")

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logging.info(f"Recognized text: {result.text}")
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logging.warning("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error(f"Speech recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"Error details: {cancellation_details.error_details}")
    except Exception as e:
        logging.error(f"Exception during speech recognition: {str(e)}", exc_info=True)

    return None
