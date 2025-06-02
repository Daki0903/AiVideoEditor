import speech_recognition as sr

def generate_subtitles(audio_path, output_srt):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_path)

    with audio_file as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language='sr-RS')
    except Exception as e:
        text = "[Greška u prepoznavanju govora]"

    # Jednostavan .srt fajl sa celim tekstom kao jedna stavka
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("1\n00:00:00,000 --> 00:00:30,000\n")
        f.write(text)
