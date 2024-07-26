import azure.cognitiveservices.speech as speechsdk
from config import Config

speech_config = speechsdk.SpeechConfig(subscription=Config.SPEECH_KEY, region=Config.SPEECH_REGION)

def get_voice_input(audio_stream):
    import logging
    import os
    from logging.handlers import RotatingFileHandler

    log_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'logs')
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, 'voice_memory.log')

    logger = logging.getLogger('voice_memory')
    logger.setLevel(logging.DEBUG)

    print(f'Log directory: {log_directory}')
    print(f'Log file: {log_file}')
    print(f'Log directory: {log_directory}')
    print(f'Log file: {log_file}')
    if not os.path.exists(log_directory):
        print(f'Creating log directory: {log_directory}')
        os.makedirs(log_directory)
    if not os.path.exists(log_file):
        print(f'Creating log file: {log_file}')
        open(log_file, 'a').close()
    logger.info('Log directory: %s', log_directory)
    logger.info('Log file: %s', log_file)
    print(f'Logger setup complete. Log file: {log_file}')
    logger.info('Logger setup complete. Log file: %s', log_file)
    print(f'Logger setup complete. Log file: {log_file}')
    logger.info('Logger setup complete. Log file: %s', log_file)

    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        print('Adding file handler to logger')
        logger.addHandler(file_handler)
    else:
        print('Clearing existing handlers and adding file handler to logger')
        logger.handlers.clear()
        logger.addHandler(file_handler)

    print(f'Logger setup complete. Log file: {log_file}')
    logger.info('Logger setup complete. Log file: %s', log_file)
    
    print("Starting voice input processing for audio stream")
    logger.info("Starting voice input processing for audio stream")
    try:
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "es-ES", "fr-FR", "de-DE"])
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config
        )

        print("Initiating speech recognition")
        logger.info("Initiating speech recognition")
        result = speech_recognizer.recognize_once_async().get()
        print(f"Speech recognition result reason: {result.reason}")
        logger.info(f"Speech recognition result reason: {result.reason}")

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized text: {result.text}")
            logger.info(f"Recognized text: {result.text}")
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
            logger.warning("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech recognition canceled: {cancellation_details.reason}")
            logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
                logger.error(f"Error details: {cancellation_details.error_details}")
    except Exception as e:
        print(f"Exception during speech recognition: {str(e)}")
        logger.error(f"Exception during speech recognition: {str(e)}", exc_info=True)

    return None
